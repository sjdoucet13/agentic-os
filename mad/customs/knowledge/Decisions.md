# Decisions — mad / customs

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Konva for the in-browser canvas** (drag/resize/text/image); **Sharp server-side** for composite +
  DPI scoring — cheaper than running heavyweight graphics on the client.
- **Proof-approval gate (not automatic)** — admin uploads a proof, customer approves or requests
  revisions; captures a customer attestation before production. Tracked in OrderAuditLog.
- **Separate Blank + Listing products** — one blank can spawn many saleable listings sharing one stock
  pool (e.g. 25 designs on one tumbler blank = 25 SKUs, 1 on-hand count).
- **Collections over vendor taxonomy** for customs discovery — curated, brand-controlled, separated
  from armory.
- **Flat customs shipping** ($14.95, hardcoded) for now; an admin-configurable rate is deferred to a
  later customs-admin sprint.

## Related
- [[mad/customs/knowledge/Architecture|Architecture]] — what these choices built
- [[mad/customs/knowledge/Lessons|Lessons]] — what they taught
