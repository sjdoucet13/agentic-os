# Lessons — fugro

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **Reuse the MSAL token cache.** A single shared `DataverseClient` per Flask process reuses its token
  across requests, saving ~2.4s/request vs a fresh token fetch.
- **Cache the master template locally.** Copy the `J:\` cost-tracker workbook to a local cache at
  startup and read the fast local copy; refresh on restart. Trade-off: rate changes apply at next
  restart, not mid-session (acceptable — rates change ~quarterly).
- **Module-level caches for rarely-changing lookups** (transit times, choice metadata) avoid N+1 reads;
  cleared only on restart.
- **Composite business keys** (`number + sub`) prevent a multi-phase/re-run greensheet from clobbering
  the wrong record.
- **Decimal cost math, never float.** Round at the billed line, then sum (don't sum then round). Carry
  a "ties-to-the-cent" check that independently recomputes the total and asserts a match — a tripwire
  for future edge cases.
- **Pure-function computation cores.** `cost_compute.compute_tracker()`, `greensheet_parser.parse_*`,
  and `cost_tracker_state.serialize_*` are I/O-free → unit-testable without mocking Dataverse, and let
  the on-screen / xlsx / PDF renderers share one math implementation.
- **Idempotent metadata scripts with `--dry-run`.** `create_tables.py` / `update_status_options.py`
  check existence before creating/modifying → safe re-runs on the shared env (where a destructive change
  hits all 3 PMs).
- **Forward-only auto-advance with a hand-edit guard** is cheap (compare current vs target in the
  lifecycle list) and prevents data loss.

## Related
- [[fugro/knowledge/Decisions|Decisions]] — the choices behind these lessons
- [[fugro/knowledge/Gotchas|Gotchas]] — the traps they avoid
