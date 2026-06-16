# Decisions — mad / _shared (brand · LLC · infra — NOT compliance)

> Decisions made and the *why* behind them (ADR-style). Append-only — never rewrite a
> past decision; supersede it with a new entry. Walled to this domain.

- **Monorepo dual-storefront** (one Next.js app, two hostnames) over two separate apps — shared cart,
  payment, auth, and admin infra; the foundry gate lets both pre-launch on the same instance.
- **Supabase Auth with role in `app_metadata`**, synced to Prisma `User.role` via a DB trigger; API
  routes fall back to a Prisma read.
- **NMI over Stripe** — Stripe appears nowhere in the repo (Scott's processor relationship).
- **Cloudflare R2** for media + presigned uploads.
- **DigitalOcean droplet crontab for catalog/stock sync** — Vercel cron was deleted 2026-05-26.
- **Hard mixed-cart rejection** (armory + customs in one order = 400) to avoid split-fulfillment.
- **Single Resend sender domain** (`madarmorytx.com`) for both storefronts with display-name
  differentiation; a Pro upgrade (separate `madcustomstx.com` sender) is deferred until customs traffic
  justifies it.
- **Pre-launch lockdown** — foundry gate + search-engine shutoff (robots `Disallow: /`, empty sitemap,
  `noindex/nofollow`) behind `PRE_LAUNCH_LOCKDOWN` constants, original rules preserved for the flip.
