---
entity: FiscalPeriods
source: F&O OData
scanned: 2026-06-18
records: 224
tags: [fo, odata, date-table, calendar, reference]
---

# FiscalPeriods

**Fiscal calendar periods — candidate DATE TABLE for Power BI.** 224 records covering approximately 18–19 years of monthly fiscal periods.

## Description

F&O OData entity exposing the D365 fiscal calendar. Contains all accounting periods with start/end dates, fiscal year, period name, and quarter. With 224 records at 12 periods/year, this covers roughly 18–19 years of calendar history (~2007–2025 or similar range).

This replaces the missing `Dates` table from the legacy SQL Power BI model. Alternative approach: create a DAX date table directly in Power BI.

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `Calendar` | Text | — | Fiscal calendar name |
| `FiscalYear` | Text | — | Fiscal year (e.g. "2026") |
| `StartDate` | Date | — | Period start date |
| `EndDate` | Date | — | Period end date |
| `PeriodName` | Text | — | Period label (e.g. "Jan 2026", "Period 1") |
| `Quarter` | Text | — | Quarter (Q1/Q2/Q3/Q4) |

## Notes

- 224 records ÷ 12 months/year ≈ 18.7 years of data.
- Use as the date dimension in the Power BI star schema to connect all fact tables.
- Join key: match `StartDate`/`EndDate` to `AccountingDate` in [[DEVCustomerInvoiceJournalEntries]], [[DEVCostTransactionEntries]], [[msdyn_actuals]], [[vki_odoo_prod_datas]].
- **Alternative**: If F&O OData is not used for Power BI, create a DAX date table (standard practice, no data gateway needed):

```dax
Dates = CALENDAR(DATE(2010,1,1), DATE(2030,12,31))
```

Then add columns for Year, Month, Quarter, FiscalYear via calculated columns.

- `PeriodName` matches the `vki_period` field format in [[vki_odoo_prod_datas]] (e.g. "5/2026" — check format alignment).

## Power BI Usage

If using this entity as the date table:
1. Load via F&O OData connector (same gateway as other DEV* entities).
2. Mark as Date Table in Power BI Desktop (using `StartDate` or `EndDate`).
3. Create relationships to fact tables on `AccountingDate` / `vki_date` / `craef_validityperiod`.

## Related Entities

- [[DEVCustomerInvoiceJournalEntries]] — Join via `AccountingDate`
- [[DEVCostTransactionEntries]] — Join via `AccountingDate`
- [[DEVProjectInvoiceJournalEntries]] — Join via `AccountingDate`
- [[vki_odoo_prod_datas]] — Join via `vki_date`
- [[msdyn_actuals]] — Join via actuals date field
