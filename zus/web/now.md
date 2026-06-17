# zus / web — Now

> FOCUS moment for the zus web platform. Stay inside zus/web (+ `_shared` for clan
> concepts, `intel/` for the decode/data contract).

## Current focus
- **Site-role token bug** (FIX NEXT — live post-cutover): the switchboard mints `role` = clan role, but the `/admin` middleware gate expects a *site* role → a site super-admin who is only a member in the switched clan gets bounced. Fix: stamp an explicit `siteRole` claim on every token mint; gate `/admin` on it (back-compat fallback).

## Next actions
- [ ] Clan-permissions page (clan-scoped permission mgmt; folds in the admin entry-guard role separation)
- [ ] Player name-history (track renames for identity continuity; pairs with re-admission)
- [ ] Player-facing rebuild (user-vs-player profile split + "Gemini cringe" label redo)
- [ ] Capital-rotation full live test + the CREATE_CAPITAL gate question

_Done per commits: white-on-white admin dropdowns (`ed1492f`). In flight: the `screenshot-pipeline` score-write/OCR refactor (wrapping up). Full backlog in `nextjs-boilerplate/recon/PINNED_BACKLOG.md`._

## Blocked
- _(none)_

## Parked
- Committed `.env` with live prod secrets (Mongo / Gemini / JWT) — rotate + git-history scrub (separate remediation task; not actioned).

## Related
- [[zus/web/knowledge/Architecture|Architecture]] — the platform layers
- [[zus/web/knowledge/Gotchas|Gotchas]] — the site-role token bug + live issues
