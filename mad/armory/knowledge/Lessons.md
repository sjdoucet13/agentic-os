# Lessons — mad / armory — REGULATED

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **Compliance audit BEFORE launch, not after.** Armory is federally regulated; shipping a firearm to
  a prohibited state = ATF liability. Don't assume the CSV restriction rules are complete — lawyer
  review is required.
- **Firearm classification needs a single source of truth** (`tier1 === 'firearms'`), not a convenience
  boolean that can drift from it.
- **Validate license expiry + state restrictions at payment time.** Lazy evaluation (only at FFL
  selection) misses licenses that go stale after the order, and re-checks the cart against the final
  ship-to state.
- **Vendor data quality = downstream data quality.** RSR / Davidsons / Sports South use different
  schemas (UPC padding, category IDs, pricing fields); the adapter/normalization layer
  (`CategoryMapping`, normalization scripts) is essential but brittle — keep it centralized.

## Related
- [[mad/armory/knowledge/Decisions|Decisions]] — the choices behind these lessons
- [[mad/armory/knowledge/Gotchas|Gotchas]] — the traps they avoid

> ⚠️ COMPLIANCE WALL: FFL / Class-02-SOT / NFA knowledge lives ONLY here
> (mad/armory). Never copy into customs or _shared.
