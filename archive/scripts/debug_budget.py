import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

PORT = 63175

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

# Lire les mesures du modèle
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

print('=== Mesures dans le modèle ===')
for t in model.Tables:
    for m in t.Measures:
        print('  [{}] {}'.format(t.Name, m.Name))
        print('    {}'.format(m.Expression[:200]))
        print()

srv.Disconnect()

print()
print('=== Milestones count ===')
_, r = dax("EVALUATE ROW(\"N\", COUNTROWS(Milestones))")
for row in r:
    for k,v in row.items(): print('  {} = {}'.format(k.strip('[]').strip(), v))

print()
print('=== Invoices count ===')
_, r = dax("EVALUATE ROW(\"N\", COUNTROWS(Invoices))")
for row in r:
    for k,v in row.items(): print('  {} = {}'.format(k.strip('[]').strip(), v))
