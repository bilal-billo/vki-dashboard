import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, MPartitionSource

PORT = 63175

NEW_MQUERY = '''let
    Source = OData.Feed("https://operations-vki-prod.crm4.dynamics.com/api/data/v9.2/vki_odoo_prod_datas", null, [Implementation="2.0"]),
    Cols = Table.SelectColumns(Source, {
        "vki_externalprimarykey", "vki_employee", "vki_date", "vki_project",
        "vki_hours", "vki_amount", "vki_analyticjournal", "vki_financialaccount",
        "vki_period", "vki_matricule", "vki_description", "vki_projectid"
    }),
    Normalized = Table.AddColumn(Cols, "StatNumber", each
        let
            code = Text.Start([vki_project], 8),
            fixed = if Text.Length(code) >= 3 and Text.At(code, 2) = "O"
                    then Text.Start(code, 2) & "R" & Text.Middle(code, 3)
                    else code
        in fixed
    ),
    Reclassified = Table.AddColumn(Normalized, "AnalyticalJournal", each
        if [vki_analyticjournal] = "UNASSIGNED" and [vki_employee] <> "0"
        then "T1 Manpower"
        else [vki_analyticjournal]
    ),
    Dropped = Table.RemoveColumns(Reclassified, {"vki_analyticjournal"}),
    Renamed = Table.RenameColumns(Dropped, {
        {"vki_externalprimarykey", "OdooID"},
        {"vki_employee",           "Employee"},
        {"vki_date",               "Date"},
        {"vki_project",            "ProjectLabel"},
        {"vki_hours",              "Hours"},
        {"vki_amount",             "Amount"},
        {"vki_financialaccount",   "FinancialAccount"},
        {"vki_period",             "Period"},
        {"vki_matricule",          "Matricule"},
        {"vki_description",        "Description"},
        {"vki_projectid",          "ProjectID"}
    }),
    Types = Table.TransformColumnTypes(Renamed, {
        {"Date", type date},
        {"Hours", type number},
        {"Amount", type number}
    })
in
    Types'''

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

table = model.Tables.Find('OdooData')
if table is None:
    print('ERROR: table OdooData not found')
    sys.exit(1)

print('Table OdooData trouvee — partitions:')
for p in table.Partitions:
    src = p.Source
    if src is not None and hasattr(src, 'Expression'):
        print('  Partition: {} — ancienne source (100 premiers chars):'.format(p.Name))
        print('  ' + src.Expression[:100])
        src.Expression = NEW_MQUERY
        print('  -> Mise a jour OK')
    else:
        print('  Partition: {} — type: {}'.format(p.Name, type(src)))

model.SaveChanges()
print('\nSauvegarde OK — refresh la table OdooData dans Power BI')
srv.Disconnect()
