# Gotchas — zus / _shared (clan domain · clanSlug — protocol lives in intel/)

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **Don't identify the clan by its in-game tag.** The tag "ZUS" is worn by multiple clans; the unique
  key is the numeric `clan_id` (on decode/ingest — see `intel/`) and `clanSlug` (on the platform).
- **`clanSlug` is lowercase-normalized** — always go through `getClanQuery()`; don't hand-build clan
  filters.
- **Names are not identity.** Use `gamePlayerId`; a rename without identity continuity splits a
  player's history (see the wolf-stone rename incident in `web/`).

## Related
- [[zus/_shared/knowledge/Architecture|Architecture]] — the identity / isolation model
- [[zus/_shared/knowledge/Domain|Domain]] — clanSlug vs clan_id vs gamePlayerId
