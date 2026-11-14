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

# Revenue_BOB : CustRevenue + ProjOnAccount + ProjTurnover
m = mt.Measures.Find('Revenue_BOB')
m.Expression = """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] IN {"CustRevenue", "ProjOnAccount", "ProjTurnover"}
)"""
print('Revenue_BOB mis a jour')

# Invoiced = CustRevenue uniquement (factures directes)
inv = mt.Measures.Find('Invoiced')
inv.Expression = """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] = "CustRevenue"
)"""
print('Invoiced mis a jour (CustRevenue uniquement)')

# Nouvelle mesure : Revenue_OnAccount
existing = mt.Measures.Find('Revenue_OnAccount')
if existing is None:
    from Microsoft.AnalysisServices.Tabular import Measure
    m2 = Measure()
    m2.Name = 'Revenue_OnAccount'
    m2.Expression = """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] IN {"ProjOnAccount", "ProjTurnover"}
)"""
    m2.FormatString = u'\u20ac #,##0'
    m2.DisplayFolder = 'Revenues'
    mt.Measures.Add(m2)
    print('Revenue_OnAccount cree')
else:
    existing.Expression = """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] IN {"ProjOnAccount", "ProjTurnover"}
)"""
    print('Revenue_OnAccount mis a jour')

model.SaveChanges()
print('\n=== OK ===')
print('Revenue_BOB = CustRevenue + ProjOnAccount + ProjTurnover')
print('Invoiced    = CustRevenue uniquement')
print('Revenue_OnAccount = ProjOnAccount + ProjTurnover')
srv.Disconnect()
