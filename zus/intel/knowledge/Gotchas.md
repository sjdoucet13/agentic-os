# Gotchas — zus / intel

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **`decode_rubens2.py:188` writes `r[13]` (tag) instead of `r[12]` (clanId)** to the TSV — a
  regression. Using it for the roster TSV puts "ZUS" in the clanId column → `parseInt("ZUS") → NaN → 0`
  → the `clanId === 1313036` filter excludes everyone. **Use `decode_roster.py` for roster TSVs.**
- **The 10-col TSV is a hard addon↔ingest contract** — any column drift silently corrupts the ingest.
- **Field indices are baked to the game's server protocol** — a new server field shifts every index;
  there is no version check.
- **`TITLE_SEQUENCE` is positional** — reordering it corrupts every stored title string.
- **`decode_rubens.py` is big-endian** (wrong) — exploratory only; don't use for production.
- **Capture/token is time-sensitive** (tb_walk: capture + run in the same sitting; a stale token →
  401/403, unhandled).
- **Dedup is last-wins by `gamePlayerId`** — a mid-scroll move records the final state.

## Related
- [[zus/intel/knowledge/Decisions|Decisions]] — the field [12]-not-[13] rule behind the bug
- [[zus/intel/knowledge/Architecture|Architecture]] — the scripts these traps live in
