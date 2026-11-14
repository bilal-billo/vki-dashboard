import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, Table, DataColumn, Partition, MPartitionSource,
    DataType, SingleColumnRelationship, RelationshipEndCardinality,
    CrossFilteringBehavior, Measure
)

PORT = 52533

BOB_OUT_MQUERY = r"""let
    // Meme connecteur que Projects, Invoices, Milestones, etc.
    Source = CommonDataService.Database("operations-vki-prod.crm4.dynamics.com"),

    // 1. Lignes GL BOB_OUT — PostingType 200000032 = CustRevenue (694 lignes)
    //    Filtre numerique simple -> query folding Dataverse, pas de probleme enum OData F&O
    AcctRaw  = Source{[Schema="dbo", Item="mserp_generaljournalaccountentrybientity"]}[Data],
    BobRaw   = Table.SelectRows(AcctRaw, each [mserp_postingtype] = 200000032),
    AcctCols = Table.SelectColumns(BobRaw, {
        "mserp_generaljournalentry_bigint",
        "mserp_accountingcurrencyamount",
        "mserp_ledgeraccount",
        "mserp_text"
    }),

    // 2. Extraire FOProjectId depuis ledgeraccount "70400000~P-001294-K~~"
    WithProject = Table.AddColumn(AcctCols, "FOProjectId", each
        let parts = Text.Split([mserp_ledgeraccount], "~")
        in if List.Count(parts) >= 2 then parts{1} else null
    ),

    // 3. Mapping FOProjectId -> StatNumber via msdyn_project (meme source Dataverse)
    ProjRaw  = Source{[Schema="dbo", Item="msdyn_project"]}[Data],
    ProjMap  = Table.SelectColumns(ProjRaw, {"msdyn_projectnumber", "craef_vkistatnumber"}),
    J1       = Table.NestedJoin(WithProject, {"FOProjectId"}, ProjMap, {"msdyn_projectnumber"}, "pm", JoinKind.LeftOuter),
    WithStat = Table.ExpandTableColumn(J1, "pm", {"craef_vkistatnumber"}, {"StatNumber"}),

    // 4. AccountingDate via header GL (jointure bigint: entry.generaljournalentry_bigint = header.sourcekey_bigint)
    HdrRaw   = Source{[Schema="dbo", Item="mserp_generaljournalentrybientity"]}[Data],
    HdrCols  = Table.SelectColumns(HdrRaw, {"mserp_sourcekey_bigint", "mserp_accountingdate"}),
    J2       = Table.NestedJoin(WithStat, {"mserp_generaljournalentry_bigint"}, HdrCols, {"mserp_sourcekey_bigint"}, "hd", JoinKind.LeftOuter),
    WithDate = Table.ExpandTableColumn(J2, "hd", {"mserp_accountingdate"}, {"AccountingDate"}),

    Selected = Table.SelectColumns(WithDate, {
        "mserp_generaljournalentry_bigint",
        "mserp_accountingcurrencyamount",
        "FOProjectId",
        "StatNumber",
        "mserp_text",
        "AccountingDate"
    }),
    Renamed  = Table.RenameColumns(Selected, {
        {"mserp_generaljournalentry_bigint", "EntryKey"},
        {"mserp_accountingcurrencyamount",   "Amount"},
        {"mserp_text",                        "Description"}
    }),
    Types    = Table.TransformColumnTypes(Renamed, {
        {"Amount", type number},
        {"AccountingDate", type date}
    })
in
    Types"""

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

# ---- Supprimer WANI si elle existe ----
existing_wani = model.Tables.Find('WANI')
if existing_wani is not None:
    print('Suppression table WANI...')
    model.Tables.Remove(existing_wani)
    print('  WANI supprimee OK')
else:
    print('Table WANI absente — rien a supprimer')

# ---- BOB_OUT : creer ou mettre a jour ----
existing = model.Tables.Find('BOB_OUT')
if existing is not None:
    print('Table BOB_OUT existe — mise a jour M query...')
    for p in existing.Partitions:
        if hasattr(p.Source, 'Expression'):
            p.Source.Expression = BOB_OUT_MQUERY
    print('  M query mise a jour OK')
else:
    print('Creation table BOB_OUT...')
    t = Table()
    t.Name = 'BOB_OUT'
    cols = [
        ('EntryKey',       DataType.String),
        ('Amount',         DataType.Double),
        ('FOProjectId',    DataType.String),
        ('StatNumber',     DataType.String),
        ('Description',    DataType.String),
        ('AccountingDate', DataType.DateTime),
    ]
    for col_name, col_type in cols:
        c = DataColumn()
        c.Name = col_name
        c.DataType = col_type
        t.Columns.Add(c)
    p = Partition()
    p.Name = 'BOB_OUT'
    src = MPartitionSource()
    src.Expression = BOB_OUT_MQUERY
    p.Source = src
    t.Partitions.Add(p)
    model.Tables.Add(t)
    print('  Table BOB_OUT creee OK')

# ---- Relation BOB_OUT[AccountingDate] -> Dates[Date] ----
rel_date_name = 'BOB_OUT_AccountingDate_to_Dates'
if model.Relationships.Find(rel_date_name) is None:
    print('Creation relation BOB_OUT[AccountingDate] -> Dates[Date]...')
    reld = SingleColumnRelationship()
    reld.Name = rel_date_name
    reld.FromColumn = model.Tables.Find('BOB_OUT').Columns.Find('AccountingDate')
    reld.ToColumn = model.Tables.Find('Dates').Columns.Find('Date')
    reld.FromCardinality = RelationshipEndCardinality.Many
    reld.ToCardinality = RelationshipEndCardinality.One
    reld.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
    reld.IsActive = True
    model.Relationships.Add(reld)
    print('  Relation OK')
else:
    print('Relation date deja existante — skip')

# ---- Mesures Revenue ----
measures_table = model.Tables.Find('_Measures')

MEASURES = [
    (
        'Revenue_BOB_OUT',
        '-SUM(BOB_OUT[Amount])',
        '#,##0 EUR',
        'Revenues'
    ),
    (
        'Revenue_WANI',
        '// WANI absent de D365 — a demander a Peter\n0',
        '#,##0 EUR',
        'Revenues'
    ),
    (
        'Revenue_Total',
        '[Revenue_BOB_OUT] + [Revenue_WANI]',
        '#,##0 EUR',
        'Revenues'
    ),
]

for m_name, m_expr, m_fmt, m_folder in MEASURES:
    existing_m = measures_table.Measures.Find(m_name)
    if existing_m is not None:
        existing_m.Expression = m_expr
        existing_m.FormatString = m_fmt
        existing_m.DisplayFolder = m_folder
        print('Mesure %s mise a jour' % m_name)
    else:
        m = Measure()
        m.Name = m_name
        m.Expression = m_expr
        m.FormatString = m_fmt
        m.DisplayFolder = m_folder
        measures_table.Measures.Add(m)
        print('Mesure %s creee' % m_name)

model.SaveChanges()
print('\n=== OK ===')
print('Prochaine etape: clic droit BOB_OUT dans PBI -> Refresh')
print('Attendre 2-3 minutes (8 pages OData en parallele)')
srv.Disconnect()
