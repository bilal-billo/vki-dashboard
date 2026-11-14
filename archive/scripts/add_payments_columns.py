import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()

import System.Globalization as Globalization
import System.Threading as Threading
# Forcer locale en-US pour éviter LCID 4096
Threading.Thread.CurrentThread.CurrentCulture = Globalization.CultureInfo.GetCultureInfo('en-US')

from Microsoft.AnalysisServices.Tabular import (
    Server, Measure, CalculatedColumn, DataType,
    SingleColumnRelationship, CrossFilteringBehavior
)

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model

EN_US = Globalization.CultureInfo.GetCultureInfo('en-US')

def upsert_calc_col(tbl_name, col_name, expr, dtype=DataType.Int64):
    tbl = model.Tables.Find(tbl_name)
    if not tbl:
        print(f"  TABLE INTROUVABLE: {tbl_name}")
        return
    old = tbl.Columns.Find(col_name)
    if old:
        # Modifier l'expression plutôt que supprimer/recréer
        old.Expression = expr
        old.DataType = dtype
        print(f"  Updated [{tbl_name}][{col_name}]")
    else:
        col = CalculatedColumn()
        col.Name = col_name
        col.Expression = expr
        col.DataType = dtype
        col.Locale = EN_US
        tbl.Columns.Add(col)
        print(f"  Created [{tbl_name}][{col_name}]")

def upsert_measure(name, expr, fmt=None):
    tbl = model.Tables.Find('_Measures')
    old = tbl.Measures.Find(name)
    if old:
        tbl.Measures.Remove(old)
    m = Measure()
    m.Name = name
    m.Expression = expr
    if fmt:
        m.FormatString = fmt
    tbl.Measures.Add(m)
    print(f"  OK mesure [{name}]")

VKI_FY = "IF(MONTH({col}) >= 10, YEAR({col}) + 1, YEAR({col}))"

print("=== 1. Colonnes VKI FY ===")
upsert_calc_col('Dates',       'VKI FY', VKI_FY.format(col='[Date]'))
upsert_calc_col('GL_HEADER',   'VKI FY', VKI_FY.format(col='[AccountingDate]'))
upsert_calc_col('msdyn_actual','VKI FY', VKI_FY.format(col='[Accounting Date]'))
upsert_calc_col('Milestones',  'VKI FY', VKI_FY.format(col='[Milestone date]'))

print("\n=== 2. GL Account Prefix sur BOB_OUT ===")
upsert_calc_col('BOB_OUT', 'GL Account Prefix', 'LEFT([MainAccount], 2)', dtype=DataType.String)

print("\n=== 3. Mesure Planned VKI ===")
upsert_measure('Planned VKI', 'SUM(Milestones[Line Amount])', '"€"#,0.00')

print("\n=== 4. Relation msdyn_actual[Accounting Date] → Dates[Date] ===")
dates_tbl  = model.Tables.Find('Dates')
actual_tbl = model.Tables.Find('msdyn_actual')
dates_col  = dates_tbl.Columns.Find('Date')
actual_col = actual_tbl.Columns.Find('Accounting Date')

rel_exists = False
for rel in model.Relationships:
    try:
        fc = rel.FromColumn
        tc = rel.ToColumn
        if (fc.Name == 'Accounting Date' and fc.Table.Name == 'msdyn_actual' and
            tc.Name == 'Date' and tc.Table.Name == 'Dates'):
            rel_exists = True
            print("  Relation existe déjà")
            break
    except:
        pass

if not rel_exists and dates_col and actual_col:
    new_rel = SingleColumnRelationship()
    new_rel.FromColumn = actual_col
    new_rel.ToColumn   = dates_col
    new_rel.IsActive   = True
    new_rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
    model.Relationships.Add(new_rel)
    print("  Relation créée: msdyn_actual[Accounting Date] → Dates[Date] (active)")

model.SaveChanges()
print("\nSauvegarde OK")
srv.Disconnect()
