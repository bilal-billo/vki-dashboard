---
entity: cr365_vkihourlycostformulaparameters
source: Dataverse
scanned: 2026-06-18
records: 4
tags: [dataverse, hourly-rates, formulas, vki-custom]
---

# cr365_vkihourlycostformulaparameters

**Parameter definitions (A, B, C, D) used in hourly cost formulas.** Small lookup table — 4 records, one per formula parameter.

## Description

Custom VKI entity that defines the parameters referenced in the hourly cost formulas stored in [[cr365_vkihourlycostcalculationtypes]]. Each parameter (A, B, C, D) maps to a specific salary or cost field in [[craef_vkihourlycostratesandperiodses]] via an option set value.

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `cr365_vkihourlycostformulaparameterid` | GUID (PK) | — | Primary key |
| `cr365_parametername` | Text | "A" | Parameter letter used in formula string |
| `cr365_fieldname` | Option Set | 4 | Maps to a field in the rates entity |

## Known Parameter Mapping (to confirm with Peter)

| Parameter | Option Set Value | Likely Field | Source |
|---|---|---|---|
| A | — | `cr7d4_monthlygrosssalarystaff` | Monthly gross salary (staff) |
| B | — | `cr7d4_monthlygrosssalarystaffphd` | Monthly gross salary (PhD) |
| C | — | TBD | Reserved / other cost component |
| D | — | TBD | Reserved / other cost component |

## Notes

- Only 4 records (A, B, C, D) — simple lookup table.
- `cr365_fieldname` is stored as an option set integer value (e.g. `4`); the mapping to actual field names in [[craef_vkihourlycostratesandperiodses]] needs to be confirmed with Peter.
- Parameters A and B are confirmed from sample data (salary fields are populated in the rates table). C and D usage is not yet confirmed.
- See [[Open_Questions]] — question on A/B parameter mapping.

## Related Entities

- [[cr365_vkihourlycostcalculationtypes]] — Formulas that use these parameters
- [[craef_vkihourlycostratesandperiodses]] — Salary source fields (A, B values come from here)
