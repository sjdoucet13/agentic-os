# Architecture — mad / _shared (brand · LLC · infra — NOT compliance)

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

Mad LLC dual-storefront e-commerce — **one Next.js app serving two hostnames**:
`madarmorytx.com` (Armory, tactical dark theme `#09090b`) + `madcustomstx.com` (Customs, neon theme
`#08080f`). Repo `~/projects/mad-custom-tx-master` (branch `working`). Pre-launch.

## Stack (ground truth)
- **Next.js 16.2.4** — uses the Next 16 `proxy.ts` middleware convention (root file exports `proxy`).
  [correction: not Next 14]
- **Supabase** — Postgres + Supabase Auth (`app_metadata.role`); **Prisma 7** via `@prisma/adapter-pg`
  (native `pg` pool).
- **Vercel** hosting · **Cloudflare R2** for media (`media.madarmorytx.com`, AWS S3 SDK).
- **NMI** payment gateway (Collect.js tokenization → `chargePayment`) · **Resend** email.
- Vendor/catalog sync on a **DigitalOcean droplet cron** (every 6h + nightly), **not** Vercel cron
  (deleted 2026-05-26). [correction]

## Dual-storefront routing (`proxy.ts`)
Detects hostname → sets `x-mad-storefront` header (`customs` / `tactical`); pages + `layout.tsx` read
it to theme and rewrite (`/`→`/armory` or `/boutique`; `/shop*`→ storefront shop). The **foundry
pre-launch gate** is deny-by-default: no `foundry_access_key` cookie → `/holding` (200 rewrite).

## Auth / admin
Supabase Auth; role resolves from `app_metadata.role` (or Prisma `User.role==ADMIN`). Admin
context-switcher cookie (Customs / Armory / Combined) scopes the dashboards; all admin API routes are
gated by `requireAdmin()`.

## Shared catalog + cart + payment
- **`Product`** (UPC primary key, `storefront` enum ARMORY|CUSTOMS|UNIVERSAL); **`VendorOffer`**
  (vendor + vendorSku → UPC; cost / stock / `lastHash` idempotency) is the shared feed-bridge model.
- **Dual-cart** in localStorage, scoped per storefront; a **mixed armory+customs cart is rejected** at
  checkout (400).
- **Payment** (`/api/payment/process`): server revalidates prices from DB → Order PENDING → NMI charge
  → PAID → Resend confirmation + QB sync async via `after()`.

## Related
- [[mad/_shared/knowledge/Decisions|Decisions]] — why this infra
- [[mad/_shared/knowledge/Domain|Domain]] — the LLC + storefront entities
- [[mad/_shared/knowledge/Gotchas|Gotchas]] — infra footguns
- [[mad/_shared/knowledge/Lessons|Lessons]] — what the infra taught
