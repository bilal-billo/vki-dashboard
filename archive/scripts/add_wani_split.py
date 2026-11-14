import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, Measure

PORT = 56550
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db    = srv.Databases[0]
model = db.Model
mt    = model.Tables.Find('_Measures')

def upsert(name, expr, fmt=u'\u20ac #,##0', folder='Revenues'):
    m = mt.Measures.Find(name)
    if m is None:
        m = Measure()
        m.Name = name
        mt.Measures.Add(m)
        action = 'CREE'
    else:
        action = 'MAJ'
    m.Expression   = expr
    m.FormatString = fmt
    m.DisplayFolder = folder
    print('  %s : [%s]' % (action, name))

print('--- Mesures WANI split ---')

# WANI New = debits sur compte 37 (montant positif = WIP booked)
upsert('WANI New D365', """CALCULATE(
    SUM(BOB_OUT[AccountingCurrencyAmount]),
    CONTAINSSTRING(BOB_OUT[LedgerDimensionValuesJson], "37000000"),
    BOB_OUT[AccountingCurrencyAmount] > 0
)""")

# WANI Cleared = credits sur compte 37 (montant negatif = WIP consomme)
upsert('WANI Cleared D365', """CALCULATE(
    SUM(BOB_OUT[AccountingCurrencyAmount]),
    CONTAINSSTRING(BOB_OUT[LedgerDimensionValuesJson], "37000000"),
    BOB_OUT[AccountingCurrencyAmount] < 0
)""")

# WANI Balance = cumul total jusqu'a la date max du contexte
upsert('WANI Balance D365', """CALCULATE(
    SUM(BOB_OUT[AccountingCurrencyAmount]),
    CONTAINSSTRING(BOB_OUT[LedgerDimensionValuesJson], "37000000"),
    FILTER(
        ALL(GL_HEADER),
        GL_HEADER[AccountingDate_Date] <= MAX(GL_HEADER[AccountingDate_Date])
    )
)""")

# Revenues per date = Invoiced + WANI net (deja = Project Revenues D365 mais renomme pour la table)
upsert('Revenues D365', """[Revenue Invoiced D365] + COALESCE([WANI New D365], 0) + COALESCE([WANI Cleared D365], 0)""")

model.SaveChanges()
print('\n=== SAUVEGARDE OK ===')

print('\nMesures Revenue dans _Measures:')
for m in mt.Measures:
    if 'D365' in m.Name or 'Revenue' in m.Name or 'WANI' in m.Name:
        print('  [%s]' % m.Name)

srv.Disconnect()
print('\nDone.')
