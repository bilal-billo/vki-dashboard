import os, sys, logging
sys.path.insert(0, 'src')
os.environ['TOM_DLL_PATH'] = r'C:\Users\Windows 11\Development\powerbi-mcp-server\tom_dlls\dlls'
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
import Microsoft.AnalysisServices.Tabular as TAB
names = [n for n in dir(TAB) if any(x in n for x in ['Relationship','Cardinality','CrossFilter','Multiplicity'])]
print('\n'.join(sorted(names)))
