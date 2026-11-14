import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, SingleColumnRelationship, RelationshipEndCardinality, CrossFilteringBehavior
)

PORT = 64093

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

tables = [t.Name for t in model.Tables]
print('Tables: ' + ', '.join(t for t in tables if not t.startswith('Local') and not t.startswith('Date')))

bob    = model.Tables.Find('BOB_OUT')
gldates = model.Tables.Find('GL_HEADER')
dates  = model.Tables.Find('Dates')

if not bob:    print('ERREUR: BOB_OUT introuvable'); srv.Disconnect(); sys.exit(1)
if not gldates: print('ERREUR: GL_HEADER introuvable'); srv.Disconnect(); sys.exit(1)
if not dates:  print('ERREUR: Dates introuvable'); srv.Disconnect(); sys.exit(1)

print('Colonnes GL_Dates: ' + ', '.join(c.Name for c in gldates.Columns))
print('Colonnes BOB_OUT: '  + ', '.join(c.Name for c in bob.Columns))

def add_rel(name, from_table, from_col, to_table, to_col):
    if model.Relationships.Find(name):
        print('Relation %s existe deja — skip' % name)
        return
    fc = from_table.Columns.Find(from_col)
    tc = to_table.Columns.Find(to_col)
    if not fc: print('ERREUR colonne %s.%s introuvable' % (from_table.Name, from_col)); return
    if not tc: print('ERREUR colonne %s.%s introuvable' % (to_table.Name, to_col)); return
    rel = SingleColumnRelationship()
    rel.Name = name
    rel.FromColumn = fc
    rel.ToColumn   = tc
    rel.FromCardinality = RelationshipEndCardinality.Many
    rel.ToCardinality   = RelationshipEndCardinality.One
    rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
    rel.IsActive = True
    model.Relationships.Add(rel)
    print('Relation %s creee : %s[%s] -> %s[%s]' % (name, from_table.Name, from_col, to_table.Name, to_col))

add_rel('BOB_OUT_to_GL_Dates', bob,    'GeneralJournalEntry', gldates, 'SourceKey')
add_rel('GL_Dates_to_Dates',   gldates, 'AccountingDate',      dates,   'Date')

model.SaveChanges()
print('\n=== Relations sauvegardees ===')
srv.Disconnect()
