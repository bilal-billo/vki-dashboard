import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, SingleColumnRelationship, RelationshipEndCardinality, CrossFilteringBehavior
)

PORT = 64093

NEW_MQUERY = r"""let
    // GL complet F&O - toutes les ecritures
    Source = OData.Feed(
        "https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType",
        null, [Implementation="2.0"]
    ),

    // Extraire F&O Project ID depuis JSON ex: [{"MAINACCOUNT":"70400000","PROJECT":"P-001294-K"}]
    WithProject = Table.AddColumn(Source, "FOProjectId", each
        let js = [LedgerDimensionValuesJson]
        in if js = null or js = "" then null
           else try Json.Document(js){0}[PROJECT] otherwise null
    ),

    // AccountingDate depuis header GL
    Hdr = OData.Feed(
        "https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalEntryBiEntities?$select=GeneralJournalEntry,AccountingDate",
        null, [Implementation="2.0"]
    ),
    Joined   = Table.NestedJoin(WithProject, {"GeneralJournalEntry"}, Hdr, {"GeneralJournalEntry"}, "h", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Joined, "h", {"AccountingDate"}),

    Types = Table.TransformColumnTypes(Expanded, {
        {"AccountingCurrencyAmount", type number},
        {"AccountingDate", type date}
    })
in
    Types"""

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

# --- Verifier qu'on ne touche QUE BOB_P7 ---
tables = [t.Name for t in model.Tables]
print('Tables dans le modele: %s' % ', '.join(tables))

bob = model.Tables.Find('BOB_P7')
if bob is None:
    bob = model.Tables.Find('BOB_OUT')
    if bob is None:
        print('ERREUR: ni BOB_P7 ni BOB_OUT trouve')
        srv.Disconnect()
        sys.exit(1)
    else:
        print('BOB_OUT existe deja — mise a jour M query uniquement')
else:
    print('Renommage BOB_P7 -> BOB_OUT...')
    bob.Name = 'BOB_OUT'

# Mise a jour M query
for p in bob.Partitions:
    if hasattr(p.Source, 'Expression'):
        p.Source.Expression = NEW_MQUERY
        p.Name = 'BOB_OUT'
print('M query mise a jour OK')

# Ajouter colonne FOProjectId si absente (elle sera creee par la M query)
# Verifier si la colonne existe deja dans le schema
col_names = [c.Name for c in bob.Columns]
print('Colonnes actuelles: %s' % ', '.join(col_names))

# Relation AccountingDate -> Dates[Date]
rel_name = 'BOB_OUT_Date'
if model.Relationships.Find(rel_name) is None:
    dates_table = model.Tables.Find('Dates')
    date_col = dates_table.Columns.Find('Date') if dates_table else None
    bob_date_col = bob.Columns.Find('AccountingDate')
    if date_col and bob_date_col:
        rel = SingleColumnRelationship()
        rel.Name = rel_name
        rel.FromColumn = bob_date_col
        rel.ToColumn = date_col
        rel.FromCardinality = RelationshipEndCardinality.Many
        rel.ToCardinality = RelationshipEndCardinality.One
        rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
        rel.IsActive = True
        model.Relationships.Add(rel)
        print('Relation BOB_OUT[AccountingDate] -> Dates[Date] creee')
    else:
        print('Colonnes AccountingDate ou Date absentes - relation a creer apres refresh')
else:
    print('Relation date deja existante')

model.SaveChanges()
print('\n=== OK - uniquement BOB_P7/BOB_OUT modifie ===')
print('Prochaine etape: clic droit BOB_OUT -> Refresh dans PBI')
srv.Disconnect()
