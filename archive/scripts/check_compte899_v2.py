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

# 1. BOB_OUT — comptes 89x (GL_HEADER lié via BOB_OUT)
print("=== BOB_OUT: MainAccount 89x (avec date GL_HEADER) ===")
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
        print(f"  Compte {r[0]:<15} {amt:>14,.2f}  cnt={r[2]}")
else:
    print("  Aucun compte 89x dans BOB_OUT")

# 2. Tous les comptes distincts dans BOB_OUT commençant par 8
print()
print("=== BOB_OUT: TOUS comptes commençant par 8 ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        BOB_OUT[MainAccount],
        "Amount", SUM(BOB_OUT[AccountingCurrencyAmount]),
        "Count", COUNTROWS(BOB_OUT)
    ),
    LEFT(BOB_OUT[MainAccount], 1) = "8"
)
ORDER BY BOB_OUT[MainAccount]
""")
if rows:
    for r in rows:
        try: amt = float(r[1])
        except: amt = 0
        print(f"  Compte {r[0]:<15} {amt:>14,.2f}  cnt={r[2]}")
else:
    print("  Aucun compte 8x dans BOB_OUT")

# 3. msdyn_actual — tous les comptes distincts
print()
print("=== msdyn_actual: Transaction categories distinctes (tous comptes GL) ===")
rows = dax("""
EVALUATE
CALCULATETABLE(
    SUMMARIZECOLUMNS(
        msdyn_actual[Transaction category],
        "Amount", SUM(msdyn_actual[Amount]),
        "Count", COUNTROWS(msdyn_actual)
    ),
    LEFT(msdyn_actual[Transaction category], 1) = "8" ||
    LEFT(msdyn_actual[Transaction category], 2) = "89"
)
ORDER BY msdyn_actual[Transaction category]
""")
if rows:
    for r in rows:
        try: amt = float(r[1])
        except: amt = 0
        print(f"  {r[0]:<20} {amt:>14,.2f}  cnt={r[2]}")
else:
    print("  Aucun compte 8x dans msdyn_actual")

# 4. GL_MainAccounts — voir ce qu'on a
print()
print("=== GL_MainAccounts (toutes les entrées) ===")
rows = dax("EVALUATE GL_MainAccounts ORDER BY GL_MainAccounts[MainAccountId]")
for r in rows:
    print(f"  {r}")

conn.Close()
