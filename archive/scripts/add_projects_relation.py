import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, SingleColumnRelationship,
    RelationshipEndCardinality, CrossFilteringBehavior
)

PORT = 56550
srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db  = srv.Databases[0]
model = db.Model

bob      = model.Tables.Find('BOB_OUT')
projects = model.Tables.Find('Projects')

if not bob:
    print('ERREUR: BOB_OUT introuvable'); srv.Disconnect(); sys.exit(1)
if not projects:
    print('ERREUR: Projects introuvable'); srv.Disconnect(); sys.exit(1)

print('Tables trouvées: BOB_OUT, Projects')

# Colonnes
from_col = bob.Columns.Find('FOProjectId')
to_col   = projects.Columns.Find('Project ID')

if not from_col:
    print('ERREUR: BOB_OUT[FOProjectId] introuvable'); srv.Disconnect(); sys.exit(1)
if not to_col:
    print('ERREUR: Projects[Project ID] introuvable'); srv.Disconnect(); sys.exit(1)

print('Colonnes trouvées: BOB_OUT[FOProjectId], Projects[Project ID]')

REL_NAME = 'BOB_OUT_to_Projects'

existing = model.Relationships.Find(REL_NAME)
if existing:
    model.Relationships.Remove(existing)
    print('Ancienne relation supprimée')

rel = SingleColumnRelationship()
rel.Name                   = REL_NAME
rel.FromColumn             = from_col
rel.ToColumn               = to_col
rel.FromCardinality        = RelationshipEndCardinality.Many
rel.ToCardinality          = RelationshipEndCardinality.One
rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
rel.IsActive               = True

model.Relationships.Add(rel)
print('Relation créée: BOB_OUT[FOProjectId] -> Projects[Project ID]')

model.SaveChanges()
print('\n=== SAUVEGARDE OK ===')
print('Le slicer VKI Stat Number filtrera maintenant Revenue Invoiced et WANI.')

# Verification
print('\nRelations actives BOB_OUT:')
for r in model.Relationships:
    if not r.IsActive: continue
    try:
        ft = r.FromColumn.Table.Name
        fn = r.FromColumn.Name
        tt = r.ToColumn.Table.Name
        tn = r.ToColumn.Name
        if ft == 'BOB_OUT' or tt == 'BOB_OUT':
            print(f'  {r.Name}: {ft}[{fn}] -> {tt}[{tn}]')
    except:
        pass

srv.Disconnect()
print('\nDone. Refresh le PBI et teste le slicer.')
