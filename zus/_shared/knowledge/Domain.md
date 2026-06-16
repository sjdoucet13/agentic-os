# Domain — zus / _shared (clan domain · clanSlug — protocol lives in intel/)

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

- **Total Battle** — the game. **ZUS** — the clan this domain serves.
- **clanSlug** — the platform's lowercase string identifier for a clan (e.g. `zus`); the isolation key
  used by `getClanQuery(clanSlug)`.
- **clan_id** — the game's numeric clan identifier; the canonical ZUS value and its decode/filtering
  live in `intel/` (not asserted here).
- **gamePlayerId** — stable per-account id (`tb:<digits>`); the identity anchor across renames.
- **Player** — a clan member tracked on the platform (might, hero level, vip, titles, coords).
- **Titles** — in-game ranks; the id→name map and the binary `titles` string convention are defined in
  `intel/` (origin) and stored on the web platform's `Players`.
