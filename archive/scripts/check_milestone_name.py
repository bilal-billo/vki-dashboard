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

print('=== Sample Milestones avec Milestone Name ===')
rows = dax("""
EVALUATE
TOPN(20,
    SELECTCOLUMNS(
        Milestones,
        "Name",     Milestones[Milestone Name],
        "LineAmt",  Milestones[Line Amount],
        "MilDate",  Milestones[Milestone date],
        "Status",   Milestones[MilestoneStatus],
        "Desc",     Milestones[Contract Line Description]
    ),
    [LineAmt], DESC
)
""")
print(f"  {'Name':<35} {'Amount':>12}  {'Date':<12}  {'Status':<12}  Desc")
for r in rows:
    try:
        amt = float(r[1]) if r[1] != 'None' else 0
    except:
        amt = 0
    d = r[2][:10] if r[2] != 'None' else ''
    print(f"  {r[0][:35]:<35} {amt:>12,.0f}  {d:<12}  {r[3]:<12}  {r[4][:40]}")

print()
count_rows = dax("EVALUATE ROW(\"n\", COUNTROWS(Milestones))")
print(f"Total rows: {count_rows[0][0]}")

# Check distinct names
print()
print("=== Distinct Milestone Names (top 30) ===")
names = dax("""
EVALUATE
TOPN(30,
    SUMMARIZECOLUMNS(
        Milestones[Milestone Name],
        "Cnt", COUNTROWS(Milestones),
        "Tot", SUM(Milestones[Line Amount])
    ),
    [Tot], DESC
)
""")
for r in names:
    try: amt = float(r[2])
    except: amt = 0
    print(f"  {r[0][:40]:<42} cnt={r[1]:>4}  {amt:>14,.0f}")

conn.Close()
