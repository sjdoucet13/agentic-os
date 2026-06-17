---
name: report
description: >-
  Deliberately wrap a work session on a domain. Use whenever the user says "report",
  "wrap", "wrap up", "end session", "let's stop here", "that's it for today", or otherwise
  signals they're closing out — even if they don't name the skill. It does the close-out
  reconcile that continuous write-back can't guarantee (there's no reliable close signal):
  final reconcile, drain the inbox into knowledge, commit, state what's next. One domain.
status: active
---

# report

The deliberate end-of-session wrap for ONE domain. Continuous write-back (the standing rule
in the domain's `CLAUDE.md`) keeps state current *as you go*; `report` is the intentional
checkpoint that catches anything it missed and drains the inbox so the next session opens
clean.

> Not to be confused with the on-demand status read (`status-report`, currently a stub).
> `report` is specifically the close-out wrap.

## Steps

1. **Summarize the session** — what you did, what moved, what shipped. Short and honest.
2. **Final `now.md` reconcile** — per sub-area, check off completed items, append anything
   discovered, re-point focus if it shifted. Catch whatever continuous write-back didn't.
3. **Drain the inbox** — for each non-empty `_inbox.md`, promote each capture into the
   right `knowledge/` file (Decisions / Gotchas / Lessons / Domain / Architecture) in the
   SAME sub-area, then remove the promoted bullets so the inbox is empty. Armory captures
   stay in armory (compliance wall).
4. **Commit vault state** — explicit paths only (`now.md`, `knowledge/`, `_inbox.md`),
   working branch, never `-A`, never code, never `main` (see the domain `CLAUDE.md`
   boundary). Small, clear commit.
5. **State next** — the new current focus + what's queued, so the next session's
   `domain-brief` opens on a true head.

## The "is the loop firing?" signal — don't skip it

Because write-back is continuous, `report` should usually find **little to do**: a couple
of check-offs, an empty or near-empty inbox. If instead it finds a LOT unreconciled — many
stale items, a full inbox, focus far from reality — that's a real signal that **the
continuous write-back rule isn't firing**. Say so plainly; it's a process problem to
surface, not a mess to quietly clean up. A heavy `report` means the loop is broken upstream,
and that's worth more than the tidy-up itself.
