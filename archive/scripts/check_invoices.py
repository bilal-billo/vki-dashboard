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

# Check Invoices table columns and sample data
print('=== Colonnes de la table Invoices ===')
q = "EVALUATE TOPN(5, Invoices)"
cols, rows = dax(q)
print('Colonnes:', cols)
print()
for row in rows:
    print(' ', row)

print()
print('=== Relations impliquant Invoices ===')
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

for rel in model.Relationships:
    from_t = rel.FromTable.Name
    to_t = rel.ToTable.Name
    if 'Invoice' in from_t or 'Invoice' in to_t:
        print('  {} [{}] -> {} [{}] | Active: {}'.format(
            from_t, rel.FromColumn.Name,
            to_t, rel.ToColumn.Name,
            rel.IsActive
        ))
srv.Disconnect()

print()
print('=== Total Invoiced sans filtre projet ===')
q2 = "EVALUATE ROW(\"Total\", SUM(Invoices[Total Amount]), \"Count\", COUNTROWS(Invoices))"
_, rows2 = dax(q2)
for row in rows2:
    print(' ', row)
