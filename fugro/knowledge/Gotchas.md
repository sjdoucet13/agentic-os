# Gotchas — fugro

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **Choice columns write integers, not labels.** Status / billing-rule / ticket-status are Choice
  (picklist) columns; on PATCH send the **integer option value** — a label string silently no-ops.
  Labels only round-trip on reads via the `@OData…FormattedValue` annotation. Resolve via
  `_find_choice_value()` before updating.
- **OIC-code whitespace in `cr4c3_notesoiccodes`.** Legacy syncs used `", "` separators; newer use
  plain `,`. `.strip()` each code before the rate-sheet lookup or the match fails **silently**.
- **Status on re-sync.** `sync_project.py` sets status to "Planned" on **create only**; updates leave
  status untouched so the PM's lifecycle moves are never clobbered. Preserve on any new sync path.
- **The cost-tracker template is position-coupled.** Cell addresses, exact section-header strings
  ("Project Fees", "Labor- Survey Personnel" — hyphen-space, not em-dash), and the 31-day grid columns
  are hardcoded in `cost_tracker.py`. Template edits must be coordinated with `TEMPLATE_RULES.md`.
- **Tripsheet dropdowns need Excel COM `ListIndex`.** The floating Form-Control dropdowns can't be set
  by openpyxl; the option lists are baked into the template and mirrored in `tripsheet.py` dicts.
- **Anthropic extraction rule: handwriting wins.** A handwritten correction over a typed value is
  authoritative (per-day hours, return date); the extraction prompt encodes this — critical on real
  tickets.
- **`both_ways_gate` soft-skips missing records** (acceptable for a spot-check gate; production code
  must NOT silently skip).
- **Invoice email is draft-not-send by design** — the PM eyeballs To/CC/attachment and sends manually
  from their own Outlook. Signature injected via the `GetInspector` trick.
- **Excel COM is synchronous on the Flask server** — a slow generation blocks the page (~30s); noted
  as a UX backlog item.
