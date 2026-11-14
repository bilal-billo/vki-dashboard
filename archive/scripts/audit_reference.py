import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, MPartitionSource
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

REF_PORT  = 60574  # Project Financial Dashboard NEW (SQL)
NEW_PORT  = 63175  # firstbuilD (Dataverse)

def dax(port, query):
    conn = AdomdConnection('Data Source=localhost:{}'.format(port))
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
    return rows

def read_model(port, label):
    srv = Server()
    srv.Connect('localhost:{}'.format(port))
    db = srv.Databases[0]
    model = db.Model

    print('\n' + '='*60)
    print('MODELE: {} (port {})'.format(label, port))
    print('='*60)

    print('\n--- TABLES & SOURCES ---')
    for t in model.Tables:
        if t.Name.startswith('LocalDate') or t.Name.startswith('DateTable'):
            continue
        src_info = ''
        for p in t.Partitions:
            s = p.Source
            if s and hasattr(s, 'Expression'):
                expr = s.Expression[:120].replace('\n',' ').strip()
                src_info = expr
        print('  [{}]  {}'.format(t.Name, src_info[:100]))

    print('\n--- MESURES (nom + expression tronquee) ---')
    for t in model.Tables:
        for m in t.Measures:
            print('  [{}] {}  =  {}'.format(t.Name, m.Name, m.Expression[:100].replace('\n',' ').strip()))

    srv.Disconnect()

read_model(REF_PORT, 'Reference SQL')
read_model(NEW_PORT, 'New Dataverse')

print('\n' + '='*60)
print('VOLUMES REFERENCE (sans filtre projet)')
print('='*60)

ref_tables = ['OdooData','Milestones','Invoices','Projects','Contracts']
for tbl in ref_tables:
    try:
        r = dax(REF_PORT, 'EVALUATE ROW("N", COUNTROWS({}))'.format(tbl))
        print('  REF {}: {} rows'.format(tbl, r[0].get('[N]','?')))
    except:
        print('  REF {}: ERROR'.format(tbl))

print()
for tbl in ref_tables:
    try:
        r = dax(NEW_PORT, 'EVALUATE ROW("N", COUNTROWS({}))'.format(tbl))
        print('  NEW {}: {} rows'.format(tbl, r[0].get('[N]','?')))
    except:
        print('  NEW {}: ERROR'.format(tbl))
