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
t = m.Tables['Milestones']
existing = [col.Name for col in t.Columns]

dax_expr = (
    'SWITCH(TRUE(),'
    'CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "ADVANCE") || CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "ACOMPTE"), "Advance Payment",'
    'CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "REPRISE") || CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "RECOVERY"), "AP Recovery",'
    'CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "FINAL"), "Final Payment",'
    'CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "PERIODIC") || CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "REPORT") || LEFT(UPPER(Milestones[Milestone Name]), 2) = "RP", "Periodic Report",'
    'CONTAINSSTRING(UPPER(Milestones[Milestone Name]), "INTERIM") || LEFT(UPPER(Milestones[Milestone Name]), 2) = "IP", "Interim Payment",'
    '"Other Milestone"'
    ')'
)

if 'Milestone Category' not in existing:
    col = TOM_NS.CalculatedColumn()
    col.Name = 'Milestone Category'
    col.DataType = TOM_NS.DataType.String
    col.Expression = dax_expr
    t.Columns.Add(col)
    print('Milestone Category ajoutee')
else:
    t.Columns['Milestone Category'].Expression = dax_expr
    print('Milestone Category mise a jour')

t.RequestRefresh(TOM_NS.RefreshType.Calculate)
m.SaveChanges()
print('SaveChanges OK')
srv.Disconnect()
