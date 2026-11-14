import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, MPartitionSource

PORT = 60574  # Reference SQL model

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

tables_of_interest = [
    'BOB_OUT_70001',
    '711 WANI FY 2022',
    'Qry_T_Revenues_Actuals_ALL',
    'Qry_Hourly_Rates_Project_Actual',
    'PMT_Schedule',
    'Project_Key_Facts',
    'Budget',
    'Project Master Data',
    'Advanced Payments',
]

for tname in tables_of_interest:
    t = model.Tables.Find(tname)
    if t is None:
        print('=== {} : NOT FOUND ===\n'.format(tname))
        continue
    print('=== {} ==='.format(tname))
    for p in t.Partitions:
        src = p.Source
        if src and hasattr(src, 'Expression'):
            print(src.Expression)
    print()

srv.Disconnect()
