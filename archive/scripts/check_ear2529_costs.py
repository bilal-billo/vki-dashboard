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

print("=== EAR 2529 — msdyn_actual par Transaction Type ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        msdyn_actual[Transaction Type],
        msdyn_actual[Transaction category],
        "Amount", SUM(msdyn_actual[Amount]),
        "Count", COUNTROWS(msdyn_actual)
    ),
    TREATAS({"EAR 2529"}, Projects[VKI Stat Number])
)
ORDER BY [Amount] DESC
""")
print(f"  {'Transaction Type':<30} {'GL Account':<15} {'Amount':>12}  Count")
for r in rows:
    try: amt = float(r[2])
    except: amt = 0
    print(f"  {r[0]:<30} {r[1]:<15} {amt:>12,.2f}  {r[3]}")

print()
print("=== EAR 2529 — Toutes les lignes msdyn_actual avec date ===")
rows = dax("""
EVALUATE
SELECTCOLUMNS(
    CALCULATETABLE(
        msdyn_actual,
        TREATAS({"EAR 2529"}, Projects[VKI Stat Number])
    ),
    "TxType",   msdyn_actual[Transaction Type],
    "Category", msdyn_actual[Transaction category],
    "Amount",   msdyn_actual[Amount],
    "AccDate",  msdyn_actual[Accounting Date],
    "DocDate",  msdyn_actual[Document Date],
    "Desc",     msdyn_actual[Description]
)
""")
print(f"  {'Type':<25} {'GL':<12} {'Amount':>12}  {'AccDate':<12}  {'DocDate':<12}  Desc")
for r in rows:
    try: amt = float(r[2])
    except: amt = 0
    acc = r[3][:10] if r[3] != 'None' else ''
    doc = r[4][:10] if r[4] != 'None' else ''
    print(f"  {r[0][:23]:<25} {r[1]:<12} {amt:>12,.2f}  {acc:<12}  {doc:<12}  {r[5][:35]}")

conn.Close()
