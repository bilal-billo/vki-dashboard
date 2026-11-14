import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

srv = Server()
srv.Connect('localhost:64093')
db = srv.Databases[0]
model = db.Model
t = model.Tables.Find('msdyn_actual')
if t:
    model.Tables.Remove(t)
    model.SaveChanges()
    print('msdyn_actual supprime')
else:
    print('pas trouve')
srv.Disconnect()
