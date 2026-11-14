---
entity: craef_vkibillingmilestoneformulas
source: Dataverse
scanned: 2026-06-18
records: 7
tags: [dataverse, billing, formulas, tm, vki-custom]
---

# craef_vkibillingmilestoneformulas

**Billing milestone calculation formulas per project type.** Defines how T&M claimable costs are calculated, with 7 formula variants (EU/COM/ESA/etc.).

## Description

Custom VKI entity storing the T&M (Time & Materials) claimable cost formulas. Each record represents one formula type, combining personnel costs, consumables, travel, depreciation, and subcontracting with project-type-specific coefficients. This implements the T&M claimable cost formula from the VIBE manual.

Results feed into [[msdyn_contractlinescheduleofvalues]].`msdyn_amount` or [[craef_vkitmbillingmilestoneses]].

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `craef_vkibillingmilestoneformulaid` | GUID (PK) | — | Primary key |
| `craef_formula` | Text | `(a * PC) + (b * CO) + (c * TE) + (d * DE) + (e * SE) + (f * NumberOfManyears)` | The T&M claimable cost formula |
| `craef_formulatype` | Text | "Generic" | Formula variant name (EU/COM/ESA/Generic/etc.) |
| `craef_manualinput` | Text | null | Manual override input (if applicable) |

## Formula Explanation

The standard formula:

```
(a * PC) + (b * CO) + (c * TE) + (d * DE) + (e * SE) + (f * NumberOfManyears)
```

| Variable | Full Name | Description |
|---|---|---|
| `PC` | Personnel Cost | Staff hourly cost × hours worked |
| `CO` | Consumables | Direct consumable costs |
| `TE` | Travel Expenses | Travel and subsistence |
| `DE` | Depreciation | Equipment depreciation |
| `SE` | Subcontracting | External subcontractor costs |
| `NumberOfManyears` | Man-years | Total effort in man-years |
| `a,b,c,d,e,f` | Coefficients | Vary by project type (EU=1.0, COM/ESA/AFOSR differ) |

For most EU projects: `a=b=c=d=e=1`, `f=0` (full pass-through). For other project types, coefficients adjust for indirect/overhead rules.

## Notes

- 7 records cover the main VKI project type categories (fewer than the 12 project types because some types share the same formula).
- The formula is from the VIBE manual T&M claimable cost definition.
- PC values are sourced from [[craef_vkihourlycostratesandperiodses]] (hourly rates × hours).
- Hours come from [[vki_odoo_prod_datas]] (Odoo timesheets) or [[msdyn_actuals]].
- Calculated results are stored in [[craef_vkitmbillingmilestoneses]].

## Related Entities

- [[craef_vkitmbillingmilestoneses]] — Resulting T&M billing milestone amounts
- [[msdyn_contractlinescheduleofvalues]] — Standard D365 billing milestone entity (msdyn_amount may be populated here alternatively)
- [[cr365_vkiprojecttypeses]] — Project types driving formula selection
- [[craef_vkihourlycostratesandperiodses]] — Personnel cost source (PC component)
- [[vki_odoo_prod_datas]] — Timesheet hours source
