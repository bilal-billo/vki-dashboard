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

# Supprimer l'ancienne relation (BOB_OUT[FOProjectId] -> Projects[Project] GUID)
old = model.Relationships.Find('BOB_OUT_to_Projects')
if old:
    model.Relationships.Remove(old)
    print('Ancienne relation BOB_OUT_to_Projects supprimee')
else:
    print('Ancienne relation introuvable — recherche par colonnes...')
    for rel in list(model.Relationships):
        if (rel.FromTable.Name == 'BOB_OUT' and rel.FromColumn.Name == 'FOProjectId'):
            print('  Suppression: %s[%s] -> %s[%s]' % (
                rel.FromTable.Name, rel.FromColumn.Name,
                rel.ToTable.Name, rel.ToColumn.Name))
            model.Relationships.Remove(rel)

# Creer la nouvelle relation: BOB_OUT[FOProjectId] -> Projects[Project ID]
bob = model.Tables.Find('BOB_OUT')
proj = model.Tables.Find('Projects')

fc = bob.Columns.Find('FOProjectId')
tc = proj.Columns.Find('Project ID')

if not fc:
    print('ERREUR: BOB_OUT[FOProjectId] introuvable')
elif not tc:
    print('ERREUR: Projects[Project ID] introuvable')
    print('Colonnes Projects: ' + ', '.join(c.Name for c in proj.Columns))
else:
    rel = SingleColumnRelationship()
    rel.Name = 'BOB_OUT_to_Projects_v2'
    rel.FromColumn = fc
    rel.ToColumn = tc
    rel.FromCardinality = RelationshipEndCardinality.Many
    rel.ToCardinality = RelationshipEndCardinality.One
    rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
    rel.IsActive = True
    model.Relationships.Add(rel)
    print('Nouvelle relation creee: BOB_OUT[FOProjectId] -> Projects[Project ID]')

model.SaveChanges()
print('\n=== Sauvegarde OK ===')
srv.Disconnect()
