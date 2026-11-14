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

def find_measure(name):
    for tbl in model.Tables:
        m = tbl.Measures.Find(name)
        if m:
            return tbl, m
    return None, None

def show(name):
    _, m = find_measure(name)
    return m.Expression.strip()[:300] if m else 'INTROUVABLE'

print("AVANT:")
print(f"  [Remaining Budget vs Revenues Booked]\n    {show('Remaining Budget vs Revenues Booked')}\n")
print(f"  [Remaining Budget vs Claimable Costs]\n    {show('Remaining Budget vs Claimable Costs')}\n")

# Fix 1: Remaining Budget vs Revenues Booked
# Problème: ALL(Milestones[Milestone date]) ne lève pas le filtre relation Dates→Milestones
# Fix: ajouter REMOVEFILTERS(Dates) pour que MaxDate contrôle le cumul correctement
tbl, m = find_measure('Remaining Budget vs Revenues Booked')
if m:
    m.Expression = """VAR MaxDate = MAX(Dates[Date])
RETURN
[Total Budget] - CALCULATE(
    SUM(Milestones[Line Amount]),
    REMOVEFILTERS(Dates),
    Milestones[Milestone date] <= MaxDate,
    Milestones[msdyn_invoicestatus] = 192350003
)"""
    print("FIX: [Remaining Budget vs Revenues Booked] — ajout REMOVEFILTERS(Dates)")
else:
    print("INTROUVABLE: Remaining Budget vs Revenues Booked")

# Fix 2: Remaining Budget vs Claimable Costs — même bug
tbl2, m2 = find_measure('Remaining Budget vs Claimable Costs')
if m2:
    old = m2.Expression.strip()
    # Remplacer ALL(Milestones[Milestone date]) par REMOVEFILTERS(Dates) dans le CALCULATE
    # La formule utilise OdooData dates — on garde la logique mais fixe le filtre temps
    new_expr = """VAR MaxDate = MAX(Dates[Date])
RETURN
[Total Budget] - CALCULATE(
    SUMX(
        FILTER(OdooData, OdooData[Date] <= MaxDate),
        VAR ProjType = LOOKUPVALUE(Projects[ContractType], Projects[VKI Stat Number], OdooData[StatNumber])
        VAR Journal   = OdooData[AnalyticalJournal]
        VAR Coef = SWITCH(TRUE(),
            LEFT(ProjType,2) = "EU", SWITCH(TRUE(),
                Journal = "T1 Manpower",         1.25,
                Journal = "T4 Subcontracting",   1.25,
                Journal = "T5 Other Costs",       1.25,
                Journal = "T6 Travel",            1.25,
                1.0),
            ProjType = "FOD", SWITCH(TRUE(),
                Journal = "T1 Manpower",         1.15,
                Journal = "T4 Subcontracting",   1.15,
                Journal = "T5 Other Costs",       1.15,
                Journal = "T6 Travel",            1.15,
                1.0),
            1.0)
        RETURN IF(Journal <> "WANI" && Journal <> "Invoice",
            -1 * OdooData[Amount] * Coef, 0)
    ),
    REMOVEFILTERS(Dates)
)"""
    m2.Expression = new_expr
    print("FIX: [Remaining Budget vs Claimable Costs] — ajout REMOVEFILTERS(Dates) + cumul OdooData[Date]")
else:
    print("INTROUVABLE: Remaining Budget vs Claimable Costs")

model.SaveChanges()
print("\nSAUVEGARDE OK")
print("\nAPRES:")
print(f"  [Remaining Budget vs Revenues Booked]\n    {show('Remaining Budget vs Revenues Booked')}\n")
print(f"  [Remaining Budget vs Claimable Costs]\n    {show('Remaining Budget vs Claimable Costs')}\n")

srv.Disconnect()
