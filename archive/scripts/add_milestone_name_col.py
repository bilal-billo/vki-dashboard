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

# Vérifier si les colonnes existent déjà
existing_cols = [col.Name for col in t.Columns]
print(f"Colonnes actuelles: {existing_cols}")

def add_data_col_if_missing(name, source_col, dtype):
    if name not in existing_cols:
        col = TOM_NS.DataColumn()
        col.Name = name
        col.SourceColumn = source_col
        col.DataType = dtype
        t.Columns.Add(col)
        print(f"  Added column: {name} (source: {source_col})")
    else:
        print(f"  Already exists: {name}")

# Ajouter les nouvelles colonnes de la M query
add_data_col_if_missing('Milestone Name', 'Milestone Name', TOM_NS.DataType.String)
add_data_col_if_missing('Contract Line Description', 'Contract Line Description', TOM_NS.DataType.String)

# Refresh + SaveChanges
t.RequestRefresh(TOM_NS.RefreshType.Full)
m.SaveChanges()
print("\nSaveChanges() OK — nouvelles colonnes ajoutées et refresh déclenché")

# Vérifier
new_cols = [col.Name for col in t.Columns if col.Type.ToString() != 'RowNumber']
print(f"Nouvelles colonnes: {new_cols}")

srv.Disconnect()
