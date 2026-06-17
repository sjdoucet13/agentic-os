# Domain — zus / web

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

The ZUS clan-intelligence platform (game: **Total Battle**). Multi-clan-capable, launched for ZUS
(`clanSlug = zus`).

- **Player** — a clan member: might, hero level, vip, `titles` (binary string from `intel`), aliases,
  coords, `lastSeen`. Keyed by stable `gamePlayerId`.
- **Score** — per-player-per-event percentage, `isCurrent` flag, dates; drives event leaderboards.
- **Event (mission)** — config: name, weight, active, allowUploads, isAggregate, componentEvents,
  Discord thread mapping.
- **Analytics** — clan might/hero snapshots; participation (event coverage %, "made" / "below"); **AWOL**
  detection (accounted-for = `isCurrent` + rawScore > 0).
- **Recruitment** — public intake form → Recruits doc → Discord notify → admin review/finalize.
- **advancedcalc** — battle-strength engine ("magic-ratio"; effective squad strength; attack-order).
- **Roles** — site role (platform-wide) vs clan role (per `accounts[]` entry). See Decisions.

## Related
- [[zus/web/knowledge/Architecture|Architecture]] — how these entities are served
- [[zus/intel/knowledge/Domain|intel contract]] — origin of the `titles` binary string on Players
- [[zus/_shared/knowledge/Domain|shared concepts]] — clanSlug + the player-identity model
