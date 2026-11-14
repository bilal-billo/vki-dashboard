import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
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

print('=== Volume OdooData ===')
_, r = dax("""
EVALUATE ROW(
    "Count",   COUNTROWS(OdooData),
    "MinDate", FORMAT(MIN(OdooData[Date]), "YYYY-MM-DD"),
    "MaxDate", FORMAT(MAX(OdooData[Date]), "YYYY-MM-DD"),
    "TotalAmount", SUM(OdooData[Amount])
)""")
for row in r:
    for k,v in row.items():
        print('  {:20s} = {}'.format(k.strip('[]').strip(), v))

print()
print('=== Journaux analytiques (Cost Category) ===')
_, r2 = dax("""
EVALUATE
SUMMARIZECOLUMNS(
    OdooData[AnalyticalJournal],
    "Count", COUNTROWS(OdooData),
    "Amount", SUM(OdooData[Amount])
)
ORDER BY [Amount] ASC
""")
for row in r2:
    print('  {:30s} | {:6s} rows | €{}'.format(
        row.get('OdooData[AnalyticalJournal]','?'),
        row.get('[Count]','?'),
        row.get('[Amount]','?')
    ))

print()
print('=== Sample T6 Travel (comme reference) ===')
_, r3 = dax("""
EVALUATE
TOPN(3,
    FILTER(OdooData, OdooData[AnalyticalJournal] = "T6 Travel"),
    OdooData[Amount], ASC
)
""")
for row in r3:
    print('  StatNr={} | Date={} | Employee={} | Amount={} | FA={}'.format(
        row.get('OdooData[StatNumber]','?'),
        row.get('OdooData[Date]','?'),
        row.get('OdooData[Employee]','?'),
        row.get('OdooData[Amount]','?'),
        row.get('OdooData[FinancialAccount]','?')[:50]
    ))
