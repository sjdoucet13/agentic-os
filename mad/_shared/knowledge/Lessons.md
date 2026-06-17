# Lessons — mad / _shared (brand · LLC · infra — NOT compliance)

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **Server-side revalidation on the payment path is non-negotiable.** It took the P0 fix `6b341c27`
  (reprice every checkout line server-side from DB, ignore client-supplied prices) to close the
  crafted-cart / price-tampering leak. Always reprice server-side.
- **Centralize admin auth.** Two codepaths exist today (`requireAdmin()` on routes + an inline check in
  the admin layout); they can drift. Use one helper everywhere and retire the inline check.
- **Secrets belong in env, never tracked code.** Committed credentials in `lib/r2.ts` are debt; cost =
  rotation + history audit. Env-var-first.
- **Presigned uploads want per-session token binding**, not just cartId-UUID opacity; rate limits +
  compute guards are the baseline, not the ceiling.
- **The storefront header is the seam.** Centralize its read so one missed layer can't leak the wrong
  storefront's theme or auth context.

## Related
- [[mad/_shared/knowledge/Architecture|Architecture]] — the infra these lessons came from
- [[mad/_shared/knowledge/Gotchas|Gotchas]] — the traps behind them
