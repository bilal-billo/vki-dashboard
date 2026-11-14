import sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, SCRIPT_DIR + r'\src')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()

# Tester les imports un par un
tests = [
    'SingleColumnRelationship',
    'RelationshipEndMultiplicity',
    'RelationshipEndCardinality',
    'CrossFilteringBehavior',
    'RelationshipCardinality',
    'Table',
    'DataColumn',
    'Partition',
    'MPartitionSource',
    'Measure',
    'ColumnDataType',
    'DataType',
]
for name in tests:
    try:
        exec('from Microsoft.AnalysisServices.Tabular import %s' % name)
        print('OK: %s' % name)
    except ImportError as e:
        print('FAIL: %s -> %s' % (name, e))
