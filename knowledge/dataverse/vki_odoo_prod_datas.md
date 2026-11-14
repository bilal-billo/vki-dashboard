---
entity: vki_odoo_prod_data
source: Dataverse prod (virtual table → SQL odoo_prod_data via on-premise gateway)
scanned: 2026-06-18
records: full history (virtual — $count not supported)
tags: [dataverse, virtual-table, timesheets, key-table]
---

# vki_odoo_prod_datas

**Description:** Virtual table in Dataverse that wraps the SQL `odoo_prod_data` table via the on-premise Microsoft Data Gateway. This is the **primary timesheet and cost table** for Power BI. Replaces the legacy direct SQL connection to `HYPERWIN2\VKISQL`.

**API collection:** `vki_odoo_prod_datas`
**Type:** Virtual table (connected to on-premise SQL via data gateway)
**Source SQL table:** `odoo_prod_data` on `HYPERWIN2\VKISQL`, database `odoo_flat`

---

## Why this table matters

This single table replaces THREE legacy sources:
1. `odoo_prod_data` (SQL) — raw timesheets
2. `BLMD_EXCEL` — hourly rates (the join is no longer needed — `vki_amount` is pre-calculated)
3. `CLAIMABLE_EXCEL` — overhead coefficients (absorbed into Power Automate)

It also replaces the SQL view `Qry_Hourly_Rates_Project_Actual` which computed `Amount` and `Amount_OH`.

---

## Key fields

| Field | Example | Maps to old |
|---|---|---|
| `vki_odoo_prod_dataid` | GUID | — |
| `vki_employee` | "Paris Sebastien" | `User` |
| `vki_matricule` | "408" | was the JOIN key to BLMD (no longer needed) |
| `vki_email` | "sebastien.paris@vki.ac.be" | — |
| `vki_hours` | -2.0 (negative in Odoo) | `Hours` (negate in DAX) |
| `vki_amount` | 198.76 | `Amount` (pre-calculated cost) |
| `vki_analyticjournal` | "T1 Manpower" | `Cost Category` |
| `vki_date` | "2026-05-21" | `Date` |
| `vki_period` | "5/2026" | period label |
| `vki_project` | "ARR 2209 - MIMOSA" | project name (denormalized) |
| `vki_projectnumber` | "P-001010-B" | D365 project number |
| `vki_projectid` | GUID | FK → [[msdyn_projects]] |
| `vki_taskid` | GUID | FK → [[msdyn_projecttasks]] |
| `vki_taskname` | "ARR 2209-WP0" | task name |
| `vki_tasknumber` | "T00001049Y" | task number |
| `vki_state` | "done" | timesheet state |
| `vki_sheetid` | 123359 | Odoo timesheet ID |
| `vki_externalprimarykey` | 262840 | Odoo primary key |
| `vki_uid` | 2013696 | Odoo user ID |
| `vki_description` | "Paris Sebastien" | `Description` |
| `vki_financialaccount` | "82011010 Paris Sebastien" | `Financial Account` |
| `vki_document` | 0 | `Document` |
| `vki_bobjournal` | 0 | BOB journal reference |
| `vki_timeoff` | 0 | leave indicator |
| `vki_leaveid` | null | leave reference |
| `vki_group` | null | group |
| `vki_processedpo` | null | processed PO |

---

## Notes

- `vki_hours` is NEGATIVE in Odoo (sign convention). Use `ABS([vki_hours])` or `[vki_hours] * -1` in DAX.
- `vki_amount` already includes the cost calculated by Odoo/SDworx — this is the Direct Cost per timesheet line. No multiplication by hourly rate needed in Power BI.
- `Amount_OH` (overhead uplift) from the old system: not yet available. Pending `craef_calculatedhourlyrate` population by Power Automate flows.
- The `vki_projectid` and `vki_taskid` GUIDs link directly to D365 entities — can be used as relationship keys in the Power BI data model.
- Virtual tables in Dataverse don't support `$count` — record count returns -1. The actual data volume = same as SQL `odoo_prod_data` (52K+ rows, 2017 → present).

---

## Links

- [[msdyn_projects]] — join via `vki_projectid`
- [[msdyn_projecttasks]] — join via `vki_taskid`
- [[craef_vkihourlycostratesandperiodses]] — future hourly rate source
- [[SQL_Views_to_D365]] — full mapping from old SQL view
- [[Build_Readiness]]
