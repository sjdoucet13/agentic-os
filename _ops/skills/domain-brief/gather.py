#!/usr/bin/env python3
"""domain-brief gather — collect ONE domain's vault slice + code-repo signal for the brief.

Deterministic input-gathering for the `domain-brief` skill. The synthesis into a tight
5–8 sentence brief is CC's job (see SKILL.md); this script just assembles the raw signal so
the brief is grounded, not guessed. Reads ONLY the named domain — single-writer /
no-contamination. Read-only: it writes nothing.

Usage:
  python3 gather.py --domain mad
  python3 gather.py --domain mad --commits 8

Stdlib only. The Phase 3 command server can spawn this with fixed argv.
"""
import argparse
import datetime
import re
import subprocess
import sys
import pathlib

VAULT = pathlib.Path(__file__).resolve().parents[3]   # _ops/skills/domain-brief/ -> vault

# domain -> its CODE repo (read-only). Same kind of fixed config as capture's allow-list.
REPO = {
    "mad":      "/home/sdoucet/projects/mad-custom-tx-master",
    "zus":      "/home/sdoucet/projects/zus-legacy/nextjs-boilerplate",
    "fugro":    "/home/sdoucet/projects/PM_Auto",
    "personal": None,
}
DOMAINS = sorted(REPO)
KN_HIGHLIGHT = ["Decisions", "Gotchas", "Lessons"]
SKELETON = re.compile(r"_\(none.*?\)_|_\(empty.*?\)_", re.I)
NOW = datetime.datetime.now()


def _git(repo, args):
    try:
        r = subprocess.run(["git", "-C", str(repo)] + args,
                           capture_output=True, text=True, timeout=20)
        return r.stdout.splitlines() if r.returncode == 0 else []
    except Exception:
        return []


def md_sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            cur = m.group(1).strip().lower()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def bullets(lines):
    out = []
    for line in lines:
        m = re.match(r"^\s*-\s*(\[[ xX]\]\s*)?(.*)", line)
        if m and m.group(2).strip() and not SKELETON.search(m.group(2)):
            done = bool(m.group(1) and m.group(1).strip().lower() == "[x]")
            out.append((done, m.group(2).strip()))
    return out


def sub_areas(ddir):
    subs = [p for p in sorted(ddir.iterdir()) if p.is_dir()
            and ((p / "now.md").is_file() or (p / "knowledge").is_dir())]
    return subs or [ddir]          # flat domain -> itself


def knowledge_highlights(path):
    out = {}
    kdir = path / "knowledge"
    for name in KN_HIGHLIGHT:
        f = kdir / f"{name}.md"
        if not f.is_file():
            continue
        body = [l for l in f.read_text(encoding="utf-8", errors="ignore").splitlines()
                if l.strip() and not l.lstrip().startswith(("#", ">")) and not SKELETON.search(l)]
        picks = [m.group(1).strip() for l in body
                 for m in [re.match(r"^\s*[-*]\s+(.*)", l)] if m and m.group(1).strip()]
        out[name] = {"count": len(picks), "picks": picks[:2]}
    return out


def reconcile_date(rel_now_paths):
    out = _git(VAULT, ["log", "-1", "--format=%cd", "--date=short", "--"] + rel_now_paths)
    return out[0].strip() if out else None


def main(argv=None):
    ap = argparse.ArgumentParser(description="gather a domain's slice for domain-brief")
    ap.add_argument("--domain", required=True, choices=DOMAINS)
    ap.add_argument("--commits", type=int, default=8)
    args = ap.parse_args(argv)
    d = args.domain
    ddir = VAULT / d
    if not ddir.is_dir():
        print(f"domain-brief: no such domain dir {d!r}", file=sys.stderr)
        return 2

    print(f"DOMAIN-BRIEF INPUTS — {d}   (gathered {NOW:%Y-%m-%d %H:%M})")
    print("=" * 64)

    now_rels = []
    print("## sub-areas")
    for sp in sub_areas(ddir):
        label = sp.name if sp != ddir else "(flat)"
        print(f"\n### {label}")
        nowf = sp / "now.md"
        if nowf.is_file():
            now_rels.append(nowf.relative_to(VAULT).as_posix())
            secs = md_sections(nowf.read_text(encoding="utf-8", errors="ignore"))
            focus = [t for _x, t in bullets(secs.get("current focus", []))]
            nxt = bullets(secs.get("next actions", []))
            blk = [t for _x, t in bullets(secs.get("blocked", []))]
            prk = [t for _x, t in bullets(secs.get("parked", []))]
            opens = [t for dn, t in nxt if not dn]
            print(f"focus: {focus[0] if focus else '(none set)'}")
            print(f"next(open {len(opens)}): " + (" | ".join(opens[:3]) if opens else "(none)"))
            if blk:
                print("blocked: " + " | ".join(blk))
            if prk:
                print("parked: " + " | ".join(prk))
        else:
            print("now.md: (none)")
        kh = knowledge_highlights(sp)
        if kh:
            print("knowledge: " + ", ".join(f"{n}({kh[n]['count']})" for n in kh))
            for n in kh:
                for p in kh[n]["picks"][:1]:
                    print(f"  {n[:3].lower()}: {p[:120]}")

    print("\n## captures (_inbox.md)")
    any_inbox = False
    for sp in sub_areas(ddir):
        inb = sp / "_inbox.md"
        if inb.is_file():
            lines = [l.strip() for l in inb.read_text(encoding="utf-8", errors="ignore").splitlines()
                     if re.match(r"^\s*-\s+\[", l)]
            if lines:
                any_inbox = True
                lbl = sp.name if sp != ddir else "(flat)"
                print(f"{lbl}: {len(lines)} unprocessed; latest: {lines[-1][:100]}")
    if not any_inbox:
        print("(none — no unprocessed captures)")

    repo = REPO.get(d)
    last_date = None
    print("\n## code repo")
    if repo and pathlib.Path(repo, ".git").exists():
        br = (_git(repo, ["branch", "--show-current"]) or ["?"])[0]
        print(f"{pathlib.Path(repo).name} @ {br}")
        log = _git(repo, ["log", f"-{args.commits}", "--format=%h|%cd|%s", "--date=short"])
        if log:
            last_date = log[0].split("|")[1]
        for ln in log:
            parts = ln.split("|", 2)
            if len(parts) == 3:
                print(f"  {parts[0]} {parts[1]} {parts[2][:90]}")
    else:
        print("(no code repo configured / not present)")

    print("\n## staleness signals")
    rec = reconcile_date(now_rels) if now_rels else None
    print(f"now.md last reconciled (vault): {rec or '(unknown)'}")
    print(f"code last commit: {last_date or '(none)'}")
    if rec and last_date:
        try:
            rd = datetime.date.fromisoformat(rec)
            cd = datetime.date.fromisoformat(last_date)
            if cd > rd:
                print("  -> HINT: code committed AFTER the last now.md reconcile — now.md may be "
                      "behind the code; offer to reconcile.")
            else:
                print("  -> date-wise now.md is at/after the latest code commit; STILL verify the "
                      "focus/done lines actually reflect the recent commits (content, not just date).")
        except ValueError:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
