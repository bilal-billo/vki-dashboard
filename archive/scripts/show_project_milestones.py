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

for stat in ['EAR 2529', 'TUR 2609']:
    print(f"\n{'='*80}")
    print(f"=== {stat} milestones ===")
    rows = dax(f"""
EVALUATE
SELECTCOLUMNS(
    FILTER(Milestones,
        RELATED(Projects[VKI Stat Number]) = "{stat}"
    ),
    "Name",     Milestones[Milestone Name],
    "Amount",   Milestones[Line Amount],
    "Date",     Milestones[Milestone date],
    "Status",   Milestones[MilestoneStatus],
    "Category", Milestones[Milestone Category]
)
""")
    print(f"  {'Milestone Name':<55} {'Amount':>10}  {'Date':<12}  {'Status':<10}  Cat")
    for r in rows:
        try: amt = float(r[1]) if r[1] != 'None' else 0
        except: amt = 0
        d = r[2][:10] if r[2] != 'None' else ''
        print(f"  {r[0][:53]:<55} {amt:>10,.0f}  {d:<12}  {r[3]:<10}  {r[4]}")
    print(f"  Total: {len(rows)} milestones")

conn.Close()
