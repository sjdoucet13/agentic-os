# _ops — Router (Skills + Automations)

`_ops` is the **operations** domain: the home of reusable **skills** (tasks) and
**automations** (skills bound to triggers). It is cross-cutting *infrastructure*, not a
work domain.

## Scope
- `skills/` — reusable, domain-agnostic tasks. Each runs *against* a domain but carries
  no domain knowledge of its own.
- `automations/` — bindings of skills to triggers (schedule / event / dashboard button).

## Isolation declaration
- `_ops` holds **no domain knowledge**. It does not reference fugro, mad, zus, or
  personal facts. Skills are parameterized by which domain they operate on; they do not
  embed one domain's content.
- A skill may *read/write a domain's* files when invoked for that domain, but it must
  keep each invocation inside a single domain and must honor the no-contamination law
  and the `mad` compliance wall.

## Skills
| Skill | Status | Purpose |
|---|---|---|
| `skills/capture/` | **active** | CAPTURE moment — append a thought/finding to the domain's `_inbox.md` (`capture.py`, stdlib) |
| `skills/status-report/` | stub | REPORT moment — summarize a domain's current state + graph staleness |
| `skills/graph-refresh/` | stub | Run `graphify update` for a repo, then update `_system/state/graph-freshness.json` |

## Automations
See `automations/triggers.md`. Trigger **logic** is deferred (roadmap); the binding
table is authored now so the shape is fixed.
