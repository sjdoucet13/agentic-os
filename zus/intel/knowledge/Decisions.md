# Decisions — zus / intel

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Filter by `clan_id` (field `[12]`), NOT the clan tag (field `[13]`).** The tag "ZUS" is worn by 3
  clans; only the numeric, server-assigned `clan_id` is unique. `REAL_ZUS_CLAN_ID = 1313036`
  (`roster-capture-ingest.ts:31`).
- **Stable identity via `gamePlayerId`** (`tb:<digits>`): match by id, fall back to alias-aware name,
  then back-fill the id — rename-proof.
- **Titles as a positional binary string** (`buildTitleSequence` → e.g. `"1,0,1,0,0"`) to reuse the web
  platform's `TitleConfig` bonus path; this is the origin of the web `Players.titles` / `titlesString`.
- **Hand-rolled LE-MessagePack** (stdlib only), not a dependency.
- **`decode_roster.py` + `roster-capture-ingest.ts` are the authoritative pair.** `decode_rubens2.py`
  extends capture scope but must NOT generate the roster TSV (field bug — see Gotchas).
