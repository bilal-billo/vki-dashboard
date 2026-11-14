---
entity: DEVCostTransactionEntries
source: F&O OData
scanned: 2026-06-18
records: 355
tags: [fo, odata, financial, transactions, dev-entity]
---

# DEVCostTransactionEntries

**VKI custom F&O entity for general cost transactions from the ledger.** 355 records containing journal entries with project dimension. Likely used for BOB-style cost analysis and WANI calculations.

## Description

Custom VKI F&O OData entity (prefixed `DEV` = built by DevElite) exposing general ledger entries filtered for cost postings. Contains journal entries with project dimension in the ledger account string. This may be the replacement for the legacy `BOB_OUT_70001` SQL table used in old Power BI.

**Important:** Peter said "use Dataverse only" — check [[craef_vkid365transactions]] first. If that entity is not fully populated, this F&O entity may be needed as fallback.

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `dataAreaId` | Text | "vki" | Company code (always "vki") |
| `AccountingDate` | Date | — | Posting date |
| `Text` | Text | "Flights & Trains~EAR 2310 - DTWO EXR0000103" | Entry description (often contains project ref after `~`) |
| `TransactionCurrencyAmount` | Decimal | -854 | Amount in transaction currency (negative = cost) |
| `AccountingCurrencyAmount` | Decimal | — | Amount in EUR (accounting currency) |
| `JournalCategory` | Text | "GeneralJournal" | Journal type |
| `LedgerPostingJournal` | Text | "DIV01" | Posting journal code |
| `LedgerAccount` | Text | "61470000~P-001391-X~0010071~" | Full dimension string |
| `PostingType` | Text | "LedgerJournal" | D365 posting type |
| `JournalNumber` | Text | "GJT0012171" | Journal reference |
| `IsCredit` | Text | "Yes" / "No" | Credit/debit indicator |
| `Project` | Text | — | Project dimension value |
| `TransactionCurrencyCode` | Text | "EUR" | Currency code |
| `MainAccount` | Text | — | Main account code |
| `FiscalCalendarYear` | Text | — | Fiscal year |
| `FiscalCalendarPeriod` | Text | — | Fiscal period |
| `GeneralJournalEntry` | Text | — | GJE reference |
| `SubledgerVoucher` | Text | — | Subledger voucher |
| `Vendor` | Text | — | Vendor account (if applicable) |
| `Customer` | Text | — | Customer account (if applicable) |

## Ledger Account Format

```
"61470000~P-001391-X~0010071~"
  ^^^^^^^   ^^^^^^^^^^^  ^^^^^^^
  MainAcct  ProjectDim   DeptDim
```

The `Text` field often encodes the project reference after `~`:
```
"Flights & Trains~EAR 2310 - DTWO EXR0000103"
  ^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Description      Project reference
```

## Sample Data

```
Text:                     "Flights & Trains~EAR 2310 - DTWO EXR0000103"
TransactionCurrencyAmount: -854
JournalCategory:          "GeneralJournal"
LedgerPostingJournal:     "DIV01"
LedgerAccount:            "61470000~P-001391-X~0010071~"
PostingType:              "LedgerJournal"
JournalNumber:            "GJT0012171"
IsCredit:                 "Yes"
TransactionCurrencyCode:  "EUR"
```

## Notes

- 355 records — relatively small count. May be filtered to specific journal types or a recent period.
- `TransactionCurrencyAmount` negative = cost/debit (confirm with `IsCredit` field).
- Candidate replacement for legacy `BOB_OUT_70001` SQL table.
- See [[DEVCustomerInvoiceJournalEntries]] for the full ledger (40,853 records).
- **Architecture decision pending**: Peter's "Dataverse only" preference means [[craef_vkid365transactions]] should be the primary source. If that entity remains at 19 records, escalate to Peter/DevElite.

## Related Entities

- [[DEVCustomerInvoiceJournalEntries]] — Full customer invoice journal (40,853 records)
- [[DEVProjectInvoiceJournalEntries]] — Project invoice journal (74 records)
- [[craef_vkid365transactions]] — Dataverse equivalent (only 19 records — likely incomplete)
- [[FiscalPeriods]] — Date/period reference
