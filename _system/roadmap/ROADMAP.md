# Roadmap — Deferred (do NOT build yet)

These were explicitly deferred in the v2 build brief. The skeleton must not implement
them; this file is the placeholder so they aren't lost.

## Graphify automation
- Install Graphify.
- Add per-repo `graphify update` git **post-commit** hooks (mad-custom-tx, zus-legacy).
- On each run, write freshness back to `_system/state/graph-freshness.json`.

## Dashboard (Node server + HTML)
- Node server serving `_system/dashboard/` HTML, **Mad Customs palette**.
- Clickable **Claude Code trigger** buttons (one-click automations).
- Rhythm / momentum stats fed from `_system/state/` (derived from the 4 moments).

## Reliability hardening (important — ROG box constraint)
- The ROG box has recurring `nvlddmkm.sys` GPU crashes → unclean reboots.
- Design the dashboard server to **survive an unclean reboot**:
  - no orphaned node processes,
  - no half-written files — use **atomic vault writes** (write-temp-then-rename).

## Ground-truth population (separate pass)
- Recon sweep of the two live repos to populate **real** domain knowledge (not
  placeholders), each repo's findings kept strictly in its own domain:
  - `sjdoucet13/mad-custom-tx`  → `mad/` (local: `~/projects/mad-custom-tx`)
  - `sjdoucet13/nextjs-boilerplate` = zus-legacy → `zus/` (local: `~/projects/zus-legacy`)
- Report findings up to planning-Claude before locking them in.
