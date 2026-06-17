# Domain — zus / intel

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

- **Game:** Total Battle. **Clan:** ZUS — canonical **`clan_id 1313036`**.
- **23-field player struct** (decoded from the response): `r[1]`=gamePlayerId (`tb:…`), `r[2]`=name,
  `r[7]`=heroLevel, `r[9]`=vip, `r[10]`=might, **`r[12]`=clanId**, **`r[13]`=tag** ("ZUS"),
  `r[15]`=[kingdom, x, y], `r[19]`=titles `[[id, grant_ts], …]`.
- **Title id→name map** (`TITLE_SEQUENCE`, positional canonical order):

  | pos | id | name |
  |---|---|---|
  | 0 | 193 | honored |
  | 1 | 329 | bane of insects |
  | 2 | 206 | light keeper _(verified in-game 2026)_ |
  | 3 | 204 | flame keeper _(verified in-game 2026)_ |
  | 4 | 222 | forge master |

  `buildTitleSequence(heldIds)` → a positional binary string, e.g. `"1,0,1,0,0"`.
- **10-col TSV export** (`rubens_roster.tsv`): `gamePlayerId, name, clanId(r12), might(r10),
  heroLevel(r7), vip(r9), kingdom, X, Y, titleIds(r19)`.
- **tb_walk ladder CSVs:** `zus_rbs_ladder.csv` = `rank,name,score,instance`;
  `full_board/sweep/hunt/div` = `rank,uid,name_clan,score`.
- **tb_walk opcodes:** 24003 standings · 24001 catalog · 24002 subject standings.

## Related
- [[zus/intel/knowledge/Architecture|Architecture]] — the capture→decode→ingest data flow
- [[zus/web/knowledge/Domain|web Players]] — where `titles` (this title map) is stored on the platform
