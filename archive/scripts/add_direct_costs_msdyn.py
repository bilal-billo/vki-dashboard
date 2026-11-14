import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, CalculatedColumn, DataType, Measure,
    SingleColumnRelationship, CrossFilteringBehavior, RelationshipEndCardinality
)

srv = Server()
srv.Connect('localhost:56550')
model = srv.Databases[0].Model

act = model.Tables.Find('msdyn_actual')
proj = model.Tables.Find('Projects')
mt = model.Tables.Find('_Measures')

# --- 1. Colonne calculée ProjectStatNr dans msdyn_actual ---
existing = act.Columns.Find('ProjectStatNr')
if existing:
    act.Columns.Remove(existing)
    print("Colonne ProjectStatNr existante supprimée")

col = CalculatedColumn()
col.Name = 'ProjectStatNr'
col.DataType = DataType.String
col.Expression = """VAR _p   = msdyn_actual[Project]
VAR _sep = FIND(" - ", _p, 1, 0)
RETURN IF(_sep > 0, LEFT(_p, _sep - 1), BLANK())"""
col.IsHidden = True
act.Columns.Add(col)
print("Colonne calculée [msdyn_actual].[ProjectStatNr] créée")

model.SaveChanges()
print("Sauvegarde 1 OK (colonne)")

# --- 2. Relation msdyn_actual[msdyn_project] → Projects[Project] (GUID unique) ---
rel_name = 'msdyn_actual_to_Projects'
for rel in model.Relationships:
    if rel.FromTable.Name == 'msdyn_actual' and rel.ToTable.Name == 'Projects':
        model.Relationships.Remove(rel)
        print("Ancienne relation msdyn_actual→Projects supprimée")
        break

rel = SingleColumnRelationship()
rel.Name = rel_name
rel.FromTable = act
rel.FromColumn = act.Columns.Find('msdyn_project')
rel.ToTable = proj
rel.ToColumn = proj.Columns.Find('Project')
rel.FromCardinality = RelationshipEndCardinality.Many
rel.ToCardinality = RelationshipEndCardinality.One
rel.IsActive = True
rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
model.Relationships.Add(rel)
print("Relation [msdyn_actual].[msdyn_project] → [Projects].[Project] (GUID) créée")

model.SaveChanges()
print("Sauvegarde 2 OK (relation)")

# --- 3. Mesures Direct Costs basées sur msdyn_actual ---
def upsert(name, expr, fmt=None):
    m = mt.Measures.Find(name)
    if not m:
        m = Measure()
        m.Name = name
        mt.Measures.Add(m)
    m.Expression = expr
    if fmt:
        m.FormatString = fmt
    print(f"  Mesure [{name}] OK")

# Direct Costs msdyn = Transaction Type = Cost uniquement
upsert('Direct Costs msdyn D365', """CALCULATE(
    SUM(msdyn_actual[Amount]),
    msdyn_actual[Transaction Type] = "Cost",
    FILTER(msdyn_actual, LEFT(msdyn_actual[Transaction category], 8) <> "48000000")
)""", '#,0.0')

# Coefficient OH par type de contrat
# EU=25%, FOD=15%, COM=25%, ESA=25% (à valider)
upsert('Direct Costs OH msdyn D365', """VAR _dc = [Direct Costs msdyn D365]
VAR _type = SELECTEDVALUE(Projects[ContractType], "")
VAR _coef = SWITCH(TRUE(),
    LEFT(_type, 2) = "EU", 0.25,
    _type = "FOD",          0.15,
    _type = "COM",          0.25,
    _type = "ESA",          0.25,
    0.20)
RETURN _dc * _coef""", '#,0.0')

upsert('Direct Costs + OH msdyn D365', """COALESCE([Direct Costs msdyn D365], 0)
+ COALESCE([Direct Costs OH msdyn D365], 0)""", '#,0.0')

# Par catégorie (code GL → expense type)
# T6 Travel = Meals, Hotel, Mileage, Metro/tram/bus/taxi, Parking
# T5 = codes GL 6xxxx (Other costs)
# T1 = OdooData seulement pour l'instant
upsert('DC Travel msdyn D365', """CALCULATE(
    SUM(msdyn_actual[Amount]),
    msdyn_actual[Transaction Type] = "Cost",
    msdyn_actual[Transaction category] IN {"Meals","Hotel","Mileage","Metro/tram/bus/taxi","Parking","Air ticket","Train ticket","Taxi"}
)""", '#,0.0')

upsert('DC Other msdyn D365', """CALCULATE(
    SUM(msdyn_actual[Amount]),
    msdyn_actual[Transaction Type] = "Cost",
    NOT msdyn_actual[Transaction category] IN {"Meals","Hotel","Mileage","Metro/tram/bus/taxi","Parking","Air ticket","Train ticket","Taxi"}
)""", '#,0.0')

model.SaveChanges()
print("\nSauvegarde 3 OK (mesures)")
print("\nMesures créées:")
print("  [Direct Costs msdyn D365]        = SUM(Amount) où TxType=Cost")
print("  [Direct Costs OH msdyn D365]     = DC × coef (EU=25%, FOD=15%...)")
print("  [Direct Costs + OH msdyn D365]   = DC + OH")
print("  [DC Travel msdyn D365]           = T6 (Meals/Hotel/Mileage...)")
print("  [DC Other msdyn D365]            = autres coûts (codes GL)")

srv.Disconnect()
