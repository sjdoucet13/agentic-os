# mad / _shared — Now  (brand · LLC · infra — NOT compliance)

> FOCUS moment for shared Mad infra (auth, payment, deploy, brand). NOT compliance —
> regulated FFL / SOT / NFA work stays in `armory/`.

## Current focus
- **Google OAuth Brand Verification** (FREE, pre-launch must-do): submit the OAuth consent-screen branding so Google sign-in shows the verified app, not the raw Supabase URL.

## Next actions
- [ ] `auth.users` DELETE trigger + populate firstName/lastName for OAuth users (the trigger-cleanup sprint)
- [ ] Centralize admin auth — retire the inline `app/admin/layout.tsx` check, use `requireAdmin()` everywhere (two codepaths today)
- [ ] Supabase custom domain (~$35/mo, optional) + Resend Pro (2nd sender domain, when customs traffic justifies)
- [ ] Passkeys / WebAuthn (Phase 2)

_Done per commits: pre-launch lockdown sweep (Jun 9–11) — search-engine shutoff behind `PRE_LAUNCH_LOCKDOWN` (`f1615184`), foundry gate inverted to deny-by-default + `/holding` page (`d07123fa`), legacy checkout path removed (`8ae4d9b7`), PII/payment data stripped from server logs (`76fbff20`), `/api/quote` rate-limited (`ab9f3bc3`). Full backlog in `mad-custom-tx/BACKLOG.md`._

## Blocked
- _(none)_

## Parked
- Committed Chattanooga FTP credentials in `lib/r2.ts` — rotate + git-history scrub (separate remediation task; not actioned).

## Related
- [[mad/_shared/knowledge/Architecture|Architecture]] — the shared infra
- [[mad/_shared/knowledge/Gotchas|Gotchas]] — infra footguns + the secrets-in-code debt
