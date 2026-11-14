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

print("=== Milestones: Stat Nr + Milestone Name + Amount ===")
rows = dax("""
EVALUATE
TOPN(25,
    SELECTCOLUMNS(
        Milestones,
        "Stat Nr",      Milestones[Stat Nr],
        "Event",        Milestones[Milestone Name],
        "Planned",      Milestones[Line Amount],
        "Date",         Milestones[Milestone date],
        "Status",       Milestones[MilestoneStatus]
    ),
    [Planned], DESC
)
""")
print(f"  {'Stat Nr':<12} {'Event':<40} {'Planned':>12}  {'Date':<12}  Status")
for r in rows:
    try: amt = float(r[2]) if r[2] != 'None' else 0
    except: amt = 0
    d = r[3][:10] if r[3] != 'None' else ''
    print(f"  {r[0]:<12} {r[1][:38]:<40} {amt:>12,.0f}  {d:<12}  {r[4]}")

# Stat Nr avec Blank?
print()
blank_rows = dax("""
EVALUATE
ROW(
    "With Stat Nr", CALCULATE(COUNTROWS(Milestones), Milestones[Stat Nr] <> BLANK()),
    "Without Stat Nr", CALCULATE(COUNTROWS(Milestones), Milestones[Stat Nr] = BLANK())
)
""")
print(f"  With Stat Nr: {blank_rows[0][0]}")
print(f"  Without Stat Nr: {blank_rows[0][1]}")

conn.Close()
