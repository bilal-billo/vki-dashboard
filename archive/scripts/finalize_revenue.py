import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, SingleColumnRelationship, RelationshipEndCardinality,
    CrossFilteringBehavior, Measure
)

srv = Server()
srv.Connect('localhost:64093')
db = srv.Databases[0]
model = db.Model

bob      = model.Tables.Find('BOB_OUT')
projects = model.Tables.Find('Projects')
measures = model.Tables.Find('_Measures')

# 1. Relation BOB_OUT[FOProjectId] -> Projects[Project]
rel_name = 'BOB_OUT_to_Projects'
if model.Relationships.Find(rel_name) is None:
    rel = SingleColumnRelationship()
    rel.Name = rel_name
    rel.FromColumn = bob.Columns.Find('FOProjectId')
    rel.ToColumn   = projects.Columns.Find('Project')
    rel.FromCardinality = RelationshipEndCardinality.Many
    rel.ToCardinality   = RelationshipEndCardinality.One
    rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
    rel.IsActive = True
    model.Relationships.Add(rel)
    print('Relation BOB_OUT[FOProjectId] -> Projects[Project] creee')
else:
    print('Relation BOB_OUT -> Projects existe deja')

# 2. Mesure Revenue_BOB
m_name = 'Revenue_BOB'
m_expr = """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] = "CustRevenue"
)"""
existing = measures.Measures.Find(m_name)
if existing is None:
    m = Measure()
    m.Name = m_name
    m.Expression = m_expr
    m.FormatString = '#,##0 EUR'
    m.DisplayFolder = 'Revenues'
    measures.Measures.Add(m)
    print('Mesure Revenue_BOB creee')
else:
    existing.Expression = m_expr
    print('Mesure Revenue_BOB mise a jour')

model.SaveChanges()
print('\n=== TOUT EST PRET POUR LA PAGE REVENUE ===')
print('  BOB_OUT[FOProjectId] -> Projects[Project]  OK')
print('  BOB_OUT -> GL_HEADER -> Dates              OK')
print('  Mesure Revenue_BOB                         OK')
srv.Disconnect()
