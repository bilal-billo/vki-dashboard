---
scanned: 2026-06-18
tags: [dataverse, index]
---

# Dataverse — Entity Index

Scan date: **2026-06-18** | Source: `operations-vki-prod.crm4.dynamics.com`
Total entities with data: **26** | Custom VKI entities found: **7 new**

## Standard D365 Entities

| Entity | Description | Status |
|--------|-------------|--------|
| [[msdyn_projects]] | Projects | ✅ 528 records |
| [[salesorders]] | Project Contracts | ✅ 530 records |
| [[salesorderdetails]] | Contract Lines | ✅ 667 records |
| [[msdyn_contractlinescheduleofvalues]] | Billing Milestones | ⚠️ 569 records (msdyn_amount = NULL) |
| [[msdyn_actuals]] | Actuals (time entries) | ✅ 4,458 records |
| [[cr365_vkiprojecttypeses]] | VKI Project Types | ✅ 12 records |
| [[pricelevels]] | Pricelists | ✅ 13 records |
| [[bookableresources]] | Resources/Employees | ✅ 283 records |
| [[accounts]] | Customers/Accounts | ✅ 2,515 records |
| [[msdyn_projecttasks]] | Project Tasks (WBS) | ✅ 1,103 records |
| [[msdyn_resourceassignments]] | Resource Assignments | ✅ 1,103 records |
| [[msdyn_transactioncategories]] | Transaction Categories (T1/T4/T5) | ✅ 175 records |
| [[invoices]] | Invoices | ✅ 87 records |
| [[msdyn_expenses]] | Expenses | ✅ 601 records |
| [[msdyn_expensecategories]] | Expense Categories | ✅ 10 records |
| [[msdyn_journallines]] | Journal Lines | ✅ 1,388 records |
| [[pricelevels]] | Pricelists | ✅ 13 records |
| [[productpricelevels]] | Pricelist Items | ✅ 1 record |
| [[msdyn_organizationalunits]] | Org Units | ✅ 12 records |
| [[transactioncurrencies]] | Currencies | ✅ 177 records |
| [[msdyn_budgetlines]] | Budget Lines | ⚠️ 0 records (empty) |
| [[msdyn_paymentschedules]] | Payment Schedules | ⚠️ 0 records (empty) |
| [[msdyn_projectpricelists]] | Project Pricelists | ⚠️ 0 records (empty) |

## VKI Custom Entities (craef_ / cr365_ / vki_ prefix)

| Entity                                   | Description                                               | Status                     |
| ---------------------------------------- | --------------------------------------------------------- | -------------------------- |
| [[craef_vkihourlycostratesandperiodses]] | **KEY**: Hourly cost rates per employee per period        | ✅ 457 records              |
| [[cr365_vkihourlycostcalculationtypes]]  | Hourly cost formulas per project type                     | ✅ 12 records               |
| [[cr365_vkihourlycostformulaparameters]] | Formula parameters A, B, C, D                             | ✅ 4 records                |
| [[craef_vkibillingmilestoneformulas]]    | T&M billing milestone formulas                            | ✅ 7 records                |
| [[craef_vkitmbillingmilestoneses]]       | **KEY**: T&M billing milestones per task                  | ✅ 561 records              |
| [[craef_vkid365transactions]]            | F&O→Dataverse financial sync (pilot)                      | ⚠️ 19 records (incomplete) |
| [[vki_odoo_prod_datas]]                  | **KEY**: Odoo timesheets (virtual table via data gateway) | ✅ virtual (-1)             |
| craef_vkihistory                         | Historical snapshot 31/12/2025                            | ❌ Not in prod yet          |
| craef_vkisdworxmatricules                | SDworx employee mapping                                   | ⚠️ 0 records (empty)       |
|                                          |                                                           |                            |

## Entity Groups

### Projects & Contracts
- [[msdyn_projects]] — Projects
- [[salesorders]] — Project Contracts (filter: `msdyn_ordertype=192350001`)
- [[salesorderdetails]] — Contract Lines (`baseamount` = budget)
- [[msdyn_contractlinescheduleofvalues]] — Standard billing milestones (no amounts)
- [[craef_vkitmbillingmilestoneses]] — **VKI custom T&M billing milestones** (use this)
- [[msdyn_projecttasks]] — WBS Tasks
- [[cr365_vkiprojecttypeses]] — VKI Project Types (EU/COM/ESA/AFOSR/...)

### Financials & Actuals
- [[msdyn_actuals]] — D365 actuals (recent, 4,458 records)
- [[vki_odoo_prod_datas]] — **Full Odoo timesheet history** (virtual table)
- [[msdyn_expenses]] — Expense reports
- [[invoices]] — Customer invoices
- [[craef_vkid365transactions]] — F&O journal sync (19 records — pilot)

### Hourly Rates System
- [[craef_vkihourlycostratesandperiodses]] — Salary data per employee per period
- [[cr365_vkihourlycostcalculationtypes]] — Formulas per project type
- [[cr365_vkihourlycostformulaparameters]] — Parameters A, B, C, D
- [[craef_vkibillingmilestoneformulas]] — T&M claimable cost formulas

### Reference / Lookup
- [[pricelevels]] — Pricelists
- [[bookableresources]] — Employees/Resources
- [[accounts]] — Customers
- [[msdyn_transactioncategories]] — T1/T4/T5 categories
- [[msdyn_organizationalunits]] — Org units
- [[transactioncurrencies]] — Currencies
