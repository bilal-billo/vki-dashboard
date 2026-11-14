import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()

from Microsoft.AnalysisServices.Tabular import Server
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

PORT = 60227

def dax(query):
    conn = AdomdConnection('Data Source=localhost:{}'.format(PORT))
    conn.Open()
    cmd = AdomdCommand(query, conn)
    reader = cmd.ExecuteReader()
    cols = [reader.GetName(i) for i in range(reader.FieldCount)]
    rows = []
    while reader.Read():
        row = {}
        for i, c in enumerate(cols):
            v = reader.GetValue(i)
            row[c] = str(v) if v is not None else 'BLANK'
        rows.append(row)
    reader.Close()
    conn.Close()
    return cols, rows

# List all tables including hidden
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

print('=== Toutes les tables du modele ===')
for t in model.Tables:
    cols = [c.Name for c in t.Columns if not c.Name.startswith('RowNumber')]
    print('  [{}] {} — colonnes: {}'.format(
        'HIDDEN' if t.IsHidden else 'VISIBLE',
        t.Name,
        cols[:8]
    ))

srv.Disconnect()

print()
print('=== Test OdooData ===')
try:
    cols, rows = dax("EVALUATE TOPN(3, OdooData)")
    print('OdooData EXISTE — colonnes:', [c for c in cols])
    print('Nb lignes visible (top3):', len(rows))
    for r in rows:
        print(' ', {k.split('[')[1].rstrip(']'): v for k, v in r.items()})
except Exception as e:
    print('OdooData NON TROUVE ou erreur:', e)

print()
print('=== Test vki_odoo_prod_datas ===')
try:
    cols2, rows2 = dax("EVALUATE TOPN(1, vki_odoo_prod_datas)")
    print('vki_odoo_prod_datas EXISTE — colonnes:', cols2[:6])
except Exception as e:
    print('Non trouve:', str(e)[:100])

print()
print('=== Test cr7d4_odoo_imported_uat_data ===')
try:
    cols3, rows3 = dax("EVALUATE TOPN(1, cr7d4_odoo_imported_uat_data)")
    print('cr7d4 EXISTE — colonnes:', cols3[:6])
except Exception as e:
    print('Non trouve:', str(e)[:100])
