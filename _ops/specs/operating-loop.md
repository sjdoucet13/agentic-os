# Operating-Loop Skill Layer — Spec

> The agentic-os runs a per-domain **operating loop** so any session (any machine, any
> time) can open, orient, work with continuous write-back, and wrap — without re-explaining
> state. This spec is the canonical reference; it was reconstructed from the build brief so
> the OS carries its own operating docs instead of depending on files outside the vault.
> It sits under the four moments in `_system/OPERATING_PROCEDURE.md` (CAPTURE / REPORT /
> RECONCILE / FOCUS) — the skills below are how those moments actually run.

## Status (rollout)

| Piece | What | Status |
|---|---|---|
| `capture` | CAPTURE — append a raw thought to a domain's `_inbox.md` | **done** (`_ops/skills/capture/`, commit `e46fb55`) |
| `domain-brief` | Orient at session open — read a domain's slice, summarize | **mad** |
| write-back rule | Standing reconcile + auto-commit instruction in each domain's `CLAUDE.md` | **mad** |
| `report` | Deliberate wrap — final reconcile, drain inbox, commit, state next | **mad** |

**Rollout rule:** prove the whole loop on **mad** first. Do NOT replicate to `zus` /
`fugro` (PM_Auto) until mad's loop is proven end-to-end. One domain at a time.

## Invariants (apply to every piece)

- **Single-writer per domain.** A skill invocation stays inside ONE domain. It never
  reads or writes another top-level domain.
- **No cross-contamination.** No bridging links/writes across top-level domains. Within
  `mad`, the `customs` / `armory` / `_shared` split must stay visible.
- **Compliance wall.** Armory FFL / Class-02-SOT / NFA knowledge lives only under
  `mad/armory/`. A brief may *surface* armory's own focus as part of mad's brief, but no
  skill writes armory regulated content into `customs` or `_shared`.
- **GateGuard stays ON.** Expect the fact-forcing gate to fire; comply per-turn, never
  disable it.
- **Git topology (confirmed, don't assume):** the **vault** is its own repo
  (`/mnt/c/Users/sdouc/projects/agentic-os`); each domain's **code** repo is separate
  (mad → `/home/sdoucet/projects/mad-custom-tx-master`, branch `working`). **Vault-state
  commits land in the vault repo on a working branch — never `main`.**

---

## 1. `domain-brief` — orient at session open

**Triggers:** session open, and on "brief" / "where are we" / "where did we leave off" /
"catch me up." Pushy on purpose — under-triggering defeats the point.

**Scope:** ONLY the named domain's vault slice. Reads:
- `now.md` across all sub-areas,
- `knowledge/` highlights (Decisions / Gotchas / Lessons),
- the last N git commits on the domain's **code** repo,
- any non-empty `_inbox.md`.

**Output:** ~5–8 sentences, **signal over completeness**:
- current focus,
- in-flight / blocked / parked,
- **what shipped since last session — from COMMITS (ground truth), not what `now.md` claims**,
- recommended next,
- any unprocessed captures sitting in `_inbox.md`.

**Self-honest staleness check (required):** if `now.md` is thin, or its last reconcile is
old, or the code repo has commits the `now.md` files don't reflect, the brief SAYS SO
("now.md doesn't mention the Jun 9–11 lockdown commits — may be behind the code; want me
to reconcile?") rather than reporting stale state as fact.

---

## 2. Continuous write-back rule — the keystone (in each domain's `CLAUDE.md`)

A standing instruction CC follows **by default**, because there is no reliable
session-close signal:

- **Reconcile `now.md` continuously as you work** — check an item off the moment it's
  done, append new items on discovery, pull the next up when focus shifts. Do NOT wait
  for session close.
- **Capture decisions / gotchas / lessons to `knowledge/` as they happen.**
- **Auto-commit vault state in small increments** to the working branch, pre-authorized
  (no per-commit confirmation).

**Hard boundary (prove it):**
- Auto-commit uses **explicit paths only** — `now.md`, `knowledge/`, `_inbox.md`.
- **NEVER** `git add -A` / `git add .`; never sweep up WIP code or untracked strays;
  never commit to `main`.
- Proof obligation: with a throwaway code change present in the repo, a vault-reconcile
  commit must NOT include it. Demonstrated by path-explicit `git add`.

---

## 3. `report` — deliberate wrap

**Triggers:** "report" / "wrap" / "wrap up" / "end session."

**Does:** summarize the session → final `now.md` reconcile (catch anything continuous
write-back missed) → promote any `_inbox.md` items into `knowledge/` and **empty the
inbox** → commit vault state (explicit paths) → state new focus + what's queued.

**Signal:** because write-back is continuous, `report` should usually find little to do.
If it finds a lot unreconciled, it **flags that the continuous rule isn't firing** — that's
a real signal, not a quiet fix.

---

## Proving the loop (acceptance)

End-to-end on mad: **brief** at open → make a change + a **capture** → confirm continuous
**reconcile / auto-commit** (path-explicit, no code/strays) → **report** to wrap.
