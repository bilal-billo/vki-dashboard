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

# M query: CustRevenue (BOB_OUT) depuis F&O
# Web.Contents au lieu de OData.Feed pour eviter que PBI modifie le filtre enum
BOB_OUT_MQUERY = r"""let
    // 8 pages avec URLs 100% statiques + options inline -> PBI evalue en parallele
    P0 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=0",     null, [Implementation="2.0"]),
    P1 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=5000",  null, [Implementation="2.0"]),
    P2 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=10000", null, [Implementation="2.0"]),
    P3 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=15000", null, [Implementation="2.0"]),
    P4 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=20000", null, [Implementation="2.0"]),
    P5 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=25000", null, [Implementation="2.0"]),
    P6 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=30000", null, [Implementation="2.0"]),
    P7 = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalAccountEntryBiEntities?$select=GeneralJournalEntry,AccountingCurrencyAmount,LedgerDimensionValuesJson,Text,PostingType&$top=5000&$skip=35000", null, [Implementation="2.0"]),
    All    = Table.Combine({P0,P1,P2,P3,P4,P5,P6,P7}),
    BobRaw = Table.SelectRows(All, each [PostingType] = "CustRevenue"),

    // Extraire code projet P-xxx depuis JSON dimension
    WithProject = Table.AddColumn(BobRaw, "FOProjectId", each
        let js     = [LedgerDimensionValuesJson],
            parsed = if js = null or js = "" then {} else try Json.Document(js) otherwise {},
            vals   = List.RemoveNulls(List.Transform(parsed, each try _[PROJECT] otherwise null))
        in if List.IsEmpty(vals) then null else List.First(vals)
    ),

    // Mapping P-numero -> StatNumber via ProjectsV2
    ProjRaw      = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/ProjectsV2?$top=500&$select=ProjectId,ProjectName", null, [Implementation="2.0"]),
    ProjWithStat = Table.AddColumn(ProjRaw, "StatNumber", each
        let parts = Text.Split(if [ProjectName] = null then "" else [ProjectName], " - ")
        in if List.Count(parts) >= 2 then Text.Trim(parts{0}) else null
    ),
    ProjMap  = Table.SelectColumns(ProjWithStat, {"ProjectId","StatNumber"}),
    J1       = Table.NestedJoin(WithProject, {"FOProjectId"}, ProjMap, {"ProjectId"}, "pm", JoinKind.LeftOuter),
    WithStat = Table.ExpandTableColumn(J1, "pm", {"StatNumber"}, {"StatNumber"}),

    // Dates depuis header GL (go-live sept 2025)
    HdrRaw   = OData.Feed("https://vki-prod.operations.eu.dynamics.com/data/GeneralJournalEntryBiEntities?$top=5000&$select=GeneralJournalEntry,AccountingDate&$filter=AccountingDate ge 2025-09-01T00:00:00Z", null, [Implementation="2.0"]),
    HdrDates = Table.SelectColumns(HdrRaw, {"GeneralJournalEntry","AccountingDate"}),
    J2       = Table.NestedJoin(WithStat, {"GeneralJournalEntry"}, HdrDates, {"GeneralJournalEntry"}, "hd", JoinKind.LeftOuter),
    WithDate = Table.ExpandTableColumn(J2, "hd", {"AccountingDate"}, {"AccountingDate"}),

    Selected = Table.SelectColumns(WithDate,
                   {"GeneralJournalEntry","AccountingCurrencyAmount","FOProjectId","StatNumber","Text","AccountingDate"}),
    Renamed  = Table.RenameColumns(Selected, {
                   {"GeneralJournalEntry","EntryKey"},{"AccountingCurrencyAmount","Amount"},{"Text","Description"}}),
    Types    = Table.TransformColumnTypes(Renamed, {{"Amount", type number},{"AccountingDate", type date}})
in
    Types"""

# M query: table WANI vide (placeholder)
WANI_MQUERY = r"""let
    // WANI = variation travaux en cours (compte 711)
    // ABSENT de D365 F&O au 2026-07-23 — saisie manuelle Finance dans ancien systeme BOB
    // TODO: demander a Peter comment encoder le WANI dans le nouveau systeme
    Source = #table(
        type table [
            EntryKey = text,
            Amount   = number,
            StatNumber = text,
            AccountingDate = date,
            Description = text
        ],
        {}
    )
in
    Source"""

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

# ---- Ajouter table BOB_OUT ----
existing = model.Tables.Find('BOB_OUT')
if existing is not None:
    print('Table BOB_OUT existe deja — mise a jour M query...')
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

# ---- Ajouter table WANI (placeholder) ----
existing_wani = model.Tables.Find('WANI')
if existing_wani is not None:
    print('Table WANI existe deja — skip')
else:
    print('Creation table WANI (placeholder)...')
    tw = Table()
    tw.Name = 'WANI'

    wani_cols = [
        ('EntryKey',       DataType.String),
        ('Amount',         DataType.Double),
        ('StatNumber',     DataType.String),
        ('AccountingDate', DataType.DateTime),
        ('Description',    DataType.String),
    ]
    for col_name, col_type in wani_cols:
        c = DataColumn()
        c.Name = col_name
        c.DataType = col_type
        tw.Columns.Add(c)

    pw = Partition()
    pw.Name = 'WANI'
    srcw = MPartitionSource()
    srcw.Expression = WANI_MQUERY
    pw.Source = srcw
    tw.Partitions.Add(pw)

    model.Tables.Add(tw)
    print('  Table WANI creee OK')

# NOTE: Relations BOB_OUT/WANI -> Projects[VKI Stat Number] non creees via script
# (doublons dans VKI Stat Number bloquent SaveChanges via TOM)
# A creer manuellement dans PBI Desktop : Many-to-Many, OneDirection, comme OdooData
print('NOTE: relations Projects a creer manuellement dans PBI Desktop (voir instructions)')

# ---- Relation BOB_OUT[AccountingDate] -> Dates[Date] ----
rel_date_name = 'BOB_OUT_AccountingDate_to_Dates'
existing_rel_date = model.Relationships.Find(rel_date_name)
if existing_rel_date is not None:
    print('Relation date %s existe deja — skip' % rel_date_name)
else:
    print('Creation relation BOB_OUT[AccountingDate] -> Dates[Date]...')
    reld = SingleColumnRelationship()
    reld.Name = rel_date_name
    bob_table2 = model.Tables.Find('BOB_OUT')
    dates_table = model.Tables.Find('Dates')
    reld.FromColumn = bob_table2.Columns.Find('AccountingDate')
    reld.ToColumn = dates_table.Columns.Find('Date')
    reld.FromCardinality = RelationshipEndCardinality.Many
    reld.ToCardinality = RelationshipEndCardinality.One
    reld.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
    reld.IsActive = True
    model.Relationships.Add(reld)
    print('  Relation BOB_OUT -> Dates OK')

# ---- Mesures Revenue dans _Measures ----
measures_table = model.Tables.Find('_Measures')

MEASURES = [
    (
        'Revenue_BOB_OUT',
        '// BOB_OUT = revenus factures (compte 70400000 F&O, equivalent ancien 70001)\n// Montants negatifs dans F&O = credit compte revenus\nIF(\n    ISFILTERED(Projects[VKI Stat Number]) || ISFILTERED(Dates[Year]),\n    -CALCULATE(SUM(BOB_OUT[Amount])),\n    -SUM(BOB_OUT[Amount])\n)',
        '#,##0 EUR',
        'Revenues'
    ),
    (
        'Revenue_WANI',
        '// WANI = variation travaux en cours (compte 711)\n// ABSENT de D365 au 2026-07-23 — a demander a Peter\n// La table WANI est un placeholder vide pour l instant\n-SUM(WANI[Amount])',
        '#,##0 EUR',
        'Revenues'
    ),
    (
        'Revenue_Total',
        '// Revenue Total = BOB_OUT facture + WANI (travaux en cours)\n[Revenue_BOB_OUT] + [Revenue_WANI]',
        '#,##0 EUR',
        'Revenues'
    ),
]

for m_name, m_expr, m_fmt, m_folder in MEASURES:
    existing_m = measures_table.Measures.Find(m_name)
    if existing_m is not None:
        print('Mesure %s existe deja — mise a jour...' % m_name)
        existing_m.Expression = m_expr
        existing_m.FormatString = m_fmt
        existing_m.DisplayFolder = m_folder
    else:
        print('Creation mesure %s...' % m_name)
        m = Measure()
        m.Name = m_name
        m.Expression = m_expr
        m.FormatString = m_fmt
        m.DisplayFolder = m_folder
        measures_table.Measures.Add(m)
        print('  OK')

model.SaveChanges()
print('\n=== Sauvegarde OK ===')
print('Prochaines etapes dans Power BI:')
print('  1. Clic droit BOB_OUT -> Refresh')
print('  2. Clic droit WANI -> Refresh')
print('  3. Creer la page Revenue dans PBI')
srv.Disconnect()
