# Domain — mad / customs

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

Mad Customs = made-to-order **laser engraving (CO2 + fiber), Cerakote, DTF (direct-to-film), and
fabrication**. Customer uploads art → picks a blank → sees a live preview → pays → proof approval →
revision window → production → ship.

## Glossary
- **Blank** — a JDS supplier item to be decorated (tumblers, cutting boards, mugs, apparel; ~2,077
  SKUs). Not customer-visible on its own.
- **Listing** — a saleable product referencing a blank (`sourceProductUpc`).
- **MockupTemplate** — per-listing blank image + engraving-box geometry (x/y/w/h + reference dims) +
  material profile + font/color palette.
- **Art quality lane** — GREEN / YELLOW / RED print-readiness from the Sharp DPI score.
- **Proof** — the admin-rendered preview the customer must approve before production.
- **Buy modes (roadmap)** — (1) Buy As-Is (finished goods, Phase 1), (2) Light Personalization
  (text + font), (3) Full Customize (Konva configurator) (Phases 2+).
- **Material profile** — e.g. laser_metal / laser_wood / dtf_cotton — drives the composite render tint.

## Related
- [[mad/customs/knowledge/Architecture|Architecture]] — how these entities flow through the pipeline
