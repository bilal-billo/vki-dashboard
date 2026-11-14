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

def upsert_measure(name, expr):
    old = tbl.Measures.Find(name)
    if old:
        tbl.Measures.Remove(old)
        print(f"Supprimée [{name}]")
    m = Measure()
    m.Name = name
    m.Expression = expr
    tbl.Measures.Add(m)
    print(f"Créée   [{name}]")

# VKI OH = 55% sur T1/T3 uniquement (MAP_COST_EXCEL SQL logic)
upsert_measure('Direct Costs OH msdyn D365', """
SUMX(
    FILTER(
        msdyn_actual,
        msdyn_actual[Transaction Type] = "Cost"
        && msdyn_actual[Expense Type D365] = "T1/T3 Manpower"
    ),
    msdyn_actual[Amount] * 0.55
)
""")

# DC + VKI OH (inchangé — somme des deux)
upsert_measure('Direct Costs + OH msdyn D365', """
COALESCE([Direct Costs msdyn D365], 0)
+ COALESCE([Direct Costs OH msdyn D365], 0)
""")

model.SaveChanges()
print("Sauvegarde OK")
srv.Disconnect()
