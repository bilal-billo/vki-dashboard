---
entity: DEVCustomerInvoiceJournalEntries
source: F&O OData
scanned: 2026-06-18
records: 40853
tags: [fo, odata, financial, ledger, dev-entity, key-table]
---

# DEVCustomerInvoiceJournalEntries

**VKI custom F&O entity — the FULL general ledger / customer invoice journal.** 40,853 entries covering all financial transactions. Largest financial dataset found in the scan.

## Description

Custom VKI F&O OData entity (prefixed `DEV` = built by DevElite) exposing the complete customer invoice and general ledger journal. With 40,853 records, this is essentially the full accounting ledger in D365 F&O. Candidate replacement for legacy `BOB_OUT_70001`, `711 WANI FY 2022`, and general financial history tables.

**Critical question:** Peter said "use Dataverse only" — but [[craef_vkid365transactions]] in Dataverse only has 19 records. Either the Dataverse sync is not yet active, or these F&O OData entities are the intended Power BI source for financial data. **Requires clarification with Peter.**

## Key Fields

Shares the same field structure as [[DEVCostTransactionEntries]]:

| Field | Type | Sample | Notes |
|---|---|---|---|
| `dataAreaId` | Text | "vki" | Company code |
| `AccountingDate` | Date | — | Posting/accounting date |
| `Text` | Text | "Free text invoice" | Entry description |
| `TransactionCurrencyAmount` | Decimal | 1088.64 | Amount in transaction currency |
| `AccountingCurrencyAmount` | Decimal | — | Amount in EUR (accounting currency) |
| `JournalCategory` | Text | "Cust" | Journal type (Cust = Customer) |
| `PostingType` | Text | "CustBalance" | D365 posting type |
| `LedgerPostingJournal` | Text | — | Posting journal code |
| `LedgerAccount` | Text | — | Full dimension string (MainAcct~Project~Dept) |
| `JournalNumber` | Text | — | Journal reference |
| `DocumentNumber` | Text | "LSINV000001" | Invoice/document number |
| `IsCredit` | Text | "Yes" / "No" | Credit/debit indicator |
| `Project` | Text | — | Project dimension |
| `TransactionCurrencyCode` | Text | "EUR" | Currency |
| `MainAccount` | Text | — | Main account code |
| `FiscalCalendarYear` | Text | — | Fiscal year |
| `FiscalCalendarPeriod` | Text | — | Fiscal period |
| `GeneralJournalEntry` | Text | — | GJE reference |
| `SubledgerVoucher` | Text | — | Subledger voucher |
| `Vendor` | Text | — | Vendor account |
| `Customer` | Text | — | Customer account |

## Sample Data

```
Text:                     "Free text invoice"
TransactionCurrencyAmount: 1088.64
JournalCategory:          "Cust"
PostingType:              "CustBalance"
DocumentNumber:           "LSINV000001"
TransactionCurrencyCode:  "EUR"
```

## Known Journal Categories in Data

| JournalCategory | PostingType | Likely Legacy Table |
|---|---|---|
| `Cust` | `CustBalance` | Customer invoices / BOB revenue |
| `GeneralJournal` | `LedgerJournal` | General ledger / WANI |
| `Project` | `CustBalance` | Project invoices / advance payments |
| `FixedAssets` | `FixedAssetsDebit` | Fixed asset depreciation |

## Notes

- **40,853 records** — full accounting ledger. Covers all posting types.
- Filter by `JournalCategory` to extract specific legacy table equivalents:
  - `JournalCategory = "Cust"` → `BOB_OUT_70001` equivalent (customer revenue)
  - `JournalCategory = "GeneralJournal"` AND fiscal year filter → `711 WANI FY 2022` equivalent
- `LedgerAccount` format: `"MainAccount~ProjectDimension~DeptDimension~"` — parse with text splitting in Power Query.
- `DocumentNumber` format `LSINV000001` = ledger/sales invoice; `PINV000008` = project invoice.
- **Architecture decision required**: If Peter confirms F&O OData is acceptable for financial data, this is the single source for all financial analysis. If Dataverse only, DevElite needs to sync this data to Dataverse (expand [[craef_vkid365transactions]]).
- Use [[FiscalPeriods]] as the date/period reference table when building the Power BI model.

## Filtering for Legacy Table Equivalents

```powerquery
// BOB_OUT_70001 equivalent
Table.SelectRows(DEVCustomerInvoiceJournalEntries,
    each [JournalCategory] = "Cust")

// 711 WANI FY 2022 equivalent
Table.SelectRows(DEVCustomerInvoiceJournalEntries,
    each [JournalCategory] = "GeneralJournal"
    and [FiscalCalendarYear] = "2022")
```

## Related Entities

- [[DEVCostTransactionEntries]] — Filtered cost view (355 records)
- [[DEVProjectInvoiceJournalEntries]] — Project invoice view (74 records)
- [[craef_vkid365transactions]] — Dataverse equivalent (19 records — incomplete)
- [[FiscalPeriods]] — Fiscal calendar for date joins
- [[accounts]] — Customer master for joins
