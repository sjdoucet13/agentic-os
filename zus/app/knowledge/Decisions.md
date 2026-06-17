# Decisions — zus / app

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Device-storage templates only** (no bundled game art) → a "generic macro tool" posture
  (copyright/trademark distance). All templates are user-captured PNGs.
- **Generic engine + server-pushed-profile architecture** (Phase D) — server integration is **not yet
  built**; the app is currently fully local and shares no code with web/intel.
- **SYNC rewind-to-top normalization** — fling backward to the list edge so the scan is deterministic
  from any start position.
- **Per-frame coverage logging** in SYNC — scan progress is fully reconstructable from the log.
- **Physics-filtered anchor detection** — reject template false-positives by measured travel vs
  predicted position.
- **Frame economy** — one capture per unit; the previous unit's OCR verify rides the next unit's
  location capture.
- **One routine at a time;** IME suppressed during routines (re-enabled in `finally`).

## Related
- [[zus/app/knowledge/Architecture|Architecture]] — what these choices built
- [[zus/app/knowledge/Gotchas|Gotchas]] — the constraints behind them
