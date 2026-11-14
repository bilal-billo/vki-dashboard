import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server, Measure

PORT = 64093

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

mt = model.Tables.Find('_Measures')
if not mt:
    print('ERREUR: table _Measures introuvable'); srv.Disconnect(); sys.exit(1)

MEASURES = [
    {
        'name': 'Invoiced',
        'expr': '[Revenue_BOB]',
        'format': u'\u20ac #,##0',
        'folder': 'Revenues'
    },
    {
        'name': 'WANI',
        'expr': '0',
        'format': u'\u20ac #,##0',
        'folder': 'Revenues'
    },
    {
        'name': 'Revenue_All',
        'expr': '[Revenue_BOB] + [WANI]',
        'format': u'\u20ac #,##0',
        'folder': 'Revenues'
    },
    {
        'name': 'Revenue_FY_Current',
        'expr': "CALCULATE([Revenue_BOB], Dates[vKI Financial Year] = YEAR(TODAY()))",
        'format': u'\u20ac #,##0',
        'folder': 'Revenues'
    },
]

for m_def in MEASURES:
    existing = mt.Measures.Find(m_def['name'])
    if existing is None:
        m = Measure()
        m.Name = m_def['name']
        m.Expression = m_def['expr']
        m.FormatString = m_def['format']
        m.DisplayFolder = m_def['folder']
        mt.Measures.Add(m)
        print('  CREE  : ' + m_def['name'])
    else:
        existing.Expression = m_def['expr']
        existing.FormatString = m_def['format']
        print('  MAJ   : ' + m_def['name'])

model.SaveChanges()
print('\n=== Mesures Revenue sauvegardees ===')

# Verification
print('\nMesures dans _Measures:')
for m in mt.Measures:
    print('  - ' + m.Name)

srv.Disconnect()
