# Architecture — zus / app

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

Android **screen-automation engine** companion for the ZUS clan (game: **Total Battle**). Repo
`~/projects/zus-legacy-companion` (branch `master`). Kotlin · Gradle 9 · minSdk 30 / target 36 ·
Android **Views** (no Compose).

## Libraries
OpenCV 4.13 (template matching) · ML Kit Text Recognition (OCR, no Play Services) ·
kotlinx-coroutines. **No network libraries** — fully local; no protocol/decode layer.

## Engine (`EngineAccessibilityService` host)
- **ScreenCapture** — accessibility-API screenshot (framework-throttled).
- **TemplateMatcher** — OpenCV grayscale `TM_CCOEFF_NORMED` against device-stored PNG templates.
- **GestureDispatcher** — accessibility gestures (anti-fling swipes, end-hold).
- **TextInput** — native `setText` (never coordinate-tapping a keyboard).
- **FieldReader** — ML Kit OCR over a measured, upscaled box (`DigitParser` for noise).

## Stores (local JSON)
CalibrationStore (device geometry) · FormationStore (unit slots) · TemplateStore (user-captured PNGs
in device storage).

## Routines + wizards
Routines: **Delete** (bottom-up), **Revive**, **Fill** (ordered fill + OCR read-back verify), **SYNC**
(verify-and-repair roster — the daily driver: rewind-to-top normalization, physics-filtered anchors,
column-batch OCR, mass-drift handoff to Fill). Wizards: WizardActivity (capture template),
GeometryActivity (5-tap calibration), FormationActivity (formation editor), RosterActivity (roster
capture).

## Related
- [[zus/app/knowledge/Decisions|Decisions]] — why device-storage templates, generic engine
- [[zus/app/knowledge/Domain|Domain]] — routines, calibration, formation, Phase D
- [[zus/app/knowledge/Gotchas|Gotchas]] — calibration + scroll + OCR fragilities
- [[zus/app/knowledge/Lessons|Lessons]] — what automation taught
