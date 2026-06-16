# Gotchas — mad / armory — REGULATED

> Traps, footguns, and surprising behaviors to remember before they bite again.
> Walled to this domain.

- **Classify firearms off `tier1 === 'firearms'`, NOT the `isFirearm` convenience boolean** — they can
  drift; a misclassified item could skip the FFL gate. `tier1` is the canonical check.
- **FFL `license_expiry` is not validated at checkout** — could charge a transfer fee for an expired
  FFL. Validate at payment time.
- **Restricted-states coverage is incomplete.** It's rules-based (`sync-restrictions.ts` +
  `apply-restriction-rules.ts`), not legal-expert-driven. The **pre-launch compliance audit is the top
  backlog item** (federal/state firearms + age-gating legal review).
- **No online 4473 / age gate** — deferred to in-person FFL + legal-notice copy.
- **RSR home-based-FFL restriction is a visibility filter only** (`lib/visibility.ts`), separate from
  cart/payment validation — a restricted item could leak through.
- **Committed Chattanooga distributor FTP credentials** in tracked `lib/r2.ts` — exposed in git
  history. Flagged in recon FINDINGS as a **separate remediation task** (rotate + scrub); not actioned
  in this pass.
- **QuickBooks sync is stubbed** — orders don't auto-sync to accounting; manual reconciliation today.

> ⚠️ COMPLIANCE WALL: FFL / Class-02-SOT / NFA knowledge lives ONLY here
> (mad/armory). Never copy into customs or _shared.
