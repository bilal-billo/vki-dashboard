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

for ms in t.Measures:
    if ms.Name == 'Approved Milestones':
        ms.Expression = 'CALCULATE(SUM(Milestones[Line Amount]), Milestones[MilestoneStatus] = "Posted")'
        print('Fixed: Approved Milestones')
    elif ms.Name == 'Planned Milestones':
        ms.Expression = 'SUM(Milestones[Line Amount])'
        print('Fixed: Planned Milestones')
    elif ms.Name == 'Not Ready Count':
        ms.Expression = 'CALCULATE(COUNTROWS(Milestones), Milestones[MilestoneStatus] = "Not Ready")'
        print('Fixed: Not Ready Count')
    elif ms.Name == 'Posted Count':
        ms.Expression = 'CALCULATE(COUNTROWS(Milestones), Milestones[MilestoneStatus] = "Posted")'
        print('Fixed: Posted Count')
    elif ms.Name == 'Milestone Completion %':
        ms.Expression = 'DIVIDE(CALCULATE(SUM(Milestones[Line Amount]), Milestones[MilestoneStatus] = "Posted"), SUM(Milestones[Line Amount]), 0)'
        print('Fixed: Milestone Completion %')
    elif ms.Name == 'Requested Amount':
        ms.Expression = 'CALCULATE(SUM(msdyn_actual[Amount]), msdyn_actual[Transaction Type] = "Billed Sales")'
        print('Fixed: Requested Amount')

m.SaveChanges()
print('SaveChanges OK — toutes les mesures corrigees')
srv.Disconnect()
