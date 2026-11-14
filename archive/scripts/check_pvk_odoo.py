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

# 1. Tous les journaux analytiques dans OdooData
print("=== OdooData: TOUS les AnalyticalJournal distincts ===")
rows = dax("""
EVALUATE
SUMMARIZECOLUMNS(
    OdooData[AnalyticalJournal],
    "Amount", SUM(OdooData[Amount]),
    "Amount_OH", SUM(OdooData[Amount_OH]),
    "Hours", SUM(OdooData[Hours]),
    "Cnt", COUNTROWS(OdooData)
)
ORDER BY [Amount_OH] DESC
""")
print(f"  {'Journal':<15} {'Amount':>14}  {'Amount_OH':>14}  {'Hours':>10}  Cnt")
for r in rows:
    try: amt = float(r[1]); oh = float(r[2]); h = float(r[3])
    except: amt = oh = h = 0
    print(f"  {r[0]:<15} {amt:>14,.0f}  {oh:>14,.0f}  {h:>10,.1f}  {r[4]}")

# 2. OdooData EAR 2529
print()
print("=== OdooData EAR 2529 (par journal) ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        OdooData[AnalyticalJournal],
        OdooData[FinancialAccount],
        "Amount", SUM(OdooData[Amount]),
        "Amount_OH", SUM(OdooData[Amount_OH]),
        "Hours", SUM(OdooData[Hours]),
        "Cnt", COUNTROWS(OdooData)
    ),
    TREATAS({"EAR 2529"}, Projects[VKI Stat Number])
)
""")
if rows:
    for r in rows:
        try: amt = float(r[2]); oh = float(r[3]); h = float(r[4])
        except: amt = oh = h = 0
        print(f"  {r[0]:<15} {r[1]:<20} {amt:>12,.0f}  OH={oh:>12,.0f}  H={h:>8,.1f}  cnt={r[5]}")
else:
    print("  Aucune donnée OdooData pour EAR 2529")

# 3. msdyn_actual — transaction categories distinctes pour EAR 2529
print()
print("=== msdyn_actual: Transaction categories EAR 2529 (toutes) ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        msdyn_actual[Transaction Type],
        msdyn_actual[Transaction category],
        "Amount", SUM(msdyn_actual[Amount]),
        "Cnt", COUNTROWS(msdyn_actual)
    ),
    TREATAS({"EAR 2529"}, Projects[VKI Stat Number])
)
ORDER BY [Amount] DESC
""")
print(f"  {'Type':<25} {'Category':<25} {'Amount':>12}  Cnt")
for r in rows:
    try: amt = float(r[2])
    except: amt = 0
    print(f"  {r[0]:<25} {r[1]:<25} {amt:>12,.2f}  {r[3]}")

conn.Close()
