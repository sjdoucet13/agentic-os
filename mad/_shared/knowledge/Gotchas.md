# Gotchas — mad / _shared (brand · LLC · infra — NOT compliance)

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **The storefront header must flow through every layer** (pages, API, email, jobs). A dropped
  `x-mad-storefront` = wrong theme or wrong context. `proxy.ts` strips any client-supplied `x-mad-*`
  headers first (injection defense).
- **Foundry secret in query param.** Moved to the `FOUNDRY_SECRET` env var (`5df28261`), but the
  `/armory/unlock` + `/boutique/unlock` routes still accept `?dev_key=` → it lands in logs/referer.
  The httpOnly cookie is the real gate; the param is used once to set it.
- **PII in server logs (partially remediated).** Despite `f60022df`, `app/actions/auth.ts` still logs
  customer email on some auth events, and `lib/nmi-client.ts` logs the NMI auth code. Logs ship to
  Vercel function logs (~90-day retention).
- **Next 16 cookie-in-render.** Dev-key cookie writes must happen in a route handler, not during
  render (`0c766f28`).
- **TLS / Postgres SSL.** A process-wide `NODE_TLS_REJECT_UNAUTHORIZED='0'` bypass was removed
  (`ed119bb1`); SSL is now scoped to the pg pool (strip `sslmode` from the URL, `0f38cd8c`).
- **Resend send killed mid-flight.** The order-confirmation email must run via `after()` so Vercel
  doesn't kill the in-flight send (`db43c819`).
- **Committed credentials in tracked code** (`lib/r2.ts`, shared infra) — a secrets-in-code hygiene
  debt; see the recon FINDINGS security flag. **Separate remediation task — not actioned here.**

## Related
- [[mad/_shared/knowledge/Architecture|Architecture]] — the infra these traps live in
- [[mad/_shared/knowledge/Lessons|Lessons]] — patterns that defuse them
