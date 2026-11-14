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

# 1. Dans msdyn_actual — chercher compte 89x
print("=== msdyn_actual: Transaction category commençant par 89 ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        msdyn_actual[Transaction category],
        msdyn_actual[Transaction Type],
        "Amount", SUM(msdyn_actual[Amount]),
        "Count", COUNTROWS(msdyn_actual)
    ),
    LEFT(msdyn_actual[Transaction category], 2) = "89"
)
ORDER BY [Amount] DESC
""")
if rows:
    for r in rows:
        try: amt = float(r[2])
        except: amt = 0
        print(f"  {r[0]:<20} {r[1]:<20} {amt:>12,.2f}  cnt={r[3]}")
else:
    print("  Aucun compte 89x dans msdyn_actual")

# 2. Dans GL_HEADER — chercher compte 899
print()
print("=== GL_HEADER: MainAccount commençant par 89 ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        GL_HEADER[MainAccount],
        GL_HEADER[AccountName],
        "Amount", SUM(GL_HEADER[AccountingCurrencyAmount]),
        "Count", COUNTROWS(GL_HEADER)
    ),
    LEFT(GL_HEADER[MainAccount], 2) = "89"
)
ORDER BY [Amount] DESC
""")
if rows:
    for r in rows:
        try: amt = float(r[2])
        except: amt = 0
        print(f"  {r[0]:<15} {r[1]:<35} {amt:>14,.2f}  cnt={r[3]}")
else:
    print("  Aucun compte 89x dans GL_HEADER")

# 3. Dans BOB_OUT — chercher compte 899
print()
print("=== BOB_OUT: MainAccount commençant par 89 ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        BOB_OUT[MainAccount],
        "Amount", SUM(BOB_OUT[AccountingCurrencyAmount]),
        "Count", COUNTROWS(BOB_OUT)
    ),
    LEFT(BOB_OUT[MainAccount], 2) = "89"
)
ORDER BY [Amount] DESC
""")
if rows:
    for r in rows:
        try: amt = float(r[1])
        except: amt = 0
        print(f"  {r[0]:<15} {amt:>14,.2f}  cnt={r[2]}")
else:
    print("  Aucun compte 89x dans BOB_OUT")

# 4. Tous les comptes GL_MainAccounts avec 89
print()
print("=== GL_MainAccounts: comptes 89x ===")
rows = dax("""
EVALUATE
FILTER(
    GL_MainAccounts,
    LEFT(GL_MainAccounts[MainAccountId], 2) = "89"
)
""")
if rows:
    for r in rows:
        print(f"  {r}")
else:
    print("  Aucun compte 89x dans GL_MainAccounts")

conn.Close()
