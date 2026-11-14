import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, MPartitionSource

PORT = 60227

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

tables_to_check = ['Projects', 'Contracts', 'Milestones', 'OdooData', 'Invoices', 'Customers']

for tname in tables_to_check:
    t = model.Tables.Find(tname)
    if t is None:
        print('=== {} : NOT FOUND ==='.format(tname))
        continue
    print('=== {} ==='.format(tname))
    for p in t.Partitions:
        src = p.Source
        if src is not None and hasattr(src, 'Expression'):
            print(src.Expression[:600])
        else:
            print('  Source type: {}'.format(type(src)))
    print()

srv.Disconnect()
