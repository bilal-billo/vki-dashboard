import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

PORT = 56550
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
model = srv.Databases[0].Model
mt = model.Tables.Find('_Measures')

# Fix WANI Balance = cumul net jusqu'a la date max du contexte
m = mt.Measures.Find('WANI Balance D365')
m.Expression = """
VAR _maxDate = MAX(GL_HEADER[AccountingDate_Date])
RETURN
CALCULATE(
    SUM(BOB_OUT[AccountingCurrencyAmount]),
    CONTAINSSTRING(BOB_OUT[LedgerDimensionValuesJson], "37000000"),
    REMOVEFILTERS(GL_HEADER),
    REMOVEFILTERS(Dates),
    GL_HEADER[AccountingDate_Date] <= _maxDate
)"""
print('MAJ: WANI Balance D365')

# Fix Revenues D365 = inclure aussi les lignes negatives (WANI Cleared)
m2 = mt.Measures.Find('Revenues D365')
m2.Expression = """
VAR _inv    = COALESCE([Revenue Invoiced D365], 0)
VAR _wNew   = COALESCE([WANI New D365], 0)
VAR _wClr   = COALESCE([WANI Cleared D365], 0)
RETURN _inv + _wNew + _wClr"""
print('MAJ: Revenues D365')

model.SaveChanges()
print('SAUVEGARDE OK')
srv.Disconnect()
