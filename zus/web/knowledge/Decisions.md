# Decisions — zus / web

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Site-role vs clan-role token model.** Site role = top-level `Users.role`
  (super-admin / global-asset-manager / member / …); clan role = per `accounts[]` entry scoped to
  `(clanSlug, playerName)`. Login + switchboard mint a token stamped with the clan role + `clanSlug`.
- **Clan isolation by `clanSlug`** via `getClanQuery()`; multi-clan via `accounts[]`; single clan (ZUS)
  at launch.
- **Production cutover (2026-06):** clan-scoped permissions, identity unification (`accounts[]` as the
  source of truth, retire legacy `characterMap`), native admin + iframe retirement, flag-based
  maintenance mode.
- **Bundle CDN deps** (Chart.js, SheetJS) instead of runtime CDN loads.
- **OCR is score-only;** the capture-ingest path owns might / hero / titles (`strip-ocr-stat-writes`).
- **Two-phase reviewed roster commit** (preview → decide → write) for the network-capture ingest.
- **JWT `tokenVersion` revocation** — lazy invalidation on mutation (no force-logout per deploy).

## Related
- [[zus/web/knowledge/Architecture|Architecture]] — what these choices built
- [[zus/web/knowledge/Gotchas|Gotchas]] — the site-role token bug the model caused
