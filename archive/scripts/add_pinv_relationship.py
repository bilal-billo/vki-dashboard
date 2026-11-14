import os, sys, logging
SCRIPT_DIR = r'C:\Users\Windows 11\Development\powerbi-mcp-server'
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'src'))
os.environ['TOM_DLL_PATH'] = os.path.join(SCRIPT_DIR, r'tom_dlls\dlls')
logging.disable(logging.CRITICAL)
from powerbi_mcp.powerbi_connector import PowerBIConnector
_dummy = PowerBIConnector()
from Microsoft.AnalysisServices.Tabular import (
    Server, SingleColumnRelationship, CrossFilteringBehavior
)

srv = Server()
srv.Connect('localhost:49640')
model = srv.Databases[0].Model

# Relation: msdyn_actual[Voucher Number] → GL_HEADER[SubledgerVoucher]
# Permet d'avoir la vraie date Finance via GL_HEADER[AccountingDate]
actual_tbl = model.Tables.Find('msdyn_actual')
gl_tbl     = model.Tables.Find('GL_HEADER')

from_col = actual_tbl.Columns.Find('Voucher Number')
to_col   = gl_tbl.Columns.Find('SubledgerVoucher')

if not from_col:
    print("ERREUR: msdyn_actual[Voucher Number] introuvable")
elif not to_col:
    print("ERREUR: GL_HEADER[SubledgerVoucher] introuvable")
else:
    # Vérifier si relation existe déjà
    exists = False
    for rel in model.Relationships:
        try:
            if (rel.FromColumn.Name == 'Voucher Number' and
                rel.FromColumn.Table.Name == 'msdyn_actual' and
                rel.ToColumn.Name == 'SubledgerVoucher' and
                rel.ToColumn.Table.Name == 'GL_HEADER'):
                exists = True
                print("Relation existe déjà")
                break
        except:
            pass

    if not exists:
        rel = SingleColumnRelationship()
        rel.FromColumn = from_col
        rel.ToColumn   = to_col
        rel.IsActive   = False  # Inactive pour ne pas perturber BOB_OUT→GL_HEADER active
        rel.CrossFilteringBehavior = CrossFilteringBehavior.OneDirection
        model.Relationships.Add(rel)
        print("Relation créée (inactive): msdyn_actual[Voucher Number] → GL_HEADER[SubledgerVoucher]")
        print("  → Utilise USERELATIONSHIP dans les mesures pour la date réelle")

model.SaveChanges()
print("\nSauvegarde OK")

# Vérifier le modèle
print("\n=== Relations msdyn_actual ↔ GL_HEADER ===")
for rel in model.Relationships:
    try:
        fc = rel.FromColumn
        tc = rel.ToColumn
        if 'actual' in fc.Table.Name or 'actual' in tc.Table.Name:
            if 'GL_HEADER' in fc.Table.Name or 'GL_HEADER' in tc.Table.Name:
                print(f"  {fc.Table.Name}[{fc.Name}] → {tc.Table.Name}[{tc.Name}]  active={rel.IsActive}")
    except:
        pass

srv.Disconnect()
