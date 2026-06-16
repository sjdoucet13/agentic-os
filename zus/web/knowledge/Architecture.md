# Architecture — zus / web

> How this domain's systems/work are structured: components, data flow, how the pieces
> fit together. Walled to this domain. Reconcile raw captures into here (RECONCILE).

The Next.js **clan-intelligence platform** for ZUS. The repo name "nextjs-boilerplate" is a misnomer —
it's a full platform. Repo `~/projects/zus-legacy/nextjs-boilerplate` (branch `screenshot-pipeline`).

## Stack
Next.js **14.2.15** · **MongoDB 6.5.0** (prod `ZUS_Clan_DB`) · **Vercel** · JWT auth (`jose`) with a
**site-role vs clan-role** split · **Google Gemini** for screenshot OCR · **UploadThing** uploads ·
Chart.js (bundled, not runtime-CDN).

## Layers
middleware (auth + clan isolation + maintenance gate) → routes (`app/api/*`, `app/[clanSlug]/*`) →
auth/isolation helpers (`app/lib/auth.ts`, `isolation.ts`, `api-helpers.ts`) → Mongo singleton +
`getClanQuery()` (`app/api/engine/db.ts`).

## Collections
Users, Clans, Players, Scores, Events (missions), Recruits / SeasonalRecruits, IdentityRequests,
AdminAuditLog / AdminActionLog, DiagnosticLogs, ClanSnapshots, LoginRateLimit.

## Subsystems
Leaderboard / scores, AWOL tracking, roster capture, participation analytics, **advancedcalc**
(battle-strength engine), OCR screenshot + Discord-image ingestion, multi-clan admin.

## Ingestion
- **Scores** — OCR of screenshots + Discord images via Gemini (`processScreenshotWithAI`,
  `processDiscordImage`); OCR is **score-only**.
- **Rosters / player stats** — from the **intel** `roster-capture-ingest.ts` bridge (network capture →
  decode → upsert `Players`); this owns might / hero / titles.
- The `screenshot-pipeline` branch refactors a shared score-write core (`resolveNorm` / `writeScore`).
