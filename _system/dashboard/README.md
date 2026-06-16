# Dashboard — STUB (deferred)

Not built yet. See `_system/roadmap/ROADMAP.md`.

Intended (later):
- A Node server + HTML view using the **Mad Customs palette**.
- One-click **Claude Code trigger** buttons wired to `_ops/automations/`.
- Rhythm / momentum stats fed from `_system/state/` (the 4-moment cadence).
- **Restart-safe**: no orphaned node processes, atomic (temp-then-rename) writes,
  survives an unclean reboot from the ROG box `nvlddmkm.sys` GPU crashes.

This is the **view layer only** — it links to `_graphs/` (read-only) and reads
`_system/state/`. It never authors knowledge.
