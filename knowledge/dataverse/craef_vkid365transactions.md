---
entity: craef_vkid365transactions
source: Dataverse
scanned: 2026-06-18
records: 19
tags: [dataverse, financial, transactions, vki-custom]
---

# craef_vkid365transactions

**Financial transactions from F&O synced into Dataverse.** Appears to be a subset/staging table of F&O ledger entries — only 19 records, suggesting pilot or test sync.

## Description

Custom VKI entity mirroring financial journal entries from D365 F&O into Dataverse. Contains ledger account, posting type, journal category, and accounting amounts. With only 19 records, this is either a pilot synchronisation or a limited staging area — the full financial data resides in F&O OData [[DEVCustomerInvoiceJournalEntries]] (40,853 records).

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `craef_vkid365transactionid` | GUID (PK) | — | Primary key |
| `craef_ledgeraccount` | Text | — | Ledger account string (MainAccount~Project~Dept) |
| `craef_journalcategory` | Text | "FixedAssets", "GeneralJournal" | Journal type category |
| `craef_postingtype` | Text | "FixedAssetsDebit", "LedgerJournal" | D365 posting type |
| `craef_accountingcurrencyamount` | Decimal | 81065.91 | Amount in accounting currency (EUR) |
| `craef_transactioncurrencyamount` | Decimal | — | Amount in transaction currency |
| `craef_accountingdate` | Date | — | Accounting date |
| `craef_journalnumber` | Text | "GJT0013934" | Journal reference number |
| `craef_subledgervoucher` | Text | — | Subledger voucher reference |
| `craef_ledgerpostingjournal` | Text | — | Posting journal reference |
| `craef_iscredit` | Boolean | — | True = credit entry |
| `craef_isCorrection` | Boolean | — | True = correction entry |
| `craef_recordid` | Text | — | Source record identifier |
| `craef_project` | Lookup | — | Project reference |

## Sample Data

```
craef_journalcategory:         "FixedAssets"
craef_postingtype:             "FixedAssetsDebit"
craef_accountingcurrencyamount: 81065.91
craef_journalnumber:           "GJT0013934"
```

## Notes

- **Only 19 records** — far below the 40,853 records in F&O [[DEVCustomerInvoiceJournalEntries]]. This is either a test/pilot sync or a specifically filtered subset.
- Peter's instruction: "use Dataverse only." If this entity is the intended Dataverse path for financial data, it needs to be populated fully by DevElite.
- The ledger account format likely follows `MainAccount~ProjectDimension~DeptDimension~` (same as F&O DEV* entities).
- May grow significantly once DevElite activates the full F&O → Dataverse sync pipeline.
- See [[Open_Questions]] for the key question on F&O OData vs Dataverse for financial data.

## Related Entities

- [[DEVCustomerInvoiceJournalEntries]] — F&O equivalent with full 40,853 records
- [[DEVCostTransactionEntries]] — F&O cost transactions (355 records)
- [[msdyn_projects]] — Project lookup
