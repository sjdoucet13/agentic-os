# Decisions — zus / _shared (clan domain · clanSlug — protocol lives in intel/)

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Isolate the platform by `clanSlug` (string), not the in-game numeric clan id.** Multi-clan
  architecture; every web query is clan-scoped via `getClanQuery(clanSlug)`.
- **Keep the protocol/decode contract in `intel/`, not `_shared`.** The platform consumes the decode
  tooling's *export*, not the binary; the contract is tooling-specific.
- **Treat `gamePlayerId` as the stable identity; names are mutable aliases** (rename continuity).
- **`_shared` holds concepts only.** Because web and app share no code, there is no shared codebase to
  document here — only shared domain understanding.
