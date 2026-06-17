#!/usr/bin/env python3
"""capture skill — the CAPTURE moment, made real.

Append a raw capture (a thought / finding / decision / bug / task) to ONE domain's
append-only `_inbox.md`. Fast, wall-respecting, single-writer. This is NOT reconciliation:
it just lands the thought in the right domain's inbox; the RECONCILE moment later promotes
inbox items into that domain's `knowledge/`.

Usage:
  echo "the thought"  | python3 capture.py --domain mad/armory
  python3 capture.py --domain fugro --text "the thought"

Design / guarantees (see _system/dashboard/SERVER_SECURITY.md §8):
  * `--domain` MUST be one of the fixed allow-list (DOMAINS). Unknown -> error, no write.
  * Each domain maps to exactly ONE in-domain `_inbox.md`. No traversal, no cross-domain
    write, no arbitrary path -> honors the no-contamination law + the mad compliance wall
    (armory captures land only under mad/armory) BY CONSTRUCTION.
  * Stdlib only. This is the SAME write path the Phase 3 command server invokes (fixed
    argv, text on stdin or --text, no shell, no eval).
"""
import argparse
import datetime
import pathlib
import sys

# _ops/skills/capture/capture.py -> vault root is 3 parents up
VAULT = pathlib.Path(__file__).resolve().parents[3]

# fixed allow-list: capture target -> the in-domain inbox (relative to vault root).
# mad has NO bare-root inbox on purpose: the customs/armory/_shared split must stay visible.
DOMAINS = {
    "fugro":       "fugro/_inbox.md",
    "mad/customs": "mad/customs/_inbox.md",
    "mad/armory":  "mad/armory/_inbox.md",
    "mad/_shared": "mad/_shared/_inbox.md",
    "zus":         "zus/_inbox.md",
    "personal":    "personal/_inbox.md",
}
MAX_LEN = 2000


def inbox_header(domain):
    h = (f"# {domain} — Inbox (raw captures)\n\n"
         "> Append-only CAPTURE surface. RECONCILE promotes items into `knowledge/`.\n"
         "> CC-written via the `capture` skill; one domain only — never hand-bridged.\n")
    if domain == "mad/armory":
        h += "> ⚠️ REGULATED — FFL / SOT / NFA compliance wall applies; armory captures stay here.\n"
    return h + "\n"


def capture(domain, text, vault=VAULT):
    """Append one capture bullet to the domain's _inbox.md. Returns (rel_path, created)."""
    if domain not in DOMAINS:
        raise ValueError(f"unknown domain {domain!r}; allowed: {', '.join(sorted(DOMAINS))}")
    text = " ".join(text.split()).strip()          # collapse to a single clean bullet line
    if not text:
        raise ValueError("empty capture text")
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN].rstrip() + "…"
    rel = DOMAINS[domain]
    inbox = (vault / rel)
    inbox.parent.mkdir(parents=True, exist_ok=True)
    created = not inbox.exists()
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with inbox.open("a", encoding="utf-8") as f:
        if created:
            f.write(inbox_header(domain))
        f.write(f"- [{stamp}] {text}\n")
    return rel, created


def main(argv=None):
    ap = argparse.ArgumentParser(description="CAPTURE — append a raw capture to a domain's _inbox.md")
    ap.add_argument("--domain", required=True, choices=sorted(DOMAINS),
                    help="capture target (fixed allow-list)")
    ap.add_argument("--text", default=None, help="the capture text (else read from stdin)")
    ap.add_argument("--vault", default=None, help="override vault root (testing only)")
    args = ap.parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    vault = pathlib.Path(args.vault).resolve() if args.vault else VAULT
    try:
        rel, created = capture(args.domain, text, vault)
    except ValueError as e:
        print(f"capture: {e}", file=sys.stderr)
        return 2
    print(f"capture ok: {args.domain} -> {rel} ({'created' if created else 'appended'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
