import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model

# Supprimer VKI FY de Dates (colonne cassée, pas nécessaire)
dates_tbl = model.Tables.Find('Dates')
if dates_tbl:
    col = dates_tbl.Columns.Find('VKI FY')
    if col:
        dates_tbl.Columns.Remove(col)
        print("Supprimé Dates[VKI FY]")
    else:
        print("Dates[VKI FY] introuvable")

# Vérifier que les autres VKI FY sont OK
for tbl_name in ['GL_HEADER', 'msdyn_actual', 'Milestones']:
    tbl = model.Tables.Find(tbl_name)
    if tbl:
        col = tbl.Columns.Find('VKI FY')
        print(f"  [{tbl_name}][VKI FY]: {'OK' if col else 'ABSENT'}")

model.SaveChanges()
print("\nSauvegarde OK — Dates[VKI FY] supprimé")
print("\nPour les tableaux PBI:")
print("  Table 1 (Payments): utilise msdyn_actual[VKI FY]")
print("  Table 2 (Adv Pay):  utilise GL_HEADER[VKI FY]")
srv.Disconnect()
