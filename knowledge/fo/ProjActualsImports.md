---
entity: ProjActualsImports
source: F&O OData
scanned: 2026-06-18
records: 3604
tags: [fo, odata, actuals, timesheets, odoo, staging]
---

# ProjActualsImports

**Actuals import staging table — Odoo time/expense data being imported into D365 Project Operations.** 3,604 records representing the F&O side of the Odoo → D365 import pipeline.

## Description

F&O OData entity acting as the staging/import table for Odoo timesheet data flowing into D365 Project Operations. Records here are in transit between Odoo (source) and [[msdyn_actuals]] (Dataverse destination). The difference between this table (3,604) and `msdyn_actuals` (4,458) is because already-posted actuals are removed from staging.

**This is an intermediate/staging table. For Power BI, use [[msdyn_actuals]] or [[vki_odoo_prod_datas]] instead.**

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `ActualsImportId` | GUID (PK) | — | Primary key |
| `ProjectId` | Text | "P-001002-R" | VKI project number |
| `ContractId` | Text | "ORD-01224-V4D6F8" | Project contract ID |
| `ContractLineId` | Text | "L-001020-J" | Contract line ID |
| `TransactionType` | Text | "Cost" | Type: Cost / Revenue |
| `AccountingDate` | Date | — | Accounting date |
| `Amount` | Decimal | — | Cost amount in EUR |
| `Quantity` | Decimal | — | Hours worked |
| `ResourceId` | GUID (FK) | — | → [[bookableresources]] |
| `BookableResourceName` | Text | — | Employee name |
| `ExternalOriginReference` | Text | — | Odoo batch/import reference ID |
| `BillingType` | Text | "Chargeable" | Chargeable / Non-chargeable |
| `TransactionCurrencyId` | Text | "EUR" | Currency |
| `TransactionCategoryId` | Text | — | T1/T4/T5 category ID |
| `Status` | Text | — | Import status |
| `ProjActualsImportSync` | Text | "Yes" | Sync flag |

## Pipeline Flow

```
Odoo SQL (odoo_prod_data)
        ↓
[Import Process / Power Automate]
        ↓
ProjActualsImports (F&O staging) — 3,604 records
        ↓
[D365 Project Operations posting]
        ↓
msdyn_actuals (Dataverse) — 4,458 records
```

The difference of ~854 records between `msdyn_actuals` (4,458) and this staging table (3,604) is because posted actuals are removed from the staging table once successfully imported.

## Notes

- **Do not use for Power BI** — this is a staging/transit table. Records disappear once posted.
- The full timesheet history is in [[vki_odoo_prod_datas]] (virtual table from SQL).
- Posted actuals (in D365) are in [[msdyn_actuals]] (Dataverse, 4,458 records).
- `ExternalOriginReference` = Odoo batch ID, useful for debugging import issues.
- `BillingType = "Chargeable"` means hours count toward billable project cost.
- `TransactionCategoryId` maps to T1 (Manpower), T4 (Consumables), T5 (Travel) — see [[msdyn_transactioncategories]].

## Related Entities

- [[msdyn_actuals]] — Dataverse destination (4,458 records — use this for Power BI)
- [[vki_odoo_prod_datas]] — Full Odoo history in Dataverse virtual table (use this for complete history)
- [[bookableresources]] — Employee resources (FK via `ResourceId`)
- [[msdyn_transactioncategories]] — T1/T4/T5 categories
