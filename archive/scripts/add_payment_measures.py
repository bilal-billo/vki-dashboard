import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, Measure

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model
tbl = model.Tables.Find('_Measures')

def upsert_measure(name, expr, fmt=None):
    old = tbl.Measures.Find(name)
    if old:
        tbl.Measures.Remove(old)
        print(f"Supprimée [{name}]")
    m = Measure()
    m.Name = name
    m.Expression = expr
    if fmt:
        m.FormatString = fmt
    tbl.Measures.Add(m)
    print(f"Créée   [{name}]")

# 1. Payments In = Billed Sales dans msdyn_actual
upsert_measure('Payments In D365', """
CALCULATE(
    SUM(msdyn_actual[Amount]),
    msdyn_actual[Transaction Type] = "Billed Sales"
)
""", '"€"#,0.00')

# 2. Payments to Partners = GL 48000000
upsert_measure('Payments to Partners D365', """
CALCULATE(
    SUM(msdyn_actual[Amount]),
    msdyn_actual[Transaction category] = "48000000"
)
""", '"€"#,0.00')

# 3. Advanced Payments = BOB_OUT GL 46xxxxxx (via colonne MainAccount ajoutée en PQ)
upsert_measure('Advanced Payments D365', """
CALCULATE(
    SUM(BOB_OUT[AccountingCurrencyAmount]),
    LEFT(BOB_OUT[MainAccount], 2) = "46"
)
""", '"€"#,0.00')

model.SaveChanges()
print("\nSauvegarde OK")
srv.Disconnect()
