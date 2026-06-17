# mad / customs — Now

> FOCUS moment for the Customs sub-area. Stay inside customs (+ `_shared` for brand/LLC).
> Do NOT pull in armory regulatory knowledge.

## Current focus
- **Configurator visual calibration**: the 2 seeded MockupTemplates (LTM7216, GFT220) have baked-in sample engravings + wrong reference dims (1024 vs actual 1800²) — source true blanks, recalibrate the engraving-box coords, re-run the idempotent seed.

## Next actions
- [ ] Admin-configurable customs shipping rate (flat $14.95 hardcoded today; deferred to the customs-admin build)
- [ ] Wire Collections into storefront discovery (`/boutique/collections[/slug]` pages not built)
- [ ] Customs account portal + welcome-email CTA destination

_Done per commits: shipping display/charge mismatch closed (`eef414cf`) — only the admin-rate half remains. Full backlog in `mad-custom-tx/BACKLOG.md`._

## Blocked
- _(none)_

## Related
- [[mad/customs/knowledge/Architecture|Architecture]] — the customs pipeline
- [[mad/customs/knowledge/Gotchas|Gotchas]] — the live footguns
