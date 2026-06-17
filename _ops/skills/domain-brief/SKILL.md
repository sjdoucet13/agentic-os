---
name: domain-brief
description: >-
  Orient at the start of a work session on a domain — read that domain's vault slice and
  give a tight, honest brief of where things stand. Use this skill whenever a session opens
  on a domain, or the user says "brief", "where are we", "where did we leave off", "catch me
  up", "status", or otherwise asks to get oriented — even if they don't name the skill.
  Under-triggering defeats the purpose, so lean toward running it. Scope is ONE domain only;
  it never reads another domain.
status: active
---

# domain-brief

Give a fast, honest read of where a single domain stands, so a session can start working
immediately instead of re-deriving state. Signal over completeness — this is a briefing,
not a report.

## How to run it

1. Run the gather helper for the domain (it assembles the raw signal deterministically;
   you do the judgement):

       python3 _ops/skills/domain-brief/gather.py --domain <mad|zus|fugro|personal>

2. Read its output, then write the brief. Do NOT just echo the gather dump — synthesise.

The helper reads ONLY that domain's slice: `now.md` across all sub-areas, `knowledge/`
highlights (Decisions / Gotchas / Lessons), the last N commits on the domain's **code**
repo, and any non-empty `_inbox.md`. It writes nothing.

## The brief — ~5–8 sentences

Cover, in roughly this order, keeping it tight:
- **current focus** (per sub-area if they differ),
- **in-flight / blocked / parked**,
- **what shipped since last session — from the COMMITS** (ground truth), not what `now.md`
  claims. **Default to ONE line** in steady state — a summary count, e.g.
  *"shipped: pre-launch lockdown sweep — 7 commits, Jun 9–11."* **Expand to the itemized
  list ONLY when the commits contradict what `now.md` claims** — i.e. when you're surfacing
  drift. The point: the daily brief stays tight, and the detail appears precisely when it's
  the signal (a stale head). On a normal day, one line; on a drift day, itemize.
- **recommended next**,
- **any unprocessed captures** sitting in `_inbox.md` (offer to reconcile them).

## Be self-honest about staleness (required)

`now.md` is a curated claim, not ground truth. If it's thin, if its last reconcile is old,
or if the code repo has commits the `now.md` focus/done lines don't reflect, **say so** —
don't report stale state as fact. The gather output gives you the reconcile date, the code's
last-commit date, and a hint; but the real check is content: do the recent commits appear in
`now.md`? If not, name the gap and offer to reconcile, e.g.:

> "now.md doesn't mention the Jun 9–11 pre-launch lockdown commits — the curated head looks
>  behind the code. Want me to reconcile it before we pick the next thing?"

## Scope discipline

One domain per brief. Never pull another top-level domain's state in. Within `mad` you may
surface `armory`'s own focus as part of mad's brief, but keep the customs / armory / _shared
split visible and never move armory's regulated knowledge into customs or _shared.
