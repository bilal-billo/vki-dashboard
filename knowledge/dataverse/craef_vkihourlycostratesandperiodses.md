---
entity: craef_vkihourlycostratesandperiodses
source: Dataverse
scanned: 2026-06-18
records: 457
tags: [dataverse, hourly-rates, key-table, vki-custom]
---

# craef_vkihourlycostratesandperiodses

**Hourly cost rates per employee per validity period.**
THIS IS THE KEY TABLE FOR HOURLY RATES (referenced in Peter's email as "VKI Hourly Cost Rates and Periods").

## Description

Custom VKI entity storing the monthly gross salary data and calculated hourly cost rates for each bookable resource, per validity period. Each record represents one employee × one period combination. The calculated hourly rate (`craef_calculatedhourlyrate`) is computed by a Power Automate flow using formulas from [[cr365_vkihourlycostcalculationtypes]].

This entity replaces the legacy `BLMD_EXCEL` source that was used in the old Power BI model.

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `craef_vkihourlycostratesandperiodsid` | GUID (PK) | — | Primary key |
| `craef_resourcename` | Text | "Olivier Jadot" | Employee display name |
| `_craef_bookableresource_value` | GUID (FK) | — | → [[bookableresources]] |
| `craef_validityperiod` | Date | 2026-01-01 | Start of validity period |
| `cr7d4_monthlygrosssalarystaff` | Decimal | 5095.66 | Parameter A in formulas |
| `craef_monthlygrosssalary` | Decimal | — | Monthly gross salary (base) |
| `craef_totalyearsalarycost` | Decimal | — | Total annual salary cost |
| `craef_calculatedhourlyrate` | Decimal | NULL | Calculated by Power Automate (not yet run in prod) |
| `cr7d4_monthlygrosssalarystaffphd` | Decimal | — | Parameter B in formulas (PhD supplement) |
| `craef_totalyearcost` | Decimal | — | Total annual cost (incl. charges) |
| `cr7d4_spare1` | Decimal | — | Reserved field |
| `cr7d4_spare2` | Decimal | — | Reserved field |
| `createdon` | DateTime | — | Record creation timestamp |
| `modifiedon` | DateTime | — | Last modification timestamp |

## Sample Data

```
craef_resourcename:          "Olivier Jadot"
craef_validityperiod:        2026-01-01
cr7d4_monthlygrosssalarystaff: 5095.66
craef_calculatedhourlyrate:  NULL
```

## Notes

- `craef_calculatedhourlyrate` is **NULL** in all current prod records — the Power Automate flows that compute this field have not yet been triggered in production.
- Salary fields (`cr7d4_monthlygrosssalarystaff`, `cr7d4_monthlygrosssalarystaffphd`) map to formula parameters A and B in [[cr365_vkihourlycostcalculationtypes]].
- Parameter mapping to confirm with Peter: A = `cr7d4_monthlygrosssalarystaff`, B = `cr7d4_monthlygrosssalarystaffphd`.
- Links to employees via `_craef_bookableresource_value` → [[bookableresources]].
- Replaces legacy `BLMD_EXCEL` hourly rate source.
- See [[cr365_vkihourlycostformulaparameters]] for parameter definitions.

## Related Entities

- [[bookableresources]] — Employee resource records (FK via `_craef_bookableresource_value`)
- [[cr365_vkihourlycostcalculationtypes]] — Formulas that use these salary values
- [[cr365_vkihourlycostformulaparameters]] — Parameter definitions (A, B, C, D)
- [[cr365_vkiprojecttypeses]] — Project types driving formula selection
