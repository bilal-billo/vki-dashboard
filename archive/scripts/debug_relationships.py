import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

PORT = 63175

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

print('=== Relations du modèle ===')
for rel in model.Relationships:
    print('  {} [{}] -> {} [{}]  | CrossFilter: {} | Active: {}'.format(
        rel.FromTable.Name, rel.FromColumn.Name,
        rel.ToTable.Name, rel.ToColumn.Name,
        str(rel.CrossFilteringBehavior),
        rel.IsActive
    ))

srv.Disconnect()

print()

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

print('=== Milestones pour EAR 2411 (ALL context) ===')
_, r = dax("""
EVALUATE
CALCULATETABLE(
    ROW("MilestonePosted", CALCULATE(SUM(Milestones[Line Amount]), Milestones[msdyn_invoicestatus] = 192350003),
        "MilestoneTotal", SUM(Milestones[Line Amount]),
        "MilestoneCount", COUNTROWS(Milestones)
    ),
    FILTER(ALL(Milestones), SEARCH("2411", Milestones[Project Contract Line Milestone], 1, 0) > 0)
)""")
for row in r:
    for k,v in row.items(): print('  {} = {}'.format(k.strip('[]').strip(), v))

print()
print('=== Milestones statuses ===')
_, r2 = dax("""
EVALUATE
SUMMARIZECOLUMNS(
    Milestones[MilestoneStatus],
    Milestones[msdyn_invoicestatus],
    "N", COUNTROWS(Milestones),
    "Sum", SUM(Milestones[Line Amount])
)""")
for row in r2:
    print('  Status={} ({}) -> {} rows, €{}'.format(
        row.get('Milestones[MilestoneStatus]','?'),
        row.get('Milestones[msdyn_invoicestatus]','?'),
        row.get('[N]','?'),
        row.get('[Sum]','?')
    ))
