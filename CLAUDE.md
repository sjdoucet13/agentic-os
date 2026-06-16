# agentic-os — Root Router (Kernel)

This file is the **kernel** of the agentic OS. Claude reads it at session start and
uses it to route work into the correct **domain**. Keep it small, declarative, and
inspectable — routing lives in markdown tables here, not in code.

This is **one Obsidian vault**. Domain isolation is enforced by the **rules in this
file and the per-domain `CLAUDE.md` routers** — not by separate vaults. A
cross-domain contamination is therefore *possible* to write, which is deliberate: a
violation should be **visible in the graph**, not silently impossible.

---

## Topology (WSL / Obsidian)

- The vault lives on the **WSL Linux filesystem** at `~/projects/agentic-os`
  (NOT under `/mnt/c/`). All git, hooks, and agent file operations run natively in WSL.
- **Obsidian** (the Windows app) opens this same folder over the network path
  `\\wsl.localhost\Ubuntu\home\<user>\projects\agentic-os`.
- Consequence: never assume a Windows path internally. Author with POSIX paths.
  Obsidian is a *viewer/editor over* the Linux files, not the source of truth for paths.

---

## The Four Layers (Chase AI "Agentic OS" model)

| Layer | What it is | Where it lives |
|---|---|---|
| **Domains** | Areas of work, each with walled knowledge | `fugro/`, `mad/`, `zus/`, `personal/` |
| **Skills** | Reusable tasks | `_ops/skills/` |
| **Automations** | Skills bound to triggers | `_ops/automations/` |
| **Dashboard** | The view + one-click triggers | `_system/dashboard/` |

---

## Domain Registry

| Domain | Path | Scope | Skills/Automations? | Graph |
|---|---|---|---|---|
| `_system` | `_system/` | Vault infrastructure: dashboard, operating procedure, machine state, roadmap | meta only | — |
| `_ops` | `_ops/` | Reusable **skills** and **automations** shared across domains | this is where they live | — |
| `fugro` | `fugro/` | The Fugro work domain | yes | — |
| `mad` | `mad/` | Mad LLC — **two sub-areas**: `customs/` and `armory/` (see `mad/CLAUDE.md`) | yes | `_graphs/mad-custom-tx/` |
| `zus` | `zus/` | The zus-legacy project (`nextjs-boilerplate`) | yes | `_graphs/zus-legacy/` |
| `personal` | `personal/` | Personal reference knowledge — **knowledge-only** | **NO** skills/automations | — |

> Ground-truth knowledge for `fugro`, `mad`, and `zus` is populated in a **separate
> recon pass** against the live repos. Until then, `knowledge/` holds empty templates,
> not facts. Do not invent domain facts here.

---

## THE NO-CONTAMINATION LAW

1. **Each domain is walled.** A domain's notes, links, and skills reference **only**
   that domain. Do not bridge domains with `[[links]]`, embeds, or shared files.

2. **The only sanctioned cross-cutting hub is `mad/_shared/`** — and it is internal to
   `mad`, not a bridge between top-level domains. It holds genuinely shared Mad LLC
   things (brand, LLC entity, shared infra/repo). It does **NOT** hold compliance.

3. **`mad` is the one relaxed boundary.** `customs/` and `armory/` are **sub-areas of
   one domain**, not separate domains, because they share the LLC, the brand palette,
   and the `mad-custom-tx` repo. The split must stay **visible** — see `mad/CLAUDE.md`.

4. **COMPLIANCE WALL (critical).** Armory's FFL / Class-02-SOT / NFA regulatory
   knowledge is a different legal surface. It must **NOT** leak into `customs/`, and
   must **NOT** live in `mad/_shared/`. It lives only under `mad/armory/`.

5. **If you must reference another domain, stop and ask.** Surface the cross-domain
   need to the user rather than silently writing a bridging link. A contamination is a
   reportable event, not a convenience.

---

## Generated vs. Authored (physical split)

- **`_graphs/` is generated, READ-ONLY, and never hand-edited.** It holds Graphify
  output. Re-running graphify **overwrites** it. Authored knowledge never lives here.
- Domains *reference* graphs (by path); the dashboard *links* to them. Nothing writes
  into `_graphs/` except Graphify.

## Machine-Written State

- **`_system/state/` is machine-written ONLY.** Freshness timestamps, last-run data,
  graph-staleness flags. No authored/human content goes here. It powers dashboard
  rhythm/momentum stats and "is this graph stale vs. its repo's latest commit?" checks.

---

## Navigation Rules (routing)

1. Identify the domain from the user's request (work area, repo, or topic).
2. Open that domain's `CLAUDE.md` router and follow its scope + isolation rules.
3. Read the domain's `now.md` for current focus before acting.
4. Keep all writes **inside that domain**. Knowledge accrues in the domain's
   `knowledge/` under the Architecture/Decisions/Lessons/Domain/Gotchas structure.
5. For a reusable task, route through `_ops/skills/`. For anything scheduled or
   event-bound, see `_ops/automations/triggers.md`.
6. Follow the **operating procedure** for the 4 moments (CAPTURE / REPORT /
   RECONCILE / FOCUS): see `_system/OPERATING_PROCEDURE.md`.

---

## Roadmap (deferred — not built yet)

See `_system/roadmap/` for the deferred build items (Graphify install + per-repo
hooks, dashboard Node server, rhythm/momentum stats, atomic writes + restart-safe
server hardened against the ROG box's `nvlddmkm.sys` GPU crashes).
