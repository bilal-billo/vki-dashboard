# VKI Financial Dashboard — Context for Claude

## Règle absolue
**PBI = Dataverse ONLY. Ne jamais connecter SQL Server directement à Power BI.**

## Fichiers Power BI
| Fichier | Usage | Port ADOMD |
|---------|-------|------------|
| `dashboard/VKI_Financial_Dashboard/firstbuilD_powerbi_VKi14112026.pbix` | Fichier de travail actif | 49640 (détection dynamique recommandée) |
| `archive/pbix/` | Références / backups | ne pas modifier |

> Le port ADOMD change à chaque redémarrage de PBI Desktop. Toujours détecter dynamiquement via `scripts/lib/tom_client.py`.

## Sources de données
| Source | Type | URL / Connexion |
|--------|------|-----------------|
| **Dataverse** | Toutes les tables projet | `operations-vki-prod.crm4.dynamics.com` |
| **D365 Finance (F&O)** | GL_HEADER, BOB_OUT | via Dataverse (entités OData) |
| **OdooData** | T1 Manpower uniquement (97 lignes) | table Dataverse `vki_odoo_prod_datas` |

## Tables visibles dans le modèle (15)
`_Measures`, `BOB_OUT`, `Contracts`, `Customers`, `Dates`, `Employees`, `GL_HEADER`, `GL_MainAccounts`, `Invoices`, `Milestones`, `msdyn_actual`, `msdyn_organizationalunit`, `OdooData`, `Projects`, `ProjectTypes`

## Tables cachées utiles
- `Query1` = `msdyn_resourcecategorypricelevels` (taux horaires par employé — utile futur T1/T3)

## Clés de jointure importantes
- `msdyn_actual[Voucher Number]` = `GL_HEADER[SubledgerVoucher]` → préfixe "PINV"
- `BOB_OUT[GeneralJournalEntry]` → `GL_HEADER[SourceKey]`
- `Projects[Project]` = GUID D365 (ex: `1C390BCC-CA66-4935-AC83-D0F3508913B3`)
- `Projects[VKI Stat Number]` = code lisible (ex: "EAR 2529")

## Colonnes calculées clés dans msdyn_actual
- `Expense Type D365` : mapping GL account → T1/T3/T5/T6 (DAX SWITCH)
- `VKI FY` : `IF(MONTH(date) >= 10, YEAR(date) + 1, YEAR(date))` — FY Oct-Sep
- `Payment Date Finance` : date paiement réel via PINV → GL_HEADER

## Gaps connus (à résoudre)
- **Sorties magasin (PVK)** : dans OpenERP uniquement, pas dans D365 → gap ~800K sur certains projets
- **T1/T3 heures RW/VLAIO** : pas dans Dataverse (timesheets D365 = Sep 2025+ seulement)
- **OdooData** : seulement 97 lignes T1 Manpower — synchronisation incomplète

## Coefficients Claimable
| Type | GUF | ICF | Fixe |
|------|-----|-----|------|
| EU | 1.0 | 1.25 | - |
| FOD | 1.0 | 1.15 | - |
| RW | 1.65 | 1.17 | - |
| VLAIO16 | 1.62 | 1.0 | +20,000€ |
| VLAIO21 | 1.596 | 1.0 | +25,000€ |
| ESA | 1.0 | 1.0 | - |

## WANI = compte 37000000 (confirmé Sophie 10/08/2026)

## Scripts Python
Tous les scripts utilisent `scripts/lib/tom_client.py` comme base de connexion.
Ne jamais hardcoder le port — utiliser `TOMClient()` qui détecte automatiquement.

## GitHub
Repo: `bilal-billo/vki-pbi-scripts`
Branch principale: `main`
