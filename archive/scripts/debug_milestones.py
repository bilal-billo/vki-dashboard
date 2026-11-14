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

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model
t = model.Tables.Find('Dates')
print('=== Dates columns ===')
for c in t.Columns:
    if not c.Name.startswith('RowNumber'):
        print(' ', c.Name, '-', str(c.DataType))
srv.Disconnect()

print()
print('=== Sample Dates rows ===')
_, r = dax("""
EVALUATE
TOPN(3, FILTER(Dates, Dates[Date] >= DATE(2026,6,28) && Dates[Date] <= DATE(2026,7,2)))
ORDER BY Dates[Date]
""")
for row in r:
    print(' ', {k.split('[')[1].rstrip(']'): v for k,v in row.items()})

print()
print('=== Total Milestones Posted EAR 2411 sans filtre date ===')
_, r2 = dax("""
EVALUATE
CALCULATETABLE(
    ROW("Posted", CALCULATE(SUM(Milestones[Line Amount]), Milestones[msdyn_invoicestatus] = 192350003,
        ALL(Dates))),
    FILTER(Projects, Projects[VKI Stat Number] = "EAR 2411")
)""")
for row in r2:
    for k,v in row.items():
        print('  {} = {}'.format(k.strip('[]').strip(), v))
