---
scanned: 2026-06-18
tags: [fo, odata, index]
---

# F&O OData — Entity Index

Scan date: **2026-06-18** | Source: `vki-prod.operations.eu.dynamics.com/data`
Total entities in metadata: ~4,511 | VKI DEV* custom entities: **5 found with data**

## VKI DEV* Custom Entities (built by DevElite)

| Entity | Description | Status |
|--------|-------------|--------|
| [[DEVCustomerInvoiceJournalEntries]] | **KEY**: Full accounting ledger | ✅ 40,853 records |
| [[ProjActualsImports]] | Odoo → D365 import staging | ✅ 3,604 records |
| [[DEVCostTransactionEntries]] | Cost journal with project dimension | ✅ 355 records |
| [[DEVProjectInvoiceJournalEntries]] | Project invoices / advance payments | ✅ 74 records |
| [[FiscalPeriods]] | Fiscal calendar periods (date table) | ✅ 224 records |

Note: These DEV* entities use F&O OData. Peter's instruction is "Dataverse only" — pending confirmation whether these are approved for Power BI. See [[Open_Questions]] Q5.

## Entities Revenue / WANI (trouvées 2026-06-19)

| Entity | Records | Description | Champs clés |
|---|---|---|---|
| `DocumentProjInvoiceOnAccLines` | **118** | Milestones facturés (PINV/PCRN) = Revenues Booked | TransId, InvoiceDate, SalesPrice, ProjInvoiceId, Txt |
| `DocumentProjInvoiceRevenueLines` | **22** | **"Reprise advance payment VKI" = WANI en F&O** | TransId, InvoiceDate, SalesPrice (-), ProjInvoiceId, Txt |
| `ProjRevenueProfiles` | 2 | Config revenue recognition: FixedPrice, CompletedPercentage | ProfileId, RevenueRecognitionAccountingRule |
| `DEVVendorInvoiceJournalEntries` | ? | Factures fournisseurs (achats) | AccountingDate, TransactionCurrencyAmount, JournalCategory=Purch |
| `DEVVendorPaymentsEntries` | ? | Paiements fournisseurs | AccountingDate, PostingType=VendBalance |
| `DEVBankTransactionsEntries` | ? | Transactions bancaires | AccountingDate, PostingType=Bank, LedgerPostingJournal=OPEN |
| `DEVFixedAssetsDepreciationEntries` | ? | Amortissements immobilisations | AccountingDate, PostingType=FixedAssetsCredit |

**Note jointure WANI**: `DocumentProjInvoiceRevenueLines` n'a pas de `ProjectId` direct — jointure via `ProjInvoiceId` → `DEVProjectInvoiceJournalEntries` mais celui-ci n'a pas non plus de `ProjectId`. Alternative: utiliser `cr7d4_odoo_imported_uat_data` (Dataverse) avec `analytical_journal='WANI'` — a `cr7d4_project_id` direct.

## Standard F&O Entities Probed

| Entity | Description | Status |
|--------|-------------|--------|
| [[CustomersV3]] | Customers | ✅ 1,000 records |
| [[ProjHourCostPricesV2]] | Hourly Cost Prices | ⚠️ 0 records (empty — VKI uses custom entity) |
| [[ProjectV2]] | Projects V2 | ❌ Not found / error |
| [[ProjectContractHeadersV2]] | Project Contracts | ❌ Not found / error |
| [[ProjectContractLinesV2]] | Contract Lines (budget) | ❌ Not found / error |
| [[ProjectTransactionsV3]] | Project Transactions | ❌ Not found / error |
| [[ProjActualCostsTrans]] | Actual Costs Transactions | ❌ Not found / error |
| [[ProjActualRevenueTrans]] | Actual Revenue Transactions | ❌ Not found / error |
| [[ProjectHourTransactions]] | Hour Transactions | ❌ Not found / error |
| [[ProjectBudgetLinesEntity]] | Budget Lines | ❌ Not found / error |
| [[ProjectBudgetRegisterEntity]] | Budget Register | ❌ Not found / error |
| [[ProjForecastCost]] | Forecast Cost | ❌ Not found / error |
| [[ProjForecastRevenue]] | Forecast Revenue | ❌ Not found / error |
| [[ProjectInvoiceJournalHeaderEntity]] | Invoice Journal Header | ❌ Not found / error |
| [[CustInvoiceJournalEntity]] | Customer Invoice Journal | ❌ Not found / error |
| [[ProjWIPStatementEntity]] | WIP Statement | ❌ Not found / error |
| [[RevenueRecognitionEntity]] | Revenue Recognition | ❌ Not found / error |
| [[HcmWorkerV2]] | Workers/Employees | ❌ Not found / error |
| [[GeneralJournalEntryEntity]] | General Journal Entries | ❌ Not found / error |
| [[ProjectAdvancePaymentsEntity]] | Advance Payments | ❌ Not found / error |
| [[FiscalCalendarPeriodEntity]] | Fiscal Calendar Periods | ❌ Not found / error |

## Entity Groups

### VKI Custom (DEV* — DevElite built)
- [[DEVCustomerInvoiceJournalEntries]] — Full ledger (40,853): replaces BOB/WANI SQL sources
- [[DEVCostTransactionEntries]] — Cost view (355): replaces BOB_OUT_70001
- [[DEVProjectInvoiceJournalEntries]] — Project invoices (74): replaces Advanced Payments
- [[ProjActualsImports]] — Odoo import staging (3,604): intermediate table, not for Power BI
- [[FiscalPeriods]] — Date table (224): use for time intelligence

### Standard / Reference
- [[CustomersV3]] — Customers (1,000 — pagination limit, full list in [[accounts]] Dataverse)
