# Architecture — zus / intel

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

Standalone reverse-engineering + decode **tooling** for ZUS data in **Total Battle**. NOT a deployed
app — local scripts Scott runs. **Guardrail: this knowledge captures the decode CONTRACT + constants
only — never the ingest script's DB credentials / connection strings.**

## Sources
`~/projects/mitmproxy/` (Scott's own scripts — NOT the mitmproxy library; loose files, not a git repo):
- **`decode_roster.py`** — AUTHORITATIVE mitmproxy addon. Hand-rolled **LE-MessagePack** decoder
  (`LEUnpacker`); decodes the captured `rubens-realm` response into a **23-field player struct**;
  writes the canonical **10-col TSV** (`rubens_roster.tsv`).
- **`roster-capture-ingest.ts`** — PRODUCTION TypeScript ingest (Node + MongoDB). Parses the TSV,
  dedups, filters by `clan_id`, upserts the web platform's `Players`. The intel→web bridge.
- `decode_rubens2.py` — extended capture (rosters + rubens-rating + asset/CDN + request bodies),
  LE-msgpack. ⚠️ has a field bug (see Gotchas).
- `decode_rubens.py` — exploratory, **big-endian** (wrong); debug dump only.

`~/projects/TBScores/tb_capture/tb_walk.py` — a parallel standings/ladder scraper (LE-msgpack) that
filters by a hardcoded ZUS **UID roster** (`if u in ZUS`, ~98 uids) and exports ladder CSVs; it carries
**no** clan_id/title contract. Has a `BURNER_UIDS` guard (refuses to run with a real account's token).

## Protocol
Little-endian MessagePack, hand-rolled (`int.from_bytes(..., "little")`). Input = mitmproxy intercept
saved as `rubens_raw/*.hex`; length-prefixed frames `[uint32 LE len][uint32 LE ?][msgpack]`.

## Data flow
mitmproxy capture (`.hex`) → `decode_roster.py` (decode → 10-col `rubens_roster.tsv`) →
`roster-capture-ingest.ts` (dedup by `gamePlayerId` → filter `clanId === 1313036` → upsert the
platform's `Players` with the title sequence + computed bonus) → web platform. Designed to run from a
web admin handler.

## Related
- [[zus/intel/knowledge/Domain|Domain]] — the 23-field struct, clan_id, title map, TSV schema
- [[zus/intel/knowledge/Decisions|Decisions]] — why field [12] not tag [13]
- [[zus/intel/knowledge/Gotchas|Gotchas]] — the decode_rubens2.py:188 bug
- [[zus/web/knowledge/Architecture|web platform]] — where this ingest lands (the intel→web bridge)
