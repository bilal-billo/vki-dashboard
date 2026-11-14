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

print("=== Top 10 projets par nombre de milestones ===")
rows = dax("""
EVALUATE
TOPN(10,
    SUMMARIZECOLUMNS(
        Projects[VKI Stat Number],
        Projects[Name],
        "NbMilestones", COUNTROWS(Milestones),
        "TotalPlanned", SUM(Milestones[Line Amount]),
        "NbPosted", CALCULATE(COUNTROWS(Milestones), Milestones[MilestoneStatus] = "Posted")
    ),
    [NbMilestones], DESC
)
""")
print(f"  {'Stat Nr':<12} {'Nb':>4} {'Posted':>6} {'Total Planned':>15}  Nom projet")
for r in rows:
    try: tot = float(r[3])
    except: tot = 0
    print(f"  {r[0]:<12} {r[2]:>4} {r[4]:>6} {tot:>15,.0f}  {r[1][:50]}")

conn.Close()
