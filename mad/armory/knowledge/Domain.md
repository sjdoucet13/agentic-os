# Domain — mad / armory — REGULATED

> Domain facts, entities, glossary, and ground truth — the stable "what is true here"
> reference. Walled to this domain.

Mad Armory = firearms + accessories retail operating under **FFL / Class-02-SOT** authority (ATF
jurisdiction). Value prop = local pickup + FFL-transfer convenience against thin (~8–15%) margins.

## Glossary
- **FFL** — Federal Firearms License; the receiving dealer a firearm is transferred to. Customers pick
  one (or in-store pickup); we route the transfer.
- **Class-02-SOT** — Special Occupational Taxpayer status (NFA dealing/manufacturing).
- **NFA** — National Firearms Act items (regulated category).
- **Firearm** — federally regulated; never shipped to a consumer — transferred via an FFL or picked up
  in store. Age / 4473 handled in person.
- **Accessory** — non-regulated (holsters, optics, ammo boxes, grips); ships unrestricted.
- **Distributors** — RSR, Davidsons, Sports South, Zanders, Chattanooga, Orion, GAS (feed the catalog).
- **Restricted states** — per-item `restricted_states[]` (ammo bans, magazine caps, SBR / assault-
  weapon bans, suppressor rules) enforced at checkout.

## Related
- [[mad/armory/knowledge/Architecture|Architecture]] — how compliance is enforced in code
- [[mad/armory/knowledge/Gotchas|Gotchas]] — where the regulated edges are fragile

> ⚠️ COMPLIANCE WALL: FFL / Class-02-SOT / NFA knowledge lives ONLY here
> (mad/armory). Never copy into customs or _shared.
