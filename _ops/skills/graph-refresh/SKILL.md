---
name: graph-refresh
description: Run `graphify update` for a repo to regenerate its read-only graph under _graphs/, then write freshness back to _system/state/graph-freshness.json.
status: stub
---

# graph-refresh (STUB)

Real logic deferred (Graphify not yet installed — see `_system/roadmap/ROADMAP.md`).
Structural placeholder.

## Intended behavior
1. For a given repo, run `graphify update` → regenerates `_graphs/<repo>/`
   (**generated, read-only**; overwrites; never hand-edited).
2. Capture the repo HEAD commit + run timestamp.
3. Write them into `_system/state/graph-freshness.json` and recompute `stale`.

## Repos / graphs
| Repo | Graph | Serves |
|---|---|---|
| mad-custom-tx | `_graphs/mad-custom-tx/` | `mad/customs`, `mad/armory` |
| zus-legacy | `_graphs/zus-legacy/` | `zus` |

## Writes
- `_graphs/<repo>/` (generated only) and `_system/state/graph-freshness.json` (machine only).
