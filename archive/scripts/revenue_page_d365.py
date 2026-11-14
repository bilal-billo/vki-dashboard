import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)

from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, Measure, CalculatedColumn, DataType,
    SingleColumnRelationship, RelationshipEndCardinality, CrossFilteringBehavior
)

PORT = 56550

srv = Server()
srv.Connect('localhost:{}'.format(PORT))
db = srv.Databases[0]
model = db.Model

gl   = model.Tables.Find('GL_HEADER')
dts  = model.Tables.Find('Dates')
mt   = model.Tables.Find('_Measures')
bob  = model.Tables.Find('BOB_OUT')

for name, tbl in [('GL_HEADER', gl), ('Dates', dts), ('_Measures', mt), ('BOB_OUT', bob)]:
    if not tbl:
        print('ERREUR: table %s introuvable' % name)
        srv.Disconnect()
        sys.exit(1)

print('=== Connexion OK — port %d ===' % PORT)
print('Tables: %d  Mesures: %d\n' % (
    sum(1 for _ in model.Tables),
    sum(1 for t in model.Tables for _ in t.Measures)
))

# -------------------------------------------------------
# 1. FIX DATETIME : AccountingDate (12:00) -> date pure (00:00)
# -------------------------------------------------------
print('--- Fix GL_HEADER datetime ---')

existing_col = gl.Columns.Find('AccountingDate_Date')
if not existing_col:
    col = CalculatedColumn()
    col.Name = 'AccountingDate_Date'
    col.Expression = "DATE(YEAR([AccountingDate]), MONTH([AccountingDate]), DAY([AccountingDate]))"
    col.DataType = DataType.DateTime
    col.IsHidden = True
    gl.Columns.Add(col)
    print('  CREE  : GL_HEADER[AccountingDate_Date]')
else:
    print('  EXISTE : GL_HEADER[AccountingDate_Date]')

# Supprimer ancienne relation (AccountingDate avec 12:00:00)
old = model.Relationships.Find('GL_Dates_to_Dates')
if old:
    model.Relationships.Remove(old)
    print('  SUPPRIME: GL_Dates_to_Dates (ancienne)')

# Recree avec AccountingDate_Date (minuit = match Dates[Date])
if not model.Relationships.Find('GL_Dates_to_Dates'):
    fc = gl.Columns.Find('AccountingDate_Date')
    tc = dts.Columns.Find('Date')
    if fc and tc:
        rel = SingleColumnRelationship()
        rel.Name = 'GL_Dates_to_Dates'
        rel.FromColumn = fc
        rel.ToColumn = tc
        rel.FromCardinality = RelationshipEndCardinality.Many
        rel.ToCardinality = RelationshipEndCardinality.One
        rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
        rel.IsActive = True
        model.Relationships.Add(rel)
        print('  CREE  : GL_Dates_to_Dates  GL_HEADER[AccountingDate_Date] -> Dates[Date]')
    else:
        print('  ERREUR: colonnes introuvables pour la relation')

# -------------------------------------------------------
# 2. MESURES REVENUE
# -------------------------------------------------------
print('\n--- Mesures Revenue ---')

def upsert(name, expr, fmt=u'\u20ac #,##0', folder='Revenues'):
    m = mt.Measures.Find(name)
    if m is None:
        m = Measure()
        m.Name = name
        mt.Measures.Add(m)
        print('  CREE  : [%s]' % name)
    else:
        print('  MAJ   : [%s]' % name)
    m.Expression = expr
    m.FormatString = fmt
    m.DisplayFolder = folder

# Revenue Invoiced D365 = CustRevenue + ProjOnAccount + ProjTurnover
# Note : CustRevenue et ProjOnAccount sont des credits (negatifs) → -SUM = positif
#        ProjTurnover est un debit (positif) → -SUM = negatif (reduction revenue partenaires)
upsert('Revenue Invoiced D365', """CALCULATE(
    -SUM(BOB_OUT[AccountingCurrencyAmount]),
    BOB_OUT[PostingType] IN {"CustRevenue", "ProjOnAccount", "ProjTurnover"}
)""")

# WANI D365 = solde net compte 37000000
# Sophie 10/08 : WANI dans D365 = compte 37 (pas 711 qui = 0)
upsert('WANI D365', """CALCULATE(
    SUM(BOB_OUT[AccountingCurrencyAmount]),
    CONTAINSSTRING(BOB_OUT[LedgerDimensionValuesJson], "37000000")
)""")

# Project Revenues D365 = Invoiced + WANI
upsert('Project Revenues D365',
    "COALESCE([Revenue Invoiced D365], 0) + COALESCE([WANI D365], 0)")

# Card KPI
upsert('Revenue D365 Card',
    '"\\u20ac" & FORMAT([Project Revenues D365] / 1000000, "0.0") & "M"',
    fmt='', folder='Revenues')

# -------------------------------------------------------
# 3. SAVE
# -------------------------------------------------------
model.SaveChanges()
print('\n=== SAUVEGARDE OK ===')

# -------------------------------------------------------
# 4. VERIFICATION via DAX
# -------------------------------------------------------
print('\nVerification mesures:')
for m in mt.Measures:
    if any(x in m.Name for x in ['Revenue', 'WANI', 'Invoiced']):
        print('  [%s]' % m.Name)

print('\nRelations actives:')
for r in model.Relationships:
    if r.IsActive and hasattr(r, 'FromColumn') and hasattr(r, 'ToColumn'):
        try:
            print('  %s : %s[%s] -> %s[%s]' % (
                r.Name,
                r.FromColumn.Table.Name, r.FromColumn.Name,
                r.ToColumn.Table.Name, r.ToColumn.Name
            ))
        except:
            print('  %s (details N/A)' % r.Name)

srv.Disconnect()
print('\nDone. Ouvre PBI et verifie la page Revenue.')
