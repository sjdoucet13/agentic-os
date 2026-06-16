---
name: status-report
description: REPORT moment — summarize a domain's current state (now.md + recent knowledge) and whether its graph is stale vs. the repo's latest commit.
status: stub
---

# status-report (STUB)

Real logic deferred. Structural placeholder for the REPORT moment.

## Intended behavior
1. For a given domain: read `now.md` and recent `knowledge/` entries.
2. Read `_system/state/graph-freshness.json`; flag any stale graph for that domain.
3. Emit: what's true now, what moved, what's blocked, what's next.
4. Report honestly — skipped/failed steps are stated, not hidden.

## Inputs (planned)
- `domain`: which domain to report on (or `all`).

## Reads
- `<domain>/now.md`, `<domain>/knowledge/*`, `_system/state/graph-freshness.json`
