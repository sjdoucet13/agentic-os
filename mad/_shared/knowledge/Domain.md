# Domain — mad / _shared (brand · LLC · infra — NOT compliance)

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

- **Mad LLC** — one legal entity, two storefronts/brands sharing infrastructure and the
  `mad-custom-tx` repo.
- **Mad Armory** (`madarmorytx.com`) — firearms + accessories retail. (Regulated FFL/SOT/NFA
  specifics live in `armory/`, **not here**.)
- **Mad Customs** (`madcustomstx.com`) — laser / Cerakote / DTF / fabrication, made-to-order.
  (Specifics live in `customs/`.)
- **Brand** — per-storefront themes (armory tactical dark `#09090b`; customs neon `#08080f`),
  storefront detected via `x-mad-storefront`.
- **Storefront assignment** — `User.origin` (ARMORY | CUSTOMS, write-once on first signup);
  `Order.originDomain` scopes orders and the admin dashboards.
- **Lifecycle states** (shared): orders move PENDING → PAID → fulfillment states; customs adds an
  ART_REVIEW / proof loop (see `customs/`).
