import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
import Microsoft.AnalysisServices.Tabular as TAB
names = [n for n in dir(TAB) if any(x in n for x in ['Relationship','Cardinality','CrossFilter','Multiplicity'])]
print('\n'.join(sorted(names)))
