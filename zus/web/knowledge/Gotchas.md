# Gotchas — zus / web

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **Site-role token bug (`323d98c`, live post-cutover).** The switchboard mints the token's `role` =
  the **clan** account role, but the middleware `/admin` gate expects a **site** role → a site
  super-admin who is only a `member` in the switched clan gets bounced from `/admin`. Fail-closed (UX
  bug, not a breach). Fix: add an explicit `siteRole` claim to every token mint and gate on it (with a
  back-compat fallback to `role` for in-flight tokens).
- **White-on-white native `<select>` dropdowns** (post-cutover, dark theme) — fixed via explicit
  `color-scheme: dark` + select/option theming.
- **`characterMap` vs `accounts[]` drift.** The legacy clan→playerName shim can drift from the
  source-of-truth `accounts[]`; the migration is confirmed a near-no-op; collapsing to accounts-only is
  deferred until the cutover is proven stable (keeps rollback viable).
- **`.env` is committed with live prod secrets** (Mongo prod URI + password, `GEMINI_API_KEY`,
  `JWT_SECRET`, Discord/UploadThing keys). **SECURITY — flagged in recon FINDINGS; separate remediation
  task (rotate + history scrub), not actioned in this pass.**

## Related
- [[zus/web/knowledge/Decisions|Decisions]] — the site-role vs clan-role token model behind the bug
- [[zus/web/knowledge/Architecture|Architecture]] — the middleware/auth layer involved
