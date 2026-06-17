# Lessons — mad / customs

> What was learned: what worked, what didn't, what to change next time. Append-only.
> Walled to this domain.

- **Proof approval as a gate, not optional.** It captures customer intent before production; the
  revision loop prevents waste, and OrderAuditLog tracks every revision request (a cost baseline for a
  future revision-fee model).
- **Material affects rendering.** The material profile (laser_metal, laser_wood, dtf_cotton, …) drives
  the grayscale tint in the composite — store the profile, don't hardcode substrate assumptions.
- **Blank images ≠ configurable images.** The seeded templates used catalog photos with engravings
  baked in. Procuring true blanks is a separate pass from seeding; track the image sources (vendor
  glamour shot vs true blank vs alternate views).

## Related
- [[mad/customs/knowledge/Architecture|Architecture]] — where these lessons apply
- [[mad/customs/knowledge/Gotchas|Gotchas]] — the traps they avoid
