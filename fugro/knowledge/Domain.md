# Domain — fugro

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

The Fugro USA Marine-positioning PM workflow: eliminate re-entry of the same data across the
pending list, tripsheet, cost tracker, time tickets, and invoicing, using Dataverse as shared state.

## Glossary
- **Greensheet** — Fugro project-creator XML (e.g. `26000226.xml`). Captures billing rep, vessel,
  job description, OIC codes (in the notes/Charges section), dock/location, client AFE/PO. Minted in
  the field; flows into the PM's pending list via `sync_project.py`.
- **Tripsheet** — the Fugro `Tripsheet(PSL-F01)V2.0` `.xlsm`: header (vessel/job#/dock/departure/ETA)
  + 6-slot crew roster (role + charge-code dropdowns per person) + equipment + notes. Filled by Excel
  COM; auto-runs the Email.Send macro to draft an Outlook email for PM review.
- **Cost Tracker** — the `PM_Cost_Tracking Master Rxx.xlsx` workbook: Client Reference sheet → rate
  tables (e.g. `2025_POS_CANTIUM`) with XLOOKUP rate resolution → the `PM_Draft` input sheet with a
  31-day hour grid across Project Fees / Labor / Equipment sections.
- **Time Ticket** — a scanned field PDF (crew + equipment, daily hours by date, handwritten
  corrections, client signature). Anthropic-extracted, then PM-reviewed and saved to Dataverse.
- **OIC code** — Fugro operational-item charge code (e.g. `H0F0660` = "Job Prep – Liftboat"). One OIC
  can recur across projects; one project can use the same OIC multiple times.
- **Dock / ETA Dock / Transit times** — tripsheet fields; transit hours come from a dock-city lookup.
- **Status lifecycle** — Planned → Pending (start date set) → Active (departed/offshore) → QC
  (returned) → Awaiting Client Update / Invoiced / Problem with Payment. Forward-only.
- **Environment** — one shared `USA Positioning` Dataverse env; 3 PMs; service principal
  `pm-automation-sync` (System Customizer role).
