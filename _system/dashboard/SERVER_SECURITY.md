# SERVER_SECURITY.md — Phase 3 Local Command Server · Threat Model

> **STATUS: DRAFT — pending user sign-off.** No server code exists until the sign-off
> box at the bottom is checked. This document is the gate, written *before* the server.

A browser page that can trigger local execution is the single most security-relevant
component of the agentic-os build. This is why Phase 3 was deferred to its own deliberate
pass instead of bolted onto the end of a long session. Read this, decide the open
questions (D1–D3), sign off — then we build the smallest real thing.

---

## 1. What we're building (and why it's dangerous)

A minimal **Node server, bound to `127.0.0.1` only**, that:
1. Serves the dashboard (replacing `file://`), and
2. Exposes a **fixed, allow-listed** set of named action endpoints that the command-bar
   buttons POST to. Each endpoint invokes an **existing `_ops/` skill** — the same skills
   Claude Code uses — and returns a short result the page displays.

The danger is the obvious one: a web page that reaches `127.0.0.1` and causes the local
machine to *do things*. The entire security posture below exists to ensure that page can
only do a small, fixed, safe set of things — and that *only the dashboard* can do them.

---

## 2. Assets to protect

| Asset | Exposure if compromised |
|---|---|
| The vault filesystem (`knowledge/`, `now.md`, `_ops/`) | Unwanted/forged writes; cross-domain contamination |
| The three source repos (`mad`/`zus`/`fugro`) | Read of code; the server treats them read-only |
| **Known committed secrets** (`mad lib/r2.ts`, `zus .env`) | Must NEVER be readable/returnable via any endpoint |
| The user's machine generally | RCE = total compromise — the threat we most defend against |

---

## 3. Trust boundary

- **Trusted:** the dashboard page served *by this server*, driven by the *single local user*.
- **Untrusted:** literally everything else — other browser tabs, other processes, any
  LAN/tailnet host. The server must assume any request that isn't provably from its own
  served page is hostile.

---

## 4. Threats → controls

**T1 — Arbitrary command / RCE (HIGHEST).**
Control: **ALLOW-LIST, NEVER EVAL.** The server maps a fixed enum of action names
(`capture`, `note`, `report`, `focus`) → fixed skill invocations. It NEVER interpolates
page-supplied strings into a shell, a path, or a command name. No `eval`, no
`exec`/`shell:true` with user input (use `spawn` with a fixed argv + array args), no
dynamic `require`. Payloads are validated against a strict schema: a known action enum +
a bounded, sanitized text field (for `capture`/`note`). Domain targets are chosen from a
fixed list — the page cannot name an arbitrary path or domain outside it.

**T2 — CSRF / cross-origin trigger.**
A malicious page in another tab tries to POST to `127.0.0.1:<port>`. Layered controls:
- Reject unless `Origin`/`Referer` equals the server's own origin.
- Reject unless `Sec-Fetch-Site: same-origin`.
- Require `Content-Type: application/json` (blocks HTML simple-form CSRF).
- Mint a per-process CSRF token into the served page; require it as a custom header on
  every action POST (custom headers force a CORS preflight the attacker can't satisfy).

**T3 — Network exposure.**
Bind `127.0.0.1` ONLY — never `0.0.0.0`. Explicitly **not** bound to the Tailscale
interface unless D3 says otherwise. (The user reaches this laptop via Tailscale SSH; the
*server* must not ride the tailnet by accident.)

**T4 — Secret / data leakage.**
Endpoints return only action outcomes (ok/fail + a short message). No file contents, no
env, no reading of arbitrary paths. Nothing sensitive in URLs or query strings — POST
JSON bodies only. The known committed secrets are unreachable by construction (no
read-file endpoint exists).

**T5 — Write-path integrity.**
The server invokes the SAME `_ops/` skills CC uses (single-writer rule preserved), not a
parallel writer. Writes land in the correct domain only; no cross-domain bridging; the
COMPLIANCE WALL is unaffected (no endpoint targets `armory` regulated content specially).
GateGuard semantics are respected — the server is a thin trigger, the skill does the work.

**T6 — DoS / runaway.**
Actions are short, single-concurrency, debounced, and time-bounded (kill a child that
overruns). No unbounded loops driven by the page.

**T7 — Supply chain.**
Target **zero npm dependencies** — Node stdlib `http`/`child_process` only — so no
third-party code runs inside the trusted server. (Mirrors the extractor's stdlib-only ethos.)

---

## 5. Recommended posture (the safe defaults I propose)

- **On-demand**, not always-on: start the console when you want it; stop it when done. No
  persistent background attack surface.
- **Localhost only**, not tailnet.
- **Buttons-first**; the `⌘` free-text prompt is **deferred** — a free-text parser is an
  injection surface and adds no capability the buttons don't already prove. Revisit once
  the button loop is trusted.
- **Node stdlib only**, no deps.
- **One action end-to-end first: `capture`** — lowest blast radius (it just appends a
  note to a domain). Prove the whole loop (click → server → skill → result in UI) on the
  safest action before wiring `note`/`report`/`focus`.
- The agent cell can flip to a real **`running`** state while an action executes, finally
  making `0 running` honest — cheap to add once the loop exists; not the goal.

---

## 6. Open decisions — need your call (these ARE the sign-off)

| # | Decision | Recommended | Alternative (and its cost) |
|---|---|---|---|
| **D1** | `⌘` prompt scope | **Defer** (buttons-first) | Include now as a *fixed-grammar* parser over the allow-list — more parsing/injection surface; never a "run what I typed" shell |
| **D2** | Server lifecycle | **On-demand** | Always-on background service — more "JARVIS," but a persistent surface to harden + supervise |
| **D3** | Network exposure | **Localhost only** | Tailnet-reachable (console from phone) — **materially bigger threat model**: requires an auth token + per-request auth + re-review; do NOT enable without an eyes-open decision |

---

## 7. Sign-off

- [x] Reviewed; controls in §4 and posture in §5 approved.
- [x] **D1 = defer the ⌘ prompt (buttons-first) · D2 = on-demand · D3 = localhost only**
- [ ] Cleared to build `capture` end-to-end — ⚠ **BLOCKED on §8** (skills are stubs; needs
      a go-ahead to implement the capture skill + define the capture surface).

_Signed: user (dashboard sign-off) · Date: 2026-06-17_

---

## 8. Prerequisite discovered after sign-off — the skills are STUBS

`_ops/CLAUDE.md` and `_ops/skills/capture/SKILL.md` both mark the skills
**`status: stub` — real logic deferred**. There is no executable capture logic for the
server to invoke, and no defined **capture surface** (where a raw capture lands). The
Phase 3 brief assumed the skills existed; they don't yet.

**Consequence:** "capture end-to-end" now also requires *implementing* the capture skill —
a vault-structure decision: *where do raw captures land?* Per OPERATING_PROCEDURE, captures
are NOT `now.md` (FOCUS — CC-owned curated head) and NOT `knowledge/` (RECONCILE output).
They need their own append-only surface, per domain, wall-respecting.

**Proposed minimal capture surface (reversible, conventional):**
- Each sub-area gets an append-only `_inbox.md`, created on first capture
  (e.g. `mad/armory/_inbox.md`, `zus/web/_inbox.md`).
- Capture = append a timestamped bullet: `- [YYYY-MM-DD HH:MM] <text>`.
- Stays inside one domain; armory captures only under `mad/armory/` (compliance wall).
- RECONCILE later promotes inbox items into `knowledge/`; CAPTURE just lands them fast.
- Implemented as a tiny stdlib script (`_ops/skills/capture/capture.py`) the server spawns
  with fixed argv (`--domain <enum>`, text on stdin) — satisfies T1/T5 (no eval; the same
  single-writer path, not a parallel one).

This is net-new vault structure + skill implementation (deferred on purpose), so it needs
an explicit go-ahead before the server has anything real to call.
