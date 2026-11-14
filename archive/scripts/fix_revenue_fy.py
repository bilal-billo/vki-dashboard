import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

PORT = 64093

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

mt = model.Tables.Find('_Measures')

m = mt.Measures.Find('Revenue_FY_Current')
if m:
    m.Expression = """VAR _fy = YEAR(TODAY())
RETURN CALCULATE(
    [Revenue_BOB],
    FILTER(ALL('Dates'), 'Dates'[vKI Financial Year] = _fy)
)"""
    print('Revenue_FY_Current mis a jour')
else:
    print('ERREUR: mesure introuvable')

model.SaveChanges()
print('Sauvegarde OK')
srv.Disconnect()
