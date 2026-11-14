import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import Server

PORT = 63175

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

fixes = {
    'Total Milestones Posted': 'CALCULATE(SUM(Milestones[Line Amount]), Milestones[msdyn_invoicestatus] = 192350003, ALL(Dates))',
    'Total Milestones Ready':  'CALCULATE(SUM(Milestones[Line Amount]), Milestones[msdyn_invoicestatus] = 192350001, ALL(Dates))',
    'Total Milestones Pending':'CALCULATE(SUM(Milestones[Line Amount]), Milestones[msdyn_invoicestatus] <> 192350003, ALL(Dates))',
}

for tbl in model.Tables:
    for m in tbl.Measures:
        if m.Name in fixes:
            print('Fixing [{}] {} ...'.format(tbl.Name, m.Name))
            m.Expression = fixes[m.Name]
            print('  OK')

model.SaveChanges()
print('\nSave OK — refresh la page Budget')
srv.Disconnect()
