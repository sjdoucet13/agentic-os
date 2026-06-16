# Operating Procedure — The Four Moments

The agentic OS runs on four repeating moments. They are not a pipeline; they are
postures you move between. Every session touches at least one. The dashboard's rhythm
stats are derived from how regularly these happen.

> Carried forward from the prior PoC. This is the one operating-procedure concept worth
> keeping. Everything else in v2 is a clean rebuild.

---

## 1. CAPTURE  — get it out of your head, into the right domain

**Trigger:** a thought, finding, decision, bug, or task appears.

- Write it down **immediately**, in the **correct domain**, never cross-domain.
- Raw captures land fast; precision comes later in RECONCILE. Speed > polish here.
- If it doesn't obviously belong to one domain, capture it and **flag the ambiguity** —
  do not guess a domain or, worse, bridge two.
- Compliance-relevant armory items capture **only** under `mad/armory/` (see the
  compliance wall in `mad/CLAUDE.md`).

**Skill:** `_ops/skills/capture/`

---

## 2. REPORT — surface state to the human

**Trigger:** start/end of a work block, or an explicit status request.

- Read the relevant domain's `now.md` + recent `knowledge/` entries.
- Summarize: what's true now, what moved, what's blocked, what's next.
- Never fabricate progress. If a step was skipped or a check failed, say so plainly.
- Graph staleness is part of the report: is each domain's `_graphs/` output stale vs.
  its repo's latest commit? (reads `_system/state/graph-freshness.json`).

**Skill:** `_ops/skills/status-report/`

---

## 3. RECONCILE — turn raw captures into walled knowledge

**Trigger:** captures have accumulated; periodically, or before FOCUS.

- Process raw captures into the domain's structured `knowledge/`:
  **Architecture / Decisions / Lessons / Domain / Gotchas**.
- Enforce the walls: each item stays in its domain. Catch and surface any capture that
  drifted cross-domain — reconciliation is where contamination gets caught.
- Re-run graph refresh if a repo changed (`_ops/skills/graph-refresh/`), then update
  `_system/state/graph-freshness.json`.
- Append a short reflection: what worked, what didn't, what to change.

---

## 4. FOCUS — decide the one next thing per domain

**Trigger:** ambiguity about what to do next; planning a session.

- For each active domain, set `now.md` to the single current focus + immediate next
  actions. `now.md` is the answer to "if I only touch this domain once today, what?"
- Keep focus **within** a domain. Cross-domain prioritization is a human decision, made
  explicitly — not encoded as links between domains.

---

## Invariants across all four moments

- **Walls first.** When in doubt about where something goes, the answer is "ask," not
  "bridge." A contamination should be a visible, reportable event.
- **Authored vs. generated.** Never hand-write into `_graphs/`. Never author into
  `_system/state/`.
- **Append, don't rewrite history.** Daily/log-style captures are append-only.
- **Report honestly.** Done-and-verified is stated plainly; skipped or failed is stated
  just as plainly.
