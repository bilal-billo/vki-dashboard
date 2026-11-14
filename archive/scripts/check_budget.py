import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()

from Microsoft.AnalysisServices.Tabular import Server
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

PORT = 60227

def dax(query):
    conn = AdomdConnection('Data Source=localhost:{}'.format(PORT))
    conn.Open()
    cmd = AdomdCommand(query, conn)
    reader = cmd.ExecuteReader()
    cols = [reader.GetName(i) for i in range(reader.FieldCount)]
    rows = []
    while reader.Read():
        row = {}
        for i, c in enumerate(cols):
            v = reader.GetValue(i)
            row[c] = str(v) if v is not None else 'BLANK'
        rows.append(row)
    reader.Close()
    conn.Close()
    return cols, rows

print('=== Budget page — valeurs pour EAR 2411 ===')
print()

# Core budget measures for EAR 2411
q = """
EVALUATE
ROW(
    "Total Budget",         CALCULATE([Total Budget],         Projects[VKI Stat Number] = "EAR 2411"),
    "Total Milestones Posted", CALCULATE([Total Milestones Posted], Projects[VKI Stat Number] = "EAR 2411"),
    "Total Milestones Amount", CALCULATE([Total Milestones Amount], Projects[VKI Stat Number] = "EAR 2411"),
    "Remaining Budget",     CALCULATE([Remaining Budget],     Projects[VKI Stat Number] = "EAR 2411"),
    "Total Claimable",      CALCULATE([Total Claimable],      Projects[VKI Stat Number] = "EAR 2411"),
    "Total Direct Costs OH",CALCULATE([Total Direct Costs OH],Projects[VKI Stat Number] = "EAR 2411"),
    "Total Invoiced",       CALCULATE([Total Invoiced],       Projects[VKI Stat Number] = "EAR 2411")
)
"""
cols, rows = dax(q)
for row in rows:
    for k, v in row.items():
        label = k.replace('[', '').replace(']', '')
        print('  {:35s} = {}'.format(label, v))

print()
print('=== Remaining Budget vs Revenues/Claimable ===')
q2 = """
EVALUATE
ROW(
    "Remaining vs Revenues Booked",  CALCULATE([Remaining Budget vs Revenues Booked],  Projects[VKI Stat Number] = "EAR 2411"),
    "Remaining vs Claimable Costs",  CALCULATE([Remaining Budget vs Claimable Costs],  Projects[VKI Stat Number] = "EAR 2411")
)
"""
try:
    cols2, rows2 = dax(q2)
    for row in rows2:
        for k, v in row.items():
            print('  {:40s} = {}'.format(k, v))
except Exception as e:
    print('  Mesures non trouvees:', e)

print()
print('=== Milestones EAR 2411 — statuts ===')
q3 = """
EVALUATE
SUMMARIZECOLUMNS(
    Milestones[msdyn_invoicestatus],
    Milestones[MilestoneStatus],
    CALCULATETABLE(Milestones, Projects[VKI Stat Number] = "EAR 2411"),
    "Count",  CALCULATE(COUNTROWS(Milestones), Projects[VKI Stat Number] = "EAR 2411"),
    "Amount", CALCULATE(SUM(Milestones[Line Amount]), Projects[VKI Stat Number] = "EAR 2411")
)
"""
cols3, rows3 = dax(q3)
for row in rows3:
    print('  Status {} ({}) — {} milestones — €{}'.format(
        row.get('Milestones[msdyn_invoicestatus]','?'),
        row.get('Milestones[MilestoneStatus]','?'),
        row.get('[Count]','?'),
        row.get('[Amount]','?')
    ))
