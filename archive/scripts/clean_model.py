import clr, sys
sys.path.append(r'C:\Program Files\Microsoft SQL Server Management Studio 21\Release\Common7\IDE')
clr.AddReference('Microsoft.AnalysisServices.Tabular')
import Microsoft.AnalysisServices.Tabular as TOM_NS
import System.Globalization as Glob
import System.Threading as Thr
Thr.Thread.CurrentThread.CurrentCulture = Glob.CultureInfo.GetCultureInfo('en-US')

srv = TOM_NS.Server()
srv.Connect('localhost:49640')
db = srv.Databases[0]
m = db.Model

# ============================================================
# 1. Query1 — afficher le contenu avant de décider
# ============================================================
print("=== Query1 : colonnes et M query ===")
t_q1 = m.Tables['Query1']
for col in t_q1.Columns:
    if col.Type.ToString() != 'RowNumber':
        print(f"  [{col.Name}] src=[{col.SourceColumn if col.Type.ToString()=='Data' else ''}]")
for part in t_q1.Partitions:
    print(f"  M query: {part.Source.Expression[:300]}")

# ============================================================
# 2. msdyn_actual — masquer les colonnes inutiles
# ============================================================
print("\n=== msdyn_actual : masquage colonnes inutiles ===")

# Colonnes à GARDER visibles (essentielles)
KEEP_VISIBLE = {
    'msdyn_project',            # relation Projects
    'Transaction Type',         # Cost / Billed Sales / etc.
    'Transaction category',     # GL account (texte)
    'Amount',                   # montant
    'Accounting Date',          # date comptable
    'Document Date',            # date document
    'Description',              # description ligne
    'Voucher Number',           # lien PINV → GL_HEADER
    'Project Contract Line 2',  # nom projet lisible
    'Project Contract Line',    # lien milestone (GUID)
    'Billing status',           # statut facturation
    'msdyn_salescontractlineid',# lien contract line
    'msdyn_batchnumber',        # batch
    'FnO Vendor Invoice Number',# N° facture fournisseur
    'Transaction Class',        # classe transaction
    'Quantity',                 # quantité (heures)
    'msdyn_resourcecategory',   # catégorie ressource
    'Bookable Resource',        # ressource (employé)
    # Colonnes calculées — toujours garder
    'Payment Date Finance',
    'VKI FY',
    'ProjectStatNr',
    'Expense Type D365',
}

t_act = m.Tables['msdyn_actual']
hidden_count = 0
for col in t_act.Columns:
    if col.Type.ToString() == 'RowNumber':
        continue
    if col.Name not in KEEP_VISIBLE:
        col.IsHidden = True
        hidden_count += 1

print(f"  {hidden_count} colonnes masquées dans msdyn_actual")
visible = [col.Name for col in t_act.Columns if not col.IsHidden and col.Type.ToString() != 'RowNumber']
print(f"  Colonnes visibles restantes ({len(visible)}): {visible}")

# ============================================================
# 3. GL_HEADER — masquer colonnes techniques inutiles
# ============================================================
print("\n=== GL_HEADER : masquage colonnes techniques ===")

GL_KEEP = {
    'AccountingDate',       # date comptable (relation Dates)
    'AccountingDate_Date',  # date comptable normalisée (relation Dates)
    'SubledgerVoucher',     # lien PINV → msdyn_actual
    'SourceKey',            # relation BOB_OUT
    'DocumentDate',         # date document
    'FiscalCalendarYear',   # année fiscale
    'VKI FY',              # colonne calculée
    'JournalCategory',      # type écriture
}

t_gl = m.Tables['GL_HEADER']
gl_hidden = 0
for col in t_gl.Columns:
    if col.Type.ToString() == 'RowNumber':
        continue
    if col.Name not in GL_KEEP:
        col.IsHidden = True
        gl_hidden += 1

print(f"  {gl_hidden} colonnes masquées dans GL_HEADER")

# ============================================================
# 4. BOB_OUT — masquer PostingType (technique) si souhaité
# ============================================================
# Garder tout BOB_OUT visible pour l'instant (seulement 9 colonnes)

# ============================================================
# 5. Masquer Query1 (table mystère — pas supprimer, juste cacher)
# ============================================================
m.Tables['Query1'].IsHidden = True
print("\nQuery1 masquée (à inspecter séparément)")

# ============================================================
# 6. msdyn_organizationalunit — masquer la colonne GUID brute
# ============================================================
t_org = m.Tables['msdyn_organizationalunit']
for col in t_org.Columns:
    if col.Name == 'Organizational Unit':  # garder seulement le nom lisible
        pass
    elif col.Type.ToString() != 'RowNumber':
        col.IsHidden = True

m.SaveChanges()
print("\nSaveChanges() OK — nettoyage terminé")
srv.Disconnect()
