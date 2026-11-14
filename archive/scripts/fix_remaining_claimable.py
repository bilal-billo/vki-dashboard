import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

srv = Server()
srv.Connect('localhost:56550')
model = srv.Databases[0].Model
mt = model.Tables.Find('_Measures')

def show(name):
    m = mt.Measures.Find(name)
    return m.Expression.strip()[:150] if m else 'INTROUVABLE'

print("AVANT:")
print(f"  [Remaining vs Claimable] = {show('Remaining vs Claimable')}")
print(f"  [Total Claimable]        = {show('Total Claimable')[:80]}...")

# Fix: Remaining vs Claimable = Budget - Total Claimable (avec coefficients)
m = mt.Measures.Find('Remaining vs Claimable')
if m:
    m.Expression = "[Total Budget] - [Total Claimable]"
    print('\nMAJ: [Remaining vs Claimable] = [Total Budget] - [Total Claimable]')
else:
    print('INTROUVABLE: Remaining vs Claimable')

model.SaveChanges()
print('SAUVEGARDE OK')

print("\nAPRES:")
print(f"  [Remaining vs Claimable] = {show('Remaining vs Claimable')}")

srv.Disconnect()
