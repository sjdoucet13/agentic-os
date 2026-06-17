# mad / armory — Now  ⚠️ REGULATED

> FOCUS moment for the Armory sub-area. **Compliance wall applies** (FFL / Class-02-SOT
> / NFA). Keep regulatory knowledge here only — never in customs, never in `_shared`.

## Current focus
- ⛔ **Pre-Launch Compliance Audit** (TOP PRIORITY — blocks launch): federal + state firearms + age-gating legal review. Restricted-states coverage is rules-based today, not lawyer-verified.

## Next actions
- [ ] Validate FFL `license_expiry` at checkout (can currently charge a transfer on an expired FFL)
- [ ] Complete the restricted-states coverage audit (rules-based → verify against legal requirements)
- [ ] Classify firearms off `tier1==='firearms'`, not the `isFirearm` convenience bool (drift risk)

_Done per commits: the shared pre-launch lockdown now gates the foundry storefront too — deny-by-default holding page + search-engine shutoff (`d07123fa`, `f1615184`). Earlier: admin-API auth gating (`c04f7548`, all routes `requireAdmin()`). Full backlog in `mad-custom-tx/BACKLOG.md`._

## Blocked
- _(none)_

## Related
- [[mad/armory/knowledge/Architecture|Architecture]] — the armory pipeline
- [[mad/armory/knowledge/Gotchas|Gotchas]] — compliance footguns
