# Architecture — mad / customs

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

The Mad Customs storefront (`madcustomstx.com` / `/boutique`) + the made-to-order pipeline.

## Configurator + art pipeline
- **Konva configurator** (`components/customs/ConfiguratorClient.tsx`, `KonvaStage.tsx`) — renders the
  blank image + engraving box (from `MockupTemplate`), with draggable/resizable text + image elements.
- **Art upload** — presigned R2 POST (`/api/uploads/customs/presigned`), client/server Sharp encode,
  stored at `customs/designs/{cartId}/{rand}-{filename}`.
- **Scoring** — `/api/uploads/customs/score`: Sharp DPI calc → `ArtQualityLane` (GREEN/YELLOW/RED) on
  the OrderItem.
- **Composite preview** — `/api/uploads/customs/composite`: Sharp material-aware composite → drawer
  thumbnail.
- **Cart line** — `CustomsCartLine` (`kind:'customs'`) snapshots the full configurator state (text,
  image, coords, art-quality lane, proof flag).

## Product model
- **Listing** = `Product.sourceProductUpc IS NOT NULL` (refers to a Blank). **Blank** = a JDS vendor
  item (`sourceProductUpc IS NULL`; unit cost, reorder params; not customer-visible). **ProductVariant**
  maps blank → size/color/price. **MockupTemplate** holds the blank image + engraving-box geometry +
  material profile + fonts. **Collection** / **CollectionProduct** = admin-curated theme categories.
- **Catalog import** — JDS importer (`scripts/customs/jds-csv-importer.ts`, commit `6a1d0357`): CSV
  backbone + API enrich, idempotent on `VendorOffer(jds, sku)`, neutral `MC-` keys (~2,077 blanks).

## Proof workflow
`proof_required` → Order `ART_REVIEW` → admin uploads proof (`proofR2Key`) → customer approve/revise
via a 1-use token → `READY_FOR_PRODUCTION` → `IN_PRODUCTION` → `READY_TO_SHIP` → `SHIPPED`. Flat
$14.95 customs shipping.
