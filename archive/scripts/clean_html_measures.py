import clr, sys
sys.path.append(r'C:\Program Files\Microsoft SQL Server Management Studio 21\Release\Common7\IDE')
clr.AddReference('Microsoft.AnalysisServices.Tabular')
import Microsoft.AnalysisServices.Tabular as TOM_NS
import System.Globalization as Glob
import System.Threading as Thr
Thr.Thread.CurrentThread.CurrentCulture = Glob.CultureInfo.GetCultureInfo('en-US')

srv = TOM_NS.Server()
srv.Connect('localhost:49640')
db = srv.Databases[0]
m = db.Model

HIDE = {
    # HTML measures
    '_HTML_Planning_Table',
    '_HTML_Budget_Progress',
    '_HTML_Claimable_Table',
    '_HTML_Overview_KPIs',
    '_HTML_Budget_Chart',
    # Card measures (formatées pour affichage, redondantes)
    'Budget Card',
    'Remaining Card',
    'Invoiced Card',
    'WANI Card',
    'Revenue D365 Card',
    # Mesures OdooData (données quasi vides)
    'Total Hours',
    'Total Direct Costs',
    'Avg Hourly Rate',
    'Timesheet Lines Count',
    'Active Employees Count',
    # Anciennes mesures redondantes
    'Revenue_BOB',          # = Revenue Invoiced D365
    'Total Revenues Cumulative',  # ancienne logique cumulative
    'Remaining vs Revenues',      # = Remaining Budget
    'Remaining vs Claimable',     # = Remaining Budget
}

hidden = 0
for t in m.Tables:
    for ms in t.Measures:
        if ms.Name in HIDE and not ms.IsHidden:
            ms.IsHidden = True
            hidden += 1
            print(f"  Hidden: [{ms.Name}]")

m.SaveChanges()
print(f"\n{hidden} mesures masquées — SaveChanges OK")

print("\n=== Mesures visibles finales ===")
for t in m.Tables:
    visible = [ms.Name for ms in t.Measures if not ms.IsHidden]
    if visible:
        print(f"\n  {t.Name}:")
        for n in visible:
            print(f"    [{n}]")

srv.Disconnect()
