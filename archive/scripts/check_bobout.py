import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

PORT = 63175

conn = AdomdConnection('Data Source=localhost:{}'.format(PORT))
conn.Open()

queries = {
    'BOB_OUT lignes':   'EVALUATE ROW("n", COUNTROWS(BOB_OUT))',
    'BOB_OUT amount':   'EVALUATE ROW("amt", [Revenue_BOB_OUT])',
    'BOB_OUT projets':  'EVALUATE ROW("p", DISTINCTCOUNT(BOB_OUT[StatNumber]))',
}

for label, q in queries.items():
    try:
        cmd = AdomdCommand(q, conn)
        reader = cmd.ExecuteReader()
        reader.Read()
        val = reader.GetValue(0)
        print('%s: %s' % (label, val))
        reader.Close()
    except Exception as e:
        print('%s: ERREUR -> %s' % (label, str(e)[:80]))

conn.Close()
