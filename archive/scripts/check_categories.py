import clr, sys
sys.path.append(r'C:\Program Files\Microsoft SQL Server Management Studio 21\Release\Common7\IDE')
clr.AddReference('Microsoft.AnalysisServices.AdomdClient')
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand
import System.Globalization as Glob
import System.Threading as Thr
Thr.Thread.CurrentThread.CurrentCulture = Glob.CultureInfo.GetCultureInfo('en-US')

conn = AdomdConnection('Data Source=localhost:49640;')
conn.Open()

def dax(q):
    cmd = AdomdCommand(q, conn)
    r = cmd.ExecuteReader()
    rows = []
    while r.Read():
        rows.append([str(r[i]) for i in range(r.FieldCount)])
    r.Close()
    return rows

print("=== Distribution par Milestone Category ===")
rows = dax("""
EVALUATE
SUMMARIZECOLUMNS(
    Milestones[Milestone Category],
    "Count", COUNTROWS(Milestones),
    "Planned Total", SUM(Milestones[Line Amount]),
    "Approved Total", CALCULATE(SUM(Milestones[Line Amount]), Milestones[MilestoneStatus] = "Posted")
)
ORDER BY [Planned Total] DESC
""")
print(f"  {'Category':<22} {'Count':>6}  {'Planned':>15}  {'Approved':>15}")
for r in rows:
    try: planned = float(r[1])
    except: planned = 0
    try: approved = float(r[2])
    except: approved = 0
    print(f"  {r[0]:<22} {planned:>6,.0f}  {planned:>15,.0f}  {approved:>15,.0f}")

print()
print("=== Payment Schedule sample (Advance + Interim + Final) ===")
rows = dax("""
EVALUATE
TOPN(20,
    SELECTCOLUMNS(
        FILTER(Milestones,
            Milestones[Milestone Category] = "Advance Payment" ||
            Milestones[Milestone Category] = "Interim Payment" ||
            Milestones[Milestone Category] = "Final Payment"
        ),
        "Stat Nr",   Milestones[Stat Nr],
        "Event",     Milestones[Milestone Name],
        "Category",  Milestones[Milestone Category],
        "Planned",   Milestones[Line Amount],
        "Status",    Milestones[MilestoneStatus]
    ),
    [Planned], DESC
)
""")
print(f"  {'Stat Nr':<12} {'Event':<35} {'Cat':<18} {'Planned':>12}  Status")
for r in rows:
    try: amt = float(r[3]) if r[3] != 'None' else 0
    except: amt = 0
    print(f"  {r[0]:<12} {r[1][:33]:<35} {r[2]:<18} {amt:>12,.0f}  {r[4]}")

conn.Close()
