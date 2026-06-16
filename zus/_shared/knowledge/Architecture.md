# Architecture — zus / _shared (clan domain · clanSlug — protocol lives in intel/)

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

The shared **conceptual** layer for the ZUS presence. NOTE: `web` and `app` share **no code** — this
captures the concepts the platform (and `intel/`) reason about, not a shared codebase.

- **ZUS clan domain** — the game is **Total Battle**; "ZUS" is a clan. The platform is multi-clan-
  capable but launched for ZUS.
- **Identity / isolation by `clanSlug`** — the platform's real isolation key is `clanSlug` (a lowercase
  string, e.g. `zus`), enforced via `getClanQuery(clanSlug)` on every web query. This is NOT the in-game
  numeric clan id (that constant + its decode/filtering live in `intel/`).
- **Player identity model** — keyed by a stable `gamePlayerId` (e.g. `tb:44131158`), rename-proof;
  display names are mutable aliases (with rename history).
- **Pointer:** the binary protocol/decode, the numeric `clan_id`, the field indices, the title id→name
  map, and the export/ingest contract all live in **`intel/`** — not here.
