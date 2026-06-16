# Gotchas — mad / customs

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **MockupTemplate calibration in progress.** The 2 seeded templates (LTM7216 Polar Camel tumbler,
  GFT220 bamboo board) have baked-in sample engravings and wrong reference dimensions (set to 1024 vs
  actual 1800×1800). Source true blanks, recalibrate box coordinates, re-run the idempotent seed.
- **Presigned uploads are unauthenticated.** Only cartId-UUID opacity gates them → storage-flood +
  Sharp CPU-burn vectors. Hardened with a per-IP rate limit (20/10min) + Sharp 50MP guard
  (`f586bc1c`); PDF dropped from the presign allowlist (SVG stays). Per-cartId token binding remains a
  future escalation.
- **Customs shipping display mismatch.** Fixed to show $14.95 matching the server charge (`eef414cf`);
  the admin-configurable rate is deferred.
- **Order-confirmation email theme residue.** `OrderReceiptEmail.tsx` still renders the pre-pivot
  light/cream + orange palette, not the neon customs brand (deferred to a voice-alignment pass).
- **Collections not yet wired into discovery.** The schema + admin CRUD exist, but the
  `/boutique/collections` + `/boutique/collections/[slug]` storefront pages aren't built yet.
- **Buy-modes (2) and (3) not implemented** — Phase 1 ships Buy-As-Is only.
