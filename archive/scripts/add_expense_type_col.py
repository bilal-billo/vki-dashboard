import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, CalculatedColumn, DataType

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model
act = model.Tables.Find('msdyn_actual')

# Supprimer si existe
for name in ['Expense Type D365']:
    old = act.Columns.Find(name)
    if old:
        act.Columns.Remove(old)
        print(f"Ancienne colonne [{name}] supprimÃ©e")

# Colonne Expense Type D365
# T6 Travel = catÃ©gories transport/repas/hÃ©bergement
# T5 Material = codes GL (6xxxxx numÃ©rique)
# T4 Subcontracting = Ã  confirmer
# T1/T3 Manpower = OdooData (pas dans msdyn_actual)
col = CalculatedColumn()
col.Name = 'Expense Type D365'
col.DataType = DataType.String
col.Expression = """VAR _cat = msdyn_actual[Transaction category]
VAR _travel_names = {
    "Meals", "Hotel", "Mileage", "Metro/tram/bus/taxi", "Parking",
    "Air ticket", "Train ticket", "Taxi", "Ferry", "Car rental", "Fuel",
    "Flight", "Train", "Renting car short term", "Conference registrations"
}
VAR _travel_gl = {
    "61460000", "61511000", "61511010", "61511020", "61511030", "61620000"
}
VAR _manpower_gl = {
    "45300000", "45400000", "45400010", "45410000", "45900000", "49900030",
    "61700000", "62301000", "62301700", "62302000", "62302010", "62302020"
}
VAR _subcont_gl   = { "61800000", "61900000" }
VAR _amort_gl     = { "63021000", "63021020", "63021050" }
VAR _amort_ict_gl = { "63021010" }
VAR _other_gl     = { "74000090" }
VAR _exclu_gl     = { "48000000" }
RETURN
SWITCH(TRUE(),
    msdyn_actual[Transaction Type] <> "Cost",          BLANK(),
    msdyn_actual[VKI Task Type] = "Billing Milestone", BLANK(),
    _cat IN _exclu_gl,                                 BLANK(),
    _cat IN _travel_names,                             "T6 Travel",
    _cat IN _travel_gl,                                "T6 Travel",
    _cat IN _manpower_gl,                              "T1/T3 Manpower",
    _cat IN _subcont_gl,                               "T5 Subcontractors",
    _cat IN _amort_ict_gl,                             "T4 Amortization ICT",
    _cat IN _amort_gl,                                 "T4 Amortization",
    _cat IN _other_gl,                                 "Other",
    LEFT(_cat, 1) = "6",                               "T5 Material Purch.",
    "DC Unassigned"
)"""
act.Columns.Add(col)
print("Colonne [Expense Type D365] crÃ©Ã©e dans msdyn_actual")

model.SaveChanges()
print("Sauvegarde OK")
print()
print("Dans PBI â€” Cost Breakdown bar chart:")
print("  Y-axis:  msdyn_actual[Expense Type D365]")
print("  X-axis:  _Measures[Direct Costs D365]")
print("  Tooltip: msdyn_actual[Bookable Resource] ou [Description]")

srv.Disconnect()

