# Lessons — zus / app

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **OCR read-back verification** after input (retry once, halt on mismatch) kills the "did it stick?"
  flake that naive automation never solved.
- **Escape early on a template miss** — in an ordered list a miss means the unit is off-screen; scroll
  immediately, don't burn captures searching the current frame.
- **One capture per unit + batch column OCR** for frame economy (the frame rate is the bottleneck).
- **Anti-fling swipe + end-hold** — fling happens on fast drags; hold the end position so physics
  settles before the next capture.
- **Measured geometry beats guessed viewport** — a measured visible-list window replaced guessed
  viewport geometry and removed a whole class of failures.
