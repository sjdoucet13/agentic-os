# Lessons — zus / web

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **Flag-based maintenance mode** (env + cookie, Edge-safe, no DB/auth) gives an atomic freeze during
  cutover; bypass via `/maintenance-bypass?key=<secret>` (httpOnly cookie) for admin smoke-tests; the
  gate covers all pages + all `/api` (middleware short-circuits before auth/DB).
- **One clan-isolation helper** (`resolveClanRole`, fail-closed) reused everywhere beats ad-hoc
  per-route checks.
- **Best-effort diagnostic logs** (one per admin action) for the audit trail + troubleshooting.
- **Name-history for rename continuity.** The wolf-stone rename incident surfaced the need to track
  renames; pairs with the stable `gamePlayerId` identity from `intel`.
- **Separate the two role claims explicitly.** Conflating site role and clan role in one `role` claim
  caused the `/admin` bounce — name them so they can't be confused.

## Related
- [[zus/web/knowledge/Decisions|Decisions]] — the choices behind these lessons
- [[zus/web/knowledge/Gotchas|Gotchas]] — the bugs that taught them
