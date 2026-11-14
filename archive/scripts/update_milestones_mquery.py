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
part = list(t.Partitions)[0]
src = part.Source

new_query = r"""let
    Source = CommonDataService.Database("operations-vki-prod.crm4.dynamics.com"),
    Nav = Source{[Schema="dbo",Item="msdyn_contractlinescheduleofvalue"]}[Data],
    Cols = Table.SelectColumns(Nav, {
        "msdyn_contractlinescheduleofvalueid",
        "msdyn_name",
        "msdyn_contract","msdyn_project",
        "msdyn_amount","msdyn_contractlinemilestonenumber",
        "msdyn_invoicedate","msdyn_milestonedate","msdyn_invoicestatus",
        "msdyn_contractlinedescription"
    }),
    Renamed = Table.RenameColumns(Cols, {
        {"msdyn_contractlinescheduleofvalueid","MilestoneID"},
        {"msdyn_name","Milestone Name"},
        {"msdyn_contract","ContractID"},
        {"msdyn_project","ProjectID"},
        {"msdyn_amount","Amount"},
        {"msdyn_contractlinemilestonenumber","MilestoneNumber"},
        {"msdyn_invoicedate","InvoiceDate"},
        {"msdyn_milestonedate","MilestoneDate"},
        {"msdyn_invoicestatus","StatusCode"},
        {"msdyn_contractlinedescription","Contract Line Description"}
    }),
    Status = Table.AddColumn(Renamed, "MilestoneStatus", each
        if [StatusCode] = 192350003 then "Posted"
        else if [StatusCode] = 192350001 then "Ready"
        else if [StatusCode] = 192350000 then "Not Ready"
        else "Unknown"),
    Types = Table.TransformColumnTypes(Status, {
        {"Amount", type number},
        {"MilestoneDate", type datetime},
        {"InvoiceDate", type datetime}
    })
in
    Types"""

print("=== M query actuelle (premiers 200 chars) ===")
print(src.Expression[:200])

src.Expression = new_query
print("\n=== Nouvelle M query appliquée ===")
print(f"Longueur: {len(new_query)} chars")

m.SaveChanges()
print("\nSaveChanges() OK — Milestones M query mise a jour avec msdyn_name et msdyn_contractlinedescription")
srv.Disconnect()
