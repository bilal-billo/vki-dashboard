---
entity: craef_vkitmbillingmilestoneses
source: Dataverse
scanned: 2026-06-18
records: 561
tags: [dataverse, billing, revenue, key-table, vki-custom]
---

# craef_vkitmbillingmilestoneses

**VKI T&M Billing Milestones — custom entity with calculated T&M billing milestone amounts per project task.**
THIS IS THE KEY REVENUE TABLE — replaces [[msdyn_contractlinescheduleofvalues]] which has 569 records but `msdyn_amount = NULL`.

## Description

Custom VKI entity storing the T&M billing milestones computed from the formulas in [[craef_vkibillingmilestoneformulas]]. Each record represents one billing milestone for one project task, with date range, milestone flag, and billing name. 561 records in production.

This entity is the primary revenue source for the Power BI T&M revenue dashboard, replacing the legacy `Qry_T_Revenues_Actuals_ALL` SQL view.

## Key Fields

| Field | Type | Sample | Notes |
|---|---|---|---|
| `craef_vkitmbillingmilestonesid` | GUID (PK) | — | Primary key |
| `craef_projectname` | Text | "TUR 2602 - TERRA Experiments" | Project display name |
| `craef_originalprojectid` | Text | "P-001481-R" | VKI project number (joins to [[msdyn_projects]]) |
| `craef_projecttaskid` | GUID (FK) | — | → [[msdyn_projecttasks]] |
| `craef_taskid` | Text | "T00001990S" | Task reference number |
| `craef_startdate` | Date | 2025-12-31 | Milestone start date |
| `craef_enddate` | Date | 2026-07-31 | Milestone end date |
| `craef_ismilestone` | Boolean | true/false | True = single payment point |
| `craef_billingmilestonename` | Text | "Poste 00020 - WP2: Turbulence Grid Design" | Billing milestone label |

## Sample Data

```
craef_projectname:         "TUR 2602 - TERRA Experiments"
craef_originalprojectid:   "P-001481-R"
craef_taskid:              "T00001990S"
craef_startdate:           2025-12-31
craef_enddate:             2026-07-31
craef_ismilestone:         true
craef_billingmilestonename: "Poste 00020 - WP2: Turbulence Grid Design"
```

## Notes

- **Amount fields not confirmed:** The initial scan sample did not show explicit amount fields. A full field list query is needed — see [[Open_Questions]].
- 561 records vs [[msdyn_contractlinescheduleofvalues]] with 569 records (8 difference — may be cancelled or excluded milestones).
- Join to [[msdyn_projects]] via `craef_originalprojectid` (text match to `msdyn_projectnumber` or similar).
- Join to [[msdyn_projecttasks]] via `craef_projecttaskid` (GUID).
- Formulas applied: [[craef_vkibillingmilestoneformulas]].
- This entity is the T&M revenue source. For Fixed Price revenue, [[msdyn_contractlinescheduleofvalues]] may be used instead.

## Open Question

Does `craef_vkitmbillingmilestoneses` contain amount fields (e.g. `craef_amount`)? The sample data did not show them explicitly. Need to query `$metadata` or full field list.

## Related Entities

- [[msdyn_projects]] — Projects (join via `craef_originalprojectid`)
- [[msdyn_projecttasks]] — Tasks (FK via `craef_projecttaskid`)
- [[msdyn_contractlinescheduleofvalues]] — Standard D365 billing milestones (parallel entity, amounts NULL)
- [[craef_vkibillingmilestoneformulas]] — Formulas used to compute amounts
- [[msdyn_actuals]] — Actual costs feeding into T&M formula (PC component)
