# Architecture — mad / armory — REGULATED

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

The Mad Armory storefront (`madarmorytx.com` / `/armory`) + firearms retail/compliance pipeline.

## Vendor sync (7 distributors)
RSR, Davidsons, Sports South, Zanders, Chattanooga, Orion, GAS. FTP/SFTP download → CSV/TSV parse →
`VendorOffer(vendor, vendorSku)` (unique, `lastHash` dedup) → taxonomy map (`CategoryMapping`, 3-tier)
→ `Product` (UPC). Stock mirror every 6h on the DigitalOcean droplet, full sync nightly. **≈31,481
live SKUs at checkout** (the upstream feed is larger; ~100K was the feed size, not live). [correction]

## Firearm-compliance surfaces
- `Product.isFirearm` + `Product.restricted_states[]`.
- **Cart gate** — `tier1 === 'firearms'` check in `context/CartContext.tsx`.
- **Checkout gate** — `checkStateCompliance()` in `app/actions/compliance.ts`, **revalidated at
  payment time** in `/api/payment/process`.
- **FFL** — `ffl_dealers` table (license #, premise, expiry, status); search modal `/api/ffl/search`;
  the chosen dealer is locked to `Order.fflId/fflName/fflLicense/fflTransferFee` (triple-gated against
  tampering). Transfer fee $24.95 online / $0 in-person pickup.

## Fulfillment routing
`lib/fulfillment-optimizer.ts` + `lib/order-routing.ts`: minimize vendor splits, balance shipping.
Firearm surcharge ($14.99 flat / free > $499); split-cart surcharge ($2.99/split); margin floor
(bump shipping if gross margin < 8%); local pickup (Katy / Fulshear / Sugar Land). Order PENDING →
NMI charge → PAID; QuickBooks sync is stubbed (TODOs).

> ⚠️ COMPLIANCE WALL: FFL / Class-02-SOT / NFA knowledge lives ONLY here
> (mad/armory). Never copy into customs or _shared.
