---
entity: cr365_vkihourlycostcalculationtypes
source: Dataverse
scanned: 2026-06-18
records: 12
tags: [dataverse, hourly-rates, formulas, vki-custom]
---

# cr365_vkihourlycostcalculationtypes

**Hourly cost calculation formulas per project type.** One record per project type (EU/COM/ESA/AFOSR/etc.), each containing the formula and its validity period.

## Description

Custom VKI entity that stores the hourly cost rate calculation formula for each project type. The formulas use parameters A, B, C, D (defined in [[cr365_vkihourlycostformulaparameters]]) which map to salary fields in [[craef_vkihourlycostratesandperiodses]]. There are 12 records, matching the 12 project types in [[cr365_vkiprojecttypeses]].

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `cr365_vkihourlycostcalculationtypeid` | GUID (PK) | — | Primary key |
| `cr365_hourlycostname` | Text | "Hourly Cost AFOSR" | Human-readable name |
| `cr365_formula` | Text | `(A * 1.585 + B * 1.3) * 12 / 1720` | The calculation formula |
| `cr365_formulaperiodstart` | Date | 2025-12-31 | Formula validity start |
| `cr365_formulaperiodend` | Date | 2027-12-30 | Formula validity end |
| `_cr365_projecttype_value` | GUID (FK) | — | → [[cr365_vkiprojecttypeses]] |

## Sample Data

```
cr365_hourlycostname:    "Hourly Cost AFOSR"
cr365_formula:           "(A * 1.585  + B * 1.3) * 12 / 1720"
cr365_formulaperiodstart: 2025-12-31
cr365_formulaperiodend:  2027-12-30
```

## Formula Explanation

The sample formula `(A * 1.585 + B * 1.3) * 12 / 1720` breaks down as:

| Component | Meaning |
|---|---|
| `A` | Monthly gross salary staff (`cr7d4_monthlygrosssalarystaff`) |
| `B` | Monthly gross salary PhD (`cr7d4_monthlygrosssalarystaffphd`) |
| `1.585` | Overhead/charge coefficient for staff (varies by project type) |
| `1.3` | Overhead/charge coefficient for PhD (varies by project type) |
| `* 12` | Convert monthly to annual |
| `/ 1720` | Standard working hours per year at VKI |

The resulting rate is the **hourly cost in EUR** for the given employee on the given project type. Coefficients differ per project type (EU regulations vs ESA vs AFOSR etc.).

## Notes

- 12 records = one formula per VKI project type.
- Formulas have a validity period (`formulaperiodstart` / `formulaperiodend`) to handle regulatory changes.
- Parameters A, B, C, D are defined in [[cr365_vkihourlycostformulaparameters]].
- The formula is evaluated by a Power Automate flow, which writes the result to `craef_calculatedhourlyrate` in [[craef_vkihourlycostratesandperiodses]].

## Related Entities

- [[cr365_vkiprojecttypeses]] — Project types (FK via `_cr365_projecttype_value`)
- [[cr365_vkihourlycostformulaparameters]] — Parameter definitions (A, B, C, D)
- [[craef_vkihourlycostratesandperiodses]] — Salary data + resulting calculated rate
