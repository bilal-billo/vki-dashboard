import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, DataType

PORT = 56550
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db    = srv.Databases[0]
model = db.Model
gl    = model.Tables.Find('GL_HEADER')

col = gl.Columns.Find('AccountingDate_Date')
if col:
    col.DataType = DataType.DateTime
    col.FormatString = 'yyyy-MM-dd'
    print('AccountingDate_Date -> FormatString: yyyy-MM-dd')
else:
    print('ERREUR: colonne introuvable')

model.SaveChanges()
print('SAUVEGARDE OK')
srv.Disconnect()
