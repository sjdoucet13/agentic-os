# Decisions — fugro

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Dataverse as the 3-PM shared source of truth.** Already in place (`USA Positioning` env);
  avoids central app hosting — each PM runs Flask on localhost, all pointed at the same Dataverse.
- **Flask + Tailwind(CDN) + HTMX over Power Apps.** Scott explicitly rejected Power Platform; this
  stack has no build chain and iterates fast locally.
- **Keep Excel COM, don't reimplement the pricing template.** The cost-tracker workbook is
  XLOOKUP-driven and team-edited; fill its input cells programmatically and let Excel compute.
- **MSAL client-credentials now; delegated-OAuth migration pinned before any cloud hosting.**
  Application permissions are unlikely to pass Fugro IT for centralization. [AGENTS.md §9]
- **Phased build:** C1 (rate source Excel → Dataverse; verified to the cent, 631/631) — **done**.
  C2 Slice 1 (cost math → Python `Decimal`, live on-screen totals) — **in flight**. C2 Slice 2/3
  (standalone xlsx/PDF renderers; retire Excel COM) — **deferred**.
- **Composite business key for Project** (`projectnumber + subproject`) so a re-synced greensheet
  never clobbers the wrong record (most projects are sub-A; phases/re-runs are B/C…).
- **Forward-only status auto-advance**, never clobbering PM hand-edits (status set on create only).
- **No email auto-send.** Invoice/tripsheet emails are drafted into the PM's own Outlook; the PM
  reviews and sends (no shared service account in the local beta).
