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

# Mesures doublons à masquer dans _Measures
HIDE_MEASURES = {
    'Planned VKI',                  # = Planned Milestones
    'Total Milestones Amount',      # = Planned Milestones
    'Total Milestones Posted',      # = Approved Milestones
    'Original VKI Grant',           # = Total Budget
    'WANI Balance RT',              # = WANI Balance
    'Project Revenues RT',          # = Total Milestones Posted
    'Direct Costs D365',            # = Direct Costs msdyn D365
    'Direct Costs + VKI OH D365',   # = Direct Costs + OH msdyn D365
}

hidden = 0
for t in m.Tables:
    for ms in t.Measures:
        if ms.Name in HIDE_MEASURES:
            ms.IsHidden = True
            hidden += 1
            print(f"  Hidden: [{ms.Name}] (dans {t.Name})")

print(f"\n{hidden} mesures masquées")

# Déplacer les mesures Planning de Milestones vers _Measures pour uniformité
# (optionnel — les laisser dans Milestones est aussi valide)

# Masquer les mesures Milestones qui référencent OdooData (données incomplètes)
HIDE_ODOO_MILESTONES = {
    'Total WANI',           # OdooData[Amount] WANI — données quasi vides
    'Total Direct Costs OH', # OdooData avec logique OH — données quasi vides
    'Total Claimable',       # OdooData — données quasi vides
    'Remaining Over Time',   # utilise Total Budget - Revenues Booked
    'Revenues Booked Cumulative', # logique cumulative complexe sur OdooData
    'Remaining Budget vs Revenues Booked',  # dépend de Revenues Booked Cumulative
    'Remaining Budget vs Claimable Costs',  # dépend de Total Claimable
}

for ms in m.Tables['Milestones'].Measures:
    if ms.Name in HIDE_ODOO_MILESTONES:
        ms.IsHidden = True
        print(f"  Hidden (Milestones): [{ms.Name}]")

m.SaveChanges()
print("\nSaveChanges() OK — mesures doublons masquées")

# Résumé final
print("\n=== Mesures visibles restantes ===")
for t in m.Tables:
    visible_ms = [ms.Name for ms in t.Measures if not ms.IsHidden]
    if visible_ms:
        print(f"\n  {t.Name}:")
        for name in visible_ms:
            print(f"    [{name}]")

srv.Disconnect()
