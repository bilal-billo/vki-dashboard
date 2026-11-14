import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, Measure

srv = Server()
srv.Connect('localhost:56550')
model = srv.Databases[0].Model
mt = model.Tables.Find('_Measures')

def upsert(name, expr, fmt='#,0.0'):
    m = mt.Measures.Find(name)
    if not m:
        m = Measure()
        m.Name = name
        mt.Measures.Add(m)
    m.Expression = expr
    m.FormatString = fmt
    print(f"  [{name}] OK")

# 1. Direct Costs D365 = msdyn_actual coûts réels (TxType=Cost)
upsert('Direct Costs D365',
    '[Direct Costs msdyn D365]')

# 2. Direct Costs + VKI OH D365 = DC + overhead par type contrat
upsert('Direct Costs + VKI OH D365',
    '[Direct Costs + OH msdyn D365]')

# 3. Claimable Costs D365 = Total Claimable (OdooData avec coefficients)
# déjà dans Milestones table, on crée un alias dans _Measures
upsert('Claimable Costs D365',
    "CALCULATE([Total Claimable], ALL(Dates))")

model.SaveChanges()
print("\nSauvegarde OK")
print("\n3 KPI créés pour la page Direct Costs:")
print("  [Direct Costs D365]          → msdyn_actual TxType=Cost")
print("  [Direct Costs + VKI OH D365] → DC + OH (EU=25%, FOD=15%...)")
print("  [Claimable Costs D365]       → OdooData × coefficients (en attente données)")

srv.Disconnect()
