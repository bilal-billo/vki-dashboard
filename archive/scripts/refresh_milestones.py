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

print("Refresh de la table Milestones...")
t = m.Tables['Milestones']

# RequestRefresh puis SaveChanges pour déclencher le refresh
t.RequestRefresh(TOM_NS.RefreshType.Full)
m.SaveChanges()
print("Refresh demandé. PBI Desktop va recharger la table Milestones depuis Dataverse.")

srv.Disconnect()
