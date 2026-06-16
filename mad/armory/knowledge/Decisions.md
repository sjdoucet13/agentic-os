# Decisions — mad / armory — REGULATED

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Seven distributor feeds, opt-in per vendor** — cost arbitrage (MSRP varies 20–40% across
  distributors for the same SKU), stock availability, and exclusives.
- **FFL as a required line item for firearms.** Mad Armory routes transfers through the customer's
  chosen FFL (or in-store pickup); it is not a direct-to-consumer firearms shipper. FFL data is locked
  server-side at payment time.
- **Conservative, layered firearm gating** — cart-level (`tier1==='firearms'`) + checkout-level
  (`checkStateCompliance`) + payment-time revalidation. Restricted items can't ship to certain states.
- **NMI tokenization** keeps card data off our servers.
- **OrderAuditLog** records every order mutation (actor type + timestamp) for the regulated paper
  trail.

> ⚠️ COMPLIANCE WALL: FFL / Class-02-SOT / NFA knowledge lives ONLY here
> (mad/armory). Never copy into customs or _shared.
