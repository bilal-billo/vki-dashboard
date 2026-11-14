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

stat = "EAR 2529"

# 1. OdooData (heures T1/T3)
print(f"=== {stat} — OdooData (heures Odoo) ===")
rows = dax(f"""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        OdooData[AnalyticalJournal],
        OdooData[FinancialAccount],
        "Hours", SUM(OdooData[Hours]),
        "Amount", SUM(OdooData[Amount]),
        "Amount_OH", SUM(OdooData[Amount_OH])
    ),
    TREATAS({{"{stat}"}}, Projects[VKI Stat Number])
)
ORDER BY [Amount_OH] DESC
""")
if rows:
    print(f"  {'Journal':<15} {'FinancialAccount':<25} {'Hours':>8}  {'Amount':>12}  {'Amount_OH':>12}")
    for r in rows:
        try: h = float(r[2]); amt = float(r[3]); oh = float(r[4])
        except: h = amt = oh = 0
        print(f"  {r[0]:<15} {r[1][:23]:<25} {h:>8,.1f}  {amt:>12,.0f}  {oh:>12,.0f}")
else:
    print("  Aucune donnée OdooData")

# 2. BOB_OUT (GL Finance lié au projet)
print()
print(f"=== {stat} — BOB_OUT (GL Finance par compte) ===")
rows = dax(f"""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        BOB_OUT[MainAccount],
        BOB_OUT[PostingType],
        "Amount", SUM(BOB_OUT[AccountingCurrencyAmount]),
        "Count", COUNTROWS(BOB_OUT)
    ),
    TREATAS({{"{stat}"}}, Projects[VKI Stat Number])
)
ORDER BY [Amount] DESC
""")
if rows:
    print(f"  {'MainAccount':<15} {'PostingType':<30} {'Amount':>14}  Count")
    for r in rows:
        try: amt = float(r[2])
        except: amt = 0
        print(f"  {r[0]:<15} {r[1][:28]:<30} {amt:>14,.2f}  {r[3]}")
else:
    print("  Aucune donnée BOB_OUT")

# 3. msdyn_actual TOUS types (pas seulement Cost)
print()
print(f"=== {stat} — msdyn_actual TOUS Transaction Types ===")
rows = dax(f"""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        msdyn_actual[Transaction Type],
        "Amount", SUM(msdyn_actual[Amount]),
        "Count", COUNTROWS(msdyn_actual)
    ),
    TREATAS({{"{stat}"}}, Projects[VKI Stat Number])
)
ORDER BY [Amount] DESC
""")
for r in rows:
    try: amt = float(r[1])
    except: amt = 0
    print(f"  {r[0]:<35} {amt:>14,.2f}  cnt={r[2]}")

conn.Close()
