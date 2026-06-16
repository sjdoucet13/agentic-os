# fugro — Domain Router

The **Fugro** work domain.

## Scope
Work, knowledge, and skills relating to Fugro. Knowledge accrues under `knowledge/`
using the Architecture / Decisions / Lessons / Domain / Gotchas structure.

> Substance is **not yet populated**. Real knowledge is added in the deferred
> ground-truth recon pass. Until then, `knowledge/` holds empty templates only — do not
> invent facts.

## Isolation declaration
- This domain references **only** Fugro. It does **not** link to, embed, or borrow from
  `mad`, `zus`, or `personal`.
- No shared hub. If something seems to belong to two domains, **stop and ask** — never
  bridge with a link.

## Layout
- `knowledge/` — walled, accumulating knowledge (5-part structure).
- `skills/` — domain-specific tasks (reusable cross-domain tasks live in `_ops/`).
- `now.md` — the single current focus + next actions (the FOCUS moment).
