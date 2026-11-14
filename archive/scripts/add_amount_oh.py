import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()

from Microsoft.AnalysisServices.Tabular import Server, CalculatedColumn, DataType

PORT = 63175

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

table = model.Tables.Find('OdooData')
if table is None:
    print('ERROR: table OdooData not found')
    sys.exit(1)

# Check if already exists
existing = table.Columns.Find('Amount_OH')
if existing is not None:
    print('Column Amount_OH already exists — skipping')
else:
    col = CalculatedColumn()
    col.Name = 'Amount_OH'
    col.DataType = DataType.Double
    col.Expression = """
OdooData[Amount] *
SWITCH(TRUE(),
    OdooData[AnalyticalJournal] = "T1 Manpower", 1.55,
    LEFT(OdooData[AnalyticalJournal], 2) = "T3", 1.55,
    1
)
"""
    table.Columns.Add(col)
    model.SaveChanges()
    print('OK — colonne Amount_OH ajoutee dans OdooData')

srv.Disconnect()
