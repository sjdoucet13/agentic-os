# Lessons — zus / _shared (clan domain · clanSlug — protocol lives in intel/)

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **Identity by stable id beats identity by name** — renames happen; key on `gamePlayerId`.
- **Clan identity by unique id beats clan tag** — tags are shared/spoofable (see `intel/` for the
  field-level `[12]`-not-`[13]` rule).
- **Keep tooling-specific contracts out of the shared concept layer.** Share understanding, not
  implementation — web and app share no code, so `_shared` is concepts, and the decode contract is in
  `intel/`.

## Related
- [[zus/_shared/knowledge/Gotchas|Gotchas]] — the identity/clan traps these lessons avoid
- [[zus/intel/knowledge/Decisions|intel decisions]] — the field [12]-not-[13] clan-id rule
