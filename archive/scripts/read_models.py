import os, sys, json, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)

# Importing the connector triggers pythonnet init (pythonnet.load + import clr)
from powerbi_mcp.powerbi_connector import PowerBIConnector
# Instantiate once to run _load_assemblies() (clr.AddReference calls happen there)
_dummy = PowerBIConnector()
# Now .NET types are available
from Microsoft.AnalysisServices.Tabular import Server

def read_model(port, label):
    srv = Server()
    srv.Connect('localhost:' + str(port))
    db = srv.Databases[0]
    model = db.Model

    out = {'label': label, 'port': port, 'tables': []}
    for t in model.Tables:
        tbl = {
            'name': t.Name,
            'hidden': t.IsHidden,
            'columns': [{'name': c.Name, 'type': str(c.DataType)} for c in t.Columns],
            'measures': [
                {
                    'name': m.Name,
                    'expr': m.Expression,
                    'fmt': m.FormatString,
                    'folder': m.DisplayFolder
                }
                for m in t.Measures
            ],
        }
        out['tables'].append(tbl)
    srv.Disconnect()
    return out

ref = read_model(60574, 'Project Financial Dashboard NEW')
new = read_model(60227, 'firstbuilD_powerbi_VK1906206')

out_ref = r'C:\Users\Windows 11\Development\VKI\pbi_ref_model.json'
out_new = r'C:\Users\Windows 11\Development\VKI\pbi_new_model.json'

with open(out_ref, 'w', encoding='utf-8') as f:
    json.dump(ref, f, ensure_ascii=False, indent=2)

with open(out_new, 'w', encoding='utf-8') as f:
    json.dump(new, f, ensure_ascii=False, indent=2)

ref_measures = sum(len(t['measures']) for t in ref['tables'])
new_measures = sum(len(t['measures']) for t in new['tables'])

print('DONE')
print('REF: {} tables, {} measures'.format(len(ref['tables']), ref_measures))
print('NEW: {} tables, {} measures'.format(len(new['tables']), new_measures))
