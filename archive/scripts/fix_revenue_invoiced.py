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

def upd(name, expr):
    m = mt.Measures.Find(name)
    if m:
        m.Expression = expr
        print('MAJ: [%s]' % name)
    else:
        print('INTROUVABLE: [%s]' % name)

# Revenue Invoiced = CustRevenue + ProjOnAccount SEULEMENT (pas ProjTurnover)
upd('Revenue Invoiced D365', """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] IN {"CustRevenue", "ProjOnAccount"}
)""")

# Revenues D365 (tableau) = idem
upd('Revenues D365', """
VAR _inv  = COALESCE([Revenue Invoiced D365], 0)
VAR _wNew = COALESCE([WANI New D365], 0)
VAR _wClr = COALESCE([WANI Cleared D365], 0)
RETURN _inv + _wNew + _wClr""")

model.SaveChanges()
print('SAUVEGARDE OK')
srv.Disconnect()
