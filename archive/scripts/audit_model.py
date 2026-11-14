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

print("=" * 80)
print("AUDIT COMPLET DU MODELE PBI")
print("=" * 80)

for t in m.Tables:
    hidden = " [HIDDEN]" if t.IsHidden else ""
    print(f"\nTABLE: {t.Name}{hidden}  ({t.Columns.Count} cols, {t.Measures.Count} measures)")

    # Colonnes
    data_cols = []
    calc_cols = []
    for col in t.Columns:
        if col.Type.ToString() == 'RowNumber':
            continue
        elif col.Type.ToString() == 'Calculated':
            calc_cols.append(col)
        else:
            data_cols.append(col)

    if data_cols:
        print(f"  Data columns ({len(data_cols)}):")
        for col in data_cols:
            h = " [hidden]" if col.IsHidden else ""
            print(f"    [{col.Name}]{h}")

    if calc_cols:
        print(f"  Calculated columns ({len(calc_cols)}):")
        for col in calc_cols:
            h = " [hidden]" if col.IsHidden else ""
            print(f"    [{col.Name}] = {col.Expression[:60]}{h}")

    if t.Measures.Count > 0:
        print(f"  Measures ({t.Measures.Count}):")
        for ms in t.Measures:
            h = " [hidden]" if ms.IsHidden else ""
            print(f"    [{ms.Name}] = {ms.Expression[:70]}{h}")

srv.Disconnect()
