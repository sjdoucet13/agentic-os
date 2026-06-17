# Domain — zus / app

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

An Android companion that automates tedious in-game roster/troop management for **Total Battle** via
the accessibility service: bulk delete, revive, fill formations, and a daily **SYNC** verify-and-repair.

## Glossary
- **Template** — a user-captured PNG (red_x, del_confirm, revive_potion, unit icons) matched on screen.
- **Calibration** — measured device geometry (offset, pitch, icon column, frame size, window box);
  per-device, per-resolution.
- **Formation** — ordered unit slots (`troop_NN` key, label, fill count) in `formation.json`.
- **SYNC** — the daily-driver routine that makes the in-game roster match the stored formation by the
  cheapest repair (inline repair, or hand off to Fill on mass drift).
- **Phase D (future)** — server-pushed profiles (formation / labels / entitlements) via a device-link
  token; would consume the intel/web contract. **Not yet built.**

## Related
- [[zus/app/knowledge/Architecture|Architecture]] — how the engine works today
- [[zus/intel/knowledge/Domain|intel contract]] — what a future Phase D server-push would consume
