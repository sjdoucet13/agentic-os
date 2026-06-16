# Architecture — fugro

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

**PM_Auto** — Python/Flask local automation for Scott's Fugro USA Marine-positioning PM role.
Each of 3 PMs runs Flask **locally** (`localhost:5000`) against **one shared Microsoft Dataverse
environment** (`USA Positioning`). No central hosting. Repo: `~/projects/PM_Auto` (branch `main`).

## Stack (ground truth)
- **Python + Flask** — server-rendered HTML + Tailwind (CDN) + HTMX. **No React, no build chain.**
- **Microsoft Dataverse** (Web API) — the shared source of truth across the 3 PMs.
- **Entra ID auth via MSAL** — client-credentials flow; service principal `pm-automation-sync`.
- **Excel automation via BOTH** `openpyxl` (reads rate sheets / OIC discovery) **and**
  `pywin32` / `win32com` **COM** (writes the tripsheet `.xlsm`, drives the cost-tracker template,
  Outlook drafts). COM is required because the templates use Form-Control widgets + XLOOKUP formulas.
- **Time-ticket extraction via the Anthropic Messages API** (claude) — *not* a generic/Google
  "Vision API". [correction logged as ground truth]

## Module map
| Module | Responsibility |
|---|---|
| `dataverse_client.py` | MSAL client-credentials auth + CRUD; token-cache reuse; choice-metadata cache |
| `sync_project.py` | Greensheet XML → Dataverse Project upsert (composite key) |
| `greensheet_parser.py` | XML → dataclass; OIC-code extraction from notes |
| `rates_dataverse.py` | Phase-C1 rate reads from Dataverse |
| `cost_compute.py` | Decimal-based cost math (pure functions) — C2 Slice 1 |
| `cost_tracker.py` / `cost_tracker_state.py` | Excel-COM fill + PDF; form-state persistence to Dataverse |
| `tripsheet.py` | Excel-COM fill of the `.xlsm` (Form-Control dropdowns via `ListIndex`) + Email.Send macro |
| `timetickets.py` | Anthropic extraction of scanned time-ticket PDFs |
| `outlook_draft.py` | Draft (not send) invoice email in Outlook |
| `both_ways_gate.py` / `verify_rates.py` | Verification gates (Excel-vs-Python tie checks) |
| `create_tables.py` / `update_status_options.py` | Idempotent Dataverse metadata provisioning (`--dry-run`) |

## Data flow
Greensheet XML → `sync_project.py` → Dataverse `cr4c3_project` (key `projectnumber + subproject`)
→ Flask UI (project list/detail, cost-tracker form, tripsheet form, time-ticket review, status
actions) → Excel outputs (xlsx + PDF to `J:\…\Invoicing\`) + Outlook drafts.

## Dataverse tables
Project, Cost Tracker State, Time Ticket, Team Member, Rate / Rate Table / Client Rate Map (C1),
Transit Times, Project Note (immutable action log).
