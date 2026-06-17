# Lessons — zus / intel

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **clan_id beats clan tag for identity** — the tag is shared across 3 clans; filter on the unique
  numeric id (`1313036`) at field `[12]`, never the tag at `[13]`.
- **Endianness is load-bearing** — little-endian is correct; the big-endian draft (`decode_rubens.py`)
  was a dead end.
- **A documented TSV schema is the contract** between the decode addon and the TS ingest — keep them in
  sync or the ingest breaks silently.
- **Stable per-account id + alias back-fill** survives renames — don't key on names.
- **Guardrail discipline:** record the decode contract + constants in knowledge; keep the ingest's DB
  connection/credentials out (config/secret, not contract).

## Related
- [[zus/intel/knowledge/Decisions|Decisions]] — the choices behind these lessons
- [[zus/intel/knowledge/Gotchas|Gotchas]] — the traps they avoid
