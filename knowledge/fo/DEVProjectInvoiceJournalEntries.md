---
entity: DEVProjectInvoiceJournalEntries
source: F&O OData
scanned: 2026-06-18
records: 74
tags: [fo, odata, financial, invoices, advance-payments, dev-entity]
---

# DEVProjectInvoiceJournalEntries

**VKI custom F&O entity for project invoice journal entries.** 74 records containing advance payments and project billing transactions.

## Description

Custom VKI F&O OData entity (prefixed `DEV` = built by DevElite) exposing project-specific invoice journal entries. Sample data shows advance payments to projects (e.g. "Advance Payment PHARES"). Likely the D365 replacement for the legacy `Advanced Payments` SQL table.

**Important:** Peter said "use Dataverse only" — this F&O entity should be the fallback if advance payment data is not available in Dataverse.

## Key Fields

Shares the same field structure as [[DEVCostTransactionEntries]], plus:

| Field | Type | Sample | Notes |
|---|---|---|---|
| `dataAreaId` | Text | "vki" | Company code |
| `AccountingDate` | Date | — | Posting date |
| `Text` | Text | "Advance Payment PHARES" | Entry description |
| `TransactionCurrencyAmount` | Decimal | 71460.9 | Amount in transaction currency |
| `AccountingCurrencyAmount` | Decimal | — | Amount in EUR |
| `JournalCategory` | Text | "Project" | Journal category |
| `PostingType` | Text | "CustBalance" | D365 posting type |
| `LedgerPostingJournal` | Text | — | Posting journal |
| `JournalNumber` | Text | — | Journal reference |
| `DocumentNumber` | Text | "PINV000008" | Project invoice number |
| `ProjectCustomer` | Text | "24" | Customer account number |
| `IsCredit` | Text | — | Credit/debit indicator |
| `TransactionCurrencyCode` | Text | "EUR" | Currency |
| `MainAccount` | Text | — | Main account |
| `FiscalCalendarYear` | Text | — | Fiscal year |
| `FiscalCalendarPeriod` | Text | — | Fiscal period |
| `Vendor` | Text | — | Vendor (if applicable) |
| `Customer` | Text | — | Customer account |

## Sample Data

```
Text:                     "Advance Payment PHARES"
TransactionCurrencyAmount: 71460.9
JournalCategory:          "Project"
PostingType:              "CustBalance"
DocumentNumber:           "PINV000008"
ProjectCustomer:          "24"
TransactionCurrencyCode:  "EUR"
```

## Notes

- 74 records — small dataset, matching the limited scope of advance payment tracking.
- `PostingType = "CustBalance"` confirms these are customer balance entries (advance payment receipts).
- `DocumentNumber` format `PINV000008` = Project Invoice number in D365.
- `ProjectCustomer` = customer account number — cross-reference with [[accounts]] in Dataverse.
- Candidate replacement for legacy `Advanced Payments` SQL table.
- **Architecture decision pending**: Confirm with Peter whether this F&O entity is approved for Power BI use or if the data should come from Dataverse invoices/[[invoices]].

## Related Entities

- [[DEVCostTransactionEntries]] — Cost transactions (same structure, different filter)
- [[DEVCustomerInvoiceJournalEntries]] — Full ledger (40,853 records)
- [[invoices]] — Dataverse invoices entity (87 records — may not cover advance payments)
- [[salesorders]] — Project contracts (advance payments relate to contracts)
- [[accounts]] — Customer accounts (join via `ProjectCustomer`)
