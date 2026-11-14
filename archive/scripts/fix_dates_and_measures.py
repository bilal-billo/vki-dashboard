import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, CalculatedColumn, DataType
)

PORT = 64093

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

# --- Inspecter Dates ---
dates_tbl = model.Tables.Find('Dates')
if not dates_tbl:
    print('ERREUR: table Dates introuvable')
    srv.Disconnect()
    sys.exit(1)

print('Colonnes Dates:')
for c in dates_tbl.Columns:
    print('  [%s] type=%s kind=%s' % (c.Name, c.DataType, c.Type))

# --- Ajouter colonnes calculees si absentes ---
def add_calc_col(table, name, expr, dtype):
    if table.Columns.Find(name):
        print('  deja present: ' + name)
        return
    col = CalculatedColumn()
    col.Name = name
    col.Expression = expr
    col.DataType = dtype
    col.IsHidden = False
    table.Columns.Add(col)
    print('  CREE: ' + name)

# Calendar Year (prerequis)
add_calc_col(dates_tbl, 'Calendar Year',
    "YEAR('Dates'[Date])",
    DataType.Int64)

# Calendar Quarter (prerequis)
add_calc_col(dates_tbl, 'Calendar Quarter',
    """SWITCH(MONTH('Dates'[Date]),
    1,"Q1",2,"Q1",3,"Q1",
    4,"Q2",5,"Q2",6,"Q2",
    7,"Q3",8,"Q3",9,"Q3",
    10,"Q4",11,"Q4",12,"Q4",
    "NOK")""",
    DataType.String)

# vKI Financial Year
add_calc_col(dates_tbl, 'vKI Financial Year',
    """IF(
    'Dates'[Calendar Year] > 2023,
    'Dates'[Calendar Year],
    IF(
        'Dates'[Calendar Year] = 2023 && 'Dates'[Calendar Quarter] = "Q4",
        'Dates'[Calendar Year],
        IF(
            'Dates'[Calendar Quarter] = "Q4",
            'Dates'[Calendar Year] + 1,
            'Dates'[Calendar Year]
        )
    )
)""",
    DataType.Int64)

# vKI Fiscal Year (string "FY 2026")
add_calc_col(dates_tbl, 'vKI Fiscal Year',
    'CONCATENATE("FY ", \'Dates\'[vKI Financial Year])',
    DataType.String)

# --- Fix Revenue_FY_Current (utilise maintenant vKI Financial Year) ---
mt = model.Tables.Find('_Measures')
m = mt.Measures.Find('Revenue_FY_Current')
if m:
    m.Expression = """VAR _fy = YEAR(TODAY())
RETURN CALCULATE(
    [Revenue_BOB],
    FILTER(ALL('Dates'), 'Dates'[vKI Financial Year] = _fy)
)"""
    print('Revenue_FY_Current: expression conservee (vKI Financial Year maintenant disponible)')

model.SaveChanges()
print('\n=== Sauvegarde OK ===')
srv.Disconnect()
