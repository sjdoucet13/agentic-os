---
name: capture
description: CAPTURE moment — drop a thought, finding, decision, bug, or task into the correct domain fast, without crossing domain walls.
status: active
---

# capture

The CAPTURE moment (`_system/OPERATING_PROCEDURE.md`), implemented. Drops a raw capture
into ONE domain's append-only `_inbox.md` — fast and wall-respecting. Implementation:
`capture.py` (stdlib, no deps); this is also the exact write path the Phase 3 command
server spawns (fixed argv, no shell, no eval).

    echo "the finding" | python3 _ops/skills/capture/capture.py --domain mad/armory
    python3 _ops/skills/capture/capture.py --domain fugro --text "the finding"

## Behavior
1. Take a raw capture (text) + an **explicit** target domain from the fixed allow-list.
2. The caller (CC, or the dashboard's fixed dropdown) chooses the domain; if it's
   ambiguous, the caller resolves it FIRST — `capture.py` never guesses, and it rejects
   any domain outside the allow-list, so two domains can't be bridged.
3. Append a timestamped bullet `- [YYYY-MM-DD HH:MM] <text>` to the domain's `_inbox.md`
   (created with a header on first capture). RECONCILE later promotes inbox items into
   `knowledge/`.
4. Compliance-relevant armory items capture **only** under `mad/armory/` — enforced: the
   `mad/armory` target maps solely to `mad/armory/_inbox.md`, which carries a ⚠️ REGULATED header.

## Inputs
- `--domain`: one of fugro | mad/customs | mad/armory | mad/_shared | zus | personal
- `--text` (or stdin): the capture

## Guardrails
- Honors the no-contamination law (root `CLAUDE.md`).
- Honors the `mad` compliance wall (`mad/CLAUDE.md`).
