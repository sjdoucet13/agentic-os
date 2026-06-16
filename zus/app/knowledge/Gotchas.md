# Gotchas — zus / app

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **Resolution change invalidates calibration** — the calibration frame size must match the live frame;
  recalibrate via the 5-tap wizard.
- **SYNC requires a measured window** — old (pre-window) calibrations halt with `NO_WINDOW //
  RECALIBRATE`.
- **Scroll stride must stay below the visible window** or units leap off-screen (`strideFor` =
  `floor(visibleRows - 0.5)`, clamped to `MAX_STRIDE_ROWS`).
- **OCR ambiguity drops unread rows** — conservative line→row attribution (unread beats misattributed).
- **Mass-drift heuristic** — if ≥3 of the first 4 readable rows drifted, SYNC emits `MASS_DRIFT` and
  chains into Fill.
- **Empty accessibility tree → halt** (`NO_NODES`) — repair needs focused nodes + `ACTION_SET_TEXT`.
- **Look-alike templates → `DUPLICATE_TARGET` halt** — capture tier badges to disambiguate.
- **Fling on fast drags** — `SWIPE_DURATION_MS = 600` (tested on tablet); anti-fling end-hold; tuning is
  manual per device from `RUN_STATS`.
