#!/usr/bin/env python3
"""
agentic-os Dev Dashboard — v4 "mission control" EXTRACTOR (data-driven generator).

Reads the LIVE vault and writes, into _system/dashboard/ ONLY:
  - dashboard-data.json   the DATA layer (inspect / extend here)
  - dashboard.html        the RENDERER; DATA is inlined at generate-time so the
                          page works from file:// with no fetch/CORS problems.

ARCHITECTURE: two separated layers. This script is the extractor; dashboard.html
renders FROM the data. No project data is hand-written into the HTML — add a field
here and the renderer surfaces it. That is the cardinal rule.

SINGLE-WRITER / READ-ONLY RULE: this script READS the vault (and `git log` dates
from the three repos, read-only) and writes ONLY to _system/dashboard/. It never
writes into data/, domain folders, or _graphs/.

RUN MODEL (Phase 1): generator, not server. Refresh = re-run this script.
  $ python3 _system/dashboard/extract_dashboard.py
No server, no sockets, no live trigger buttons (those are Phase 3).

FRESHNESS THRESHOLDS (by most-recent file mtime within a sub-area):
  green < 3 days | amber 3–10 days | red > 10 days   (tune GREEN_DAYS / AMBER_DAYS)
MOMENTUM is computed from GIT COMMIT DATES per repo (not mtime — mtime resets on
checkout / NTFS): hot = commit in last 3d, cooling = last 10d, idle = none.

CANDIDATE FUTURE FIELDS (the owner expects to want more — add to scan_sub_area /
scan_domain; the renderer surfaces what's present):
  - openTodos per knowledge file, decisions/gotchas counts
  - graphStats: node/edge counts from _graphs/<g>/graphify-out/graph.json
  - lastCommit author/message per domain; PR / CI status
  - owner-set PRIORITY / pinned markers in now.md
  - PHASE 2 candidate (NOT built): re-render each repo's graph.json as a themed D3
    graph in the Armory palette, instead of iframing graphify's own-styled graph.html.
The schema is per-domain / per-sub-area objects with room for new keys.
"""

import os
import re
import json
import datetime
import pathlib
import subprocess

# --- config -----------------------------------------------------------------
VAULT = pathlib.Path(__file__).resolve().parents[2]   # _system/dashboard/ -> vault root
OUT_DIR = VAULT / "_system" / "dashboard"
GREEN_DAYS, AMBER_DAYS = 3, 10
RHYTHM_DAYS = 14
MOMENTUM_DAYS = 21

META = {"_ops", "_system"}
SKIP_TOP = {"_graphs", "_recon", ".git", ".obsidian", "_system"}
GRAPH_DIR = {"mad": "mad-custom-tx", "zus": "zus-legacy", "fugro": "PM_Auto"}
REPO = {"mad": "/home/sdoucet/projects/mad-custom-tx",
        "zus": "/home/sdoucet/projects/zus-legacy",
        "fugro": "/home/sdoucet/projects/PM_Auto"}
BACKLOG_REL = {"mad": "BACKLOG.md", "zus": "recon/PINNED_BACKLOG.md", "fugro": "BACKLOG.md"}
WSL_FILE_PREFIX = "file://wsl.localhost/Ubuntu"
GRAPH_ORDER = ["mad", "zus", "fugro"]   # dropdown order in the graph panel

NOW = datetime.datetime.now()
SKELETON = re.compile(r"_\(none.*?\)_|_\(empty.*?\)_", re.I)


# --- helpers ----------------------------------------------------------------
def mtime(p):
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def newest_mtime(root):
    best = mtime(root)
    if root.is_dir():
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                best = max(best, mtime(pathlib.Path(dp) / f))
    return best


def age_days(ts):
    return 9999.0 if not ts else (NOW - datetime.datetime.fromtimestamp(ts)).total_seconds() / 86400.0


def freshness(days):
    return "green" if days < GREEN_DAYS else "amber" if days <= AMBER_DAYS else "red"


def iso(ts):
    return None if not ts else datetime.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def clean(s):
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"[*`]", "", s)
    return s.strip()


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


def _bullets(lines):
    out = []
    for line in lines:
        m = re.match(r"^\s*-\s*(\[[ xX]\]\s*)?(.*)", line)
        if m and m.group(2).strip() and not SKELETON.search(m.group(2)):
            done = bool(m.group(1) and m.group(1).strip().lower() == "[x]")
            out.append((done, clean(m.group(2))[:200]))
    return out


def parse_now(path):
    res = {"state": None, "focusItems": [], "next": None, "nextItems": [],
           "blocked": False, "blockedItems": [], "parked": False, "parkedItems": []}
    if not path.is_file():
        return res
    secs = md_sections(path.read_text(encoding="utf-8", errors="ignore"))
    res["focusItems"] = [t for _d, t in _bullets(secs.get("current focus", []))]
    res["state"] = res["focusItems"][0] if res["focusItems"] else None
    res["nextItems"] = [{"done": d, "text": t} for d, t in _bullets(secs.get("next actions", []))]
    undone = [n["text"] for n in res["nextItems"] if not n["done"]]
    res["next"] = undone[0] if undone else None
    res["blockedItems"] = [t for _d, t in _bullets(secs.get("blocked", []))]
    res["blocked"] = bool(res["blockedItems"])
    res["parkedItems"] = [t for _d, t in _bullets(secs.get("parked", []))]
    res["parked"] = bool(res["parkedItems"])
    return res


def claude_title(domain_dir):
    p = domain_dir / "CLAUDE.md"
    if p.is_file():
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"^#\s+(.*)", line)
            if m:
                return clean(m.group(1))[:90]
    return None


def count_knowledge(path):
    kdir = path / "knowledge"
    total = populated = 0
    if kdir.is_dir():
        for f in sorted(kdir.glob("*.md")):
            total += 1
            body = "\n".join(l for l in f.read_text(encoding="utf-8", errors="ignore").splitlines()
                             if not l.startswith(("#", ">")))
            if body.strip() and not SKELETON.search(body):
                populated += 1
    return total, populated


def _git(repo, args):
    try:
        r = subprocess.run(["git", "-C", repo] + args, capture_output=True, text=True, timeout=20)
        return r.stdout.splitlines() if r.returncode == 0 else []
    except Exception:
        return []


def git_momentum(repo):
    """Activity trend from GIT commit dates over the last MOMENTUM_DAYS (oldest..newest)."""
    bars = [0] * MOMENTUM_DAYS
    today = NOW.date()
    for ln in _git(repo, ["log", f"--since={MOMENTUM_DAYS} days ago", "--format=%cd", "--date=short"]):
        try:
            d = datetime.date.fromisoformat(ln.strip())
        except ValueError:
            continue
        delta = (today - d).days
        if 0 <= delta < MOMENTUM_DAYS:
            bars[MOMENTUM_DAYS - 1 - delta] += 1
    total = sum(bars)
    recent3, recent10 = sum(bars[-3:]), sum(bars[-10:])
    if recent3 > 0:
        state, word = "hot", "hot"
    elif recent10 > 0:
        state, word = "cooling", "cooling"
    elif total > 0:
        state, word = "idle", "cold"
    else:
        state, word = "idle", "idle"
    return {"bars": bars, "total": total, "state": state, "word": word, "days": MOMENTUM_DAYS, "source": "git"}


def idle_momentum():
    return {"bars": [0] * MOMENTUM_DAYS, "total": 0, "state": "idle", "word": "idle",
            "days": MOMENTUM_DAYS, "source": "none"}


def recent_commits(repo, n=6):
    out = []
    SEP = "\x1f"
    for ln in _git(repo, ["log", f"-{n}", f"--format=%h{SEP}%cd{SEP}%s", "--date=short"]):
        parts = ln.split(SEP)
        if len(parts) == 3:
            out.append({"hash": parts[0], "date": parts[1], "subject": clean(parts[2])[:100]})
    return out


def git_last_commit_ts(repo):
    """Unix timestamp of the repo's most-recent commit (read-only). 0.0 if none/not a repo.
    'last swept' uses GIT COMMIT TIME, not mtime: mtime resets on checkout / NTFS access,
    so an mtime-based 'last swept' read ~0h constantly (always "just now"). The vault's last
    commit is the honest answer to "when did the agent last meaningfully touch the vault?"."""
    out = _git(repo, ["log", "-1", "--format=%ct"])
    try:
        return float(out[0].strip()) if out else 0.0
    except (ValueError, IndexError):
        return 0.0


# --- scanners ---------------------------------------------------------------
def scan_sub_area(domain, sub, path):
    now = parse_now(path / "now.md")
    ts = newest_mtime(path)
    days = age_days(ts)
    ktotal, kpop = count_knowledge(path)
    rel = path.relative_to(VAULT).as_posix()
    next_undone = sum(1 for n in now["nextItems"] if not n["done"])
    return {
        "subArea": sub,
        "state": now["state"], "focusItems": now["focusItems"],
        "next": now["next"], "nextItems": now["nextItems"],
        "blocked": now["blocked"], "blockedItems": now["blockedItems"],
        "parked": now["parked"], "parkedItems": now["parkedItems"],
        "counts": {"inFlight": len(now["focusItems"]), "next": next_undone,
                   "blocked": len(now["blockedItems"]), "parked": len(now["parkedItems"])},
        "lastUpdated": iso(ts), "ageDays": round(days, 1), "freshness": freshness(days),
        "knowledgeFiles": ktotal, "knowledgePopulated": kpop,
        "hasNow": (path / "now.md").is_file(), "hasSkills": (path / "skills").is_dir(),
        "paths": {"dir": rel,
                  "now": f"{rel}/now.md" if (path / "now.md").is_file() else None,
                  "knowledge": f"{rel}/knowledge" if (path / "knowledge").is_dir() else None},
    }


STATUS_RANK = {"green": 0, "amber": 1, "red": 2}
HEALTH = {"green": "healthy", "amber": "attention", "red": "critical"}


def worst_status(sa):
    st = sa["freshness"]
    if sa["blocked"]:
        return "red"
    if sa["parked"] and st != "red":
        return "amber"
    return st


def scan_domain(d):
    did = d["id"]
    ddir = VAULT / did
    kind = "meta" if did in META else "knowledge"
    subs = []
    for child in sorted(p for p in ddir.iterdir() if p.is_dir()):
        if (child / "knowledge").is_dir() or (child / "now.md").is_file():
            subs.append(scan_sub_area(did, child.name, child))
    if not subs:
        subs = [scan_sub_area(did, None, ddir)]

    statuses = [worst_status(sa) for sa in subs]
    health_status = max(statuses, key=lambda s: STATUS_RANK[s]) if statuses else "green"

    def urgency(sa):
        return (sa["blocked"], sa["parked"], STATUS_RANK[sa["freshness"]], sa["ageDays"])
    pick = max(range(len(subs)), key=lambda i: urgency(subs[i])) if subs else None
    most = None
    if pick is not None:
        sa = subs[pick]
        reason = ("blocked" if sa["blocked"] else "parked" if sa["parked"]
                  else "stalest" if sa["freshness"] != "green" else "most recent")
        most = {"subArea": sa["subArea"], "next": sa["next"] or sa["state"],
                "freshness": sa["freshness"], "reason": reason}

    counts = {"inFlight": sum(s["counts"]["inFlight"] for s in subs),
              "next": sum(s["counts"]["next"] for s in subs),
              "blocked": sum(s["counts"]["blocked"] for s in subs),
              "parked": sum(s["counts"]["parked"] for s in subs)}

    graph = None
    if did in GRAPH_DIR:
        ghtml = VAULT / "_graphs" / GRAPH_DIR[did] / "graphify-out" / "graph.html"
        graph = {"name": GRAPH_DIR[did], "html": ghtml.relative_to(VAULT).as_posix(),
                 "exists": ghtml.is_file()}
    backlog = None
    if did in REPO and did in BACKLOG_REL:
        bpath = pathlib.Path(REPO[did]) / BACKLOG_REL[did]
        backlog = {"path": str(bpath), "rel": BACKLOG_REL[did],
                   "exists": bpath.is_file(), "fileUrl": WSL_FILE_PREFIX + str(bpath)}
    repo = None
    momentum = idle_momentum()
    commits = []
    if did in REPO:
        rp = REPO[did]
        ok = pathlib.Path(rp, ".git").exists()
        repo = {"path": rp, "name": pathlib.Path(rp).name, "exists": ok}
        if ok:
            momentum = git_momentum(rp)
            commits = recent_commits(rp)

    return {
        "domain": did, "kind": kind, "title": claude_title(ddir) or did,
        "router": f"{did}/CLAUDE.md" if (ddir / "CLAUDE.md").is_file() else None,
        "health": HEALTH[health_status], "healthStatus": health_status,
        "mostUrgent": most, "counts": counts,
        "subAreaTally": [{"subArea": sa["subArea"] or "(flat)", "status": worst_status(sa)} for sa in subs],
        "lastUpdated": iso(newest_mtime(ddir)), "freshness": freshness(age_days(newest_mtime(ddir))),
        "rhythm": [0] * RHYTHM_DAYS, "momentum": momentum, "recentCommits": commits,
        "repo": repo, "graph": graph, "backlog": backlog, "subAreas": subs,
    }


def discover_domains():
    found = []
    for child in sorted(p for p in VAULT.iterdir() if p.is_dir()):
        if child.name in SKIP_TOP:
            continue
        if (child / "CLAUDE.md").is_file() or (child / "knowledge").is_dir() or (child / "now.md").is_file():
            found.append(child.name)
    found += ["_ops", "_system"]
    seen, out = set(), []
    for did in found:
        if did not in seen and (VAULT / did).is_dir():
            seen.add(did)
            out.append({"id": did})
    return out


# --- cross-domain rollups ---------------------------------------------------
URG_RANK = {"critical": 0, "warn": 1, "parked": 2, "active": 3}


def build_urgent(domains):
    items = []
    for d in domains:
        if d["kind"] != "knowledge":
            continue
        for sa in d["subAreas"]:
            base = d["domain"] + (f" · {sa['subArea']}" if sa["subArea"] else "")
            for t in sa["blockedItems"]:
                items.append({"domain": d["domain"], "label": base, "text": t, "severity": "critical", "kind": "blocked"})
            for t in sa["parkedItems"]:
                items.append({"domain": d["domain"], "label": base, "text": t, "severity": "parked", "kind": "parked"})
            if sa["state"]:
                sev = ("critical" if re.search(r"⛔|TOP PRIORITY|blocks launch", sa["state"], re.I)
                       else "warn" if re.search(r"FIX NEXT|BUG", sa["state"]) else "active")
                items.append({"domain": d["domain"], "label": base, "text": sa["state"], "severity": sev, "kind": "focus"})
    items.sort(key=lambda u: (URG_RANK[u["severity"]], u["label"]))
    return items[:9]


def build_telemetry(domains):
    flags = sum(d["counts"]["blocked"] + d["counts"]["parked"] for d in domains)
    parked = sum(d["counts"]["parked"] for d in domains)
    open_items = sum(d["counts"]["next"] for d in domains)
    code_graphs = sum(1 for d in domains if d.get("graph") and d["graph"]["exists"])
    active = sum(1 for d in domains if d["kind"] == "knowledge" and d.get("repo") and d["repo"]["exists"])
    swept = git_last_commit_ts(str(VAULT)) or newest_mtime(VAULT)   # git commit time, not mtime
    return {"agentState": "IDLE", "running": 0,
            "sweptSource": "git" if git_last_commit_ts(str(VAULT)) else "mtime",
            "lastSweptIso": iso(swept),
            "lastSweptHours": round(age_days(swept) * 24, 1) if swept else None,
            "activeProjects": active, "codeGraphs": code_graphs,
            "flags": flags, "parked": parked, "openItems": open_items}


def build_graph_panel(domains):
    by = {d["domain"]: d for d in domains}
    projects = []
    for did in GRAPH_ORDER:
        d = by.get(did)
        g = d.get("graph") if d else None
        if g:
            projects.append({"domain": did, "label": did.upper(),
                             "src": "../../" + g["html"], "exists": g["exists"]})
    default = next((p["domain"] for p in projects if p["exists"]),
                   projects[0]["domain"] if projects else None)
    return {"projects": projects, "default": default}


# --- build + write ----------------------------------------------------------
def atomic_write(path, text):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main():
    domains = [scan_domain(d) for d in discover_domains()]
    data = {
        "schemaVersion": 4, "version": "v4-missioncontrol",
        "generatedAt": NOW.isoformat(timespec="seconds"),
        "vaultPath": str(VAULT),
        "obsidianVaultPath": r"\\wsl.localhost\Ubuntu\home\sdoucet\projects\agentic-os",
        "freshnessThresholds": {"greenDays": GREEN_DAYS, "amberDays": AMBER_DAYS,
                                "momentumDays": MOMENTUM_DAYS},
        "phase": 1,
        "telemetry": build_telemetry(domains),
        "urgent": build_urgent(domains),
        "graphPanel": build_graph_panel(domains),
        "domains": domains,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(OUT_DIR / "dashboard-data.json", json.dumps(data, indent=2))
    inlined = json.dumps(data).replace("</", "<\\/")
    atomic_write(OUT_DIR / "dashboard.html", HTML_TEMPLATE.replace("/*__DATA__*/null", inlined))

    print(f"[dashboard v4] {len(domains)} domains -> {OUT_DIR}/dashboard.html")
    t = data["telemetry"]
    print(f"  telemetry: active={t['activeProjects']} graphs={t['codeGraphs']} "
          f"flags={t['flags']} parked={t['parked']} open={t['openItems']} "
          f"swept={t['lastSweptHours']}h | urgent={len(data['urgent'])}")
    for d in domains:
        m = d["momentum"]
        print(f"  {d['domain']:9} {d['kind']:9} health={d['health']:9} "
              f"momentum={m['word']:8} ({m['total']} commits/{m['days']}d) sub-areas={len(d['subAreas'])}")


# --- renderer (static template; DATA injected at /*__DATA__*/null) ----------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>agentic-os · mission control</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0a0d11; --steel:#0e1217; --steel2:#141a21; --panel:#171e26; --panel2:#1d2630;
    --line:#26303c; --line2:#36434f;
    --txt:#cdd6e2; --muted:#7d8a9c; --dim:#56636f;
    --accent:#39FF14; --accent-dim:#28b410; --accent-deep:#0c3b06;
    --green:#39FF14; --amber:#f5b915; --red:#ff4747; --grey:#8a97a6;
    --display:'Bebas Neue',Impact,sans-serif; --body:'Inter',system-ui,sans-serif; --mono:'JetBrains Mono',monospace;
    --mo:1;
  }
  [data-motion="off"]{ --mo:0; }
  @media (prefers-reduced-motion: reduce){ :root{ --mo:0; } }
  *{box-sizing:border-box}
  html,body{margin:0}
  body{background:var(--bg);color:var(--txt);font-family:var(--body);font-size:14px;line-height:1.5;
       -webkit-font-smoothing:antialiased;min-height:100vh}
  body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:9999;
    background:repeating-linear-gradient(0deg, rgba(57,255,20,.025) 0 1px, transparent 1px 3px);
    opacity:calc(.5 * var(--mo));mix-blend-mode:screen;animation:scan 8s linear infinite}
  @keyframes scan{to{background-position:0 600px}}
  a{color:inherit;text-decoration:none}
  .wrap{max-width:1280px;margin:0 auto;padding:0 18px 70px}

  .cmdbar{position:sticky;top:0;z-index:50;background:linear-gradient(180deg,#0c1015,#0a0d11);
    border-bottom:1px solid var(--line);display:flex;align-items:center;gap:14px;padding:11px 18px;backdrop-filter:blur(6px)}
  .logo{font-family:var(--display);font-size:26px;letter-spacing:1.5px;cursor:pointer;white-space:nowrap;line-height:1}
  .logo b{color:var(--accent)} .logo:hover{filter:brightness(1.15)}
  /* command bar is honest-disabled (phase 1.5): no backend on a static file:// page, so the
     palette + CAPTURE/REPORT/FOCUS are deliberately inert — dimmed, not-allowed, no fake live caret. */
  .prompt{flex:1;min-width:120px;display:flex;align-items:center;gap:8px;background:#0b0f14;
    border:1px dashed var(--line);border-radius:6px;padding:8px 12px;color:var(--dim);font-family:var(--mono);font-size:12.5px;
    cursor:not-allowed;opacity:.6;user-select:none}
  .prompt .pk{color:var(--dim)}
  .p3{font-family:var(--mono);font-size:8px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);
    border:1px solid var(--line);border-radius:3px;padding:2px 5px;margin-left:auto;white-space:nowrap}
  .cmdgrp{display:flex;align-items:center;gap:8px}
  .qbtn{font-family:var(--display);letter-spacing:1px;font-size:14px;padding:7px 12px;border-radius:5px;
    border:1px solid var(--line);background:var(--panel);color:var(--dim);cursor:not-allowed;opacity:.5;user-select:none}
  .cmdnote{font-family:var(--mono);font-size:8.5px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);
    border:1px dashed var(--line);border-radius:4px;padding:4px 8px;white-space:nowrap}
  .motionbtn{font-family:var(--mono);font-size:10px;color:var(--dim);border:1px solid var(--line);
    border-radius:5px;padding:7px 9px;background:var(--steel);cursor:pointer;white-space:nowrap}
  .motionbtn:hover{color:var(--accent-dim);border-color:var(--line2)}

  .telem{display:grid;grid-template-columns:1.7fr repeat(5,1fr);gap:1px;background:var(--line);
    border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:16px 0}
  .cell{background:linear-gradient(180deg,var(--steel2),var(--steel));padding:11px 14px}
  .cell .lab{font-family:var(--mono);font-size:8.5px;letter-spacing:1.5px;text-transform:uppercase;color:var(--dim)}
  .cell .val{font-family:var(--display);font-size:30px;letter-spacing:1px;line-height:1;margin-top:3px}
  .cell .sub{font-family:var(--mono);font-size:9.5px;color:var(--muted);margin-top:3px}
  .cell.agent{display:flex;flex-direction:column;justify-content:center}
  .cell.agent .row1{display:flex;align-items:center;gap:9px}
  .cell.agent .state{font-family:var(--display);font-size:26px;letter-spacing:1.5px;color:var(--accent)}
  .pulse{width:9px;height:9px;border-radius:50%;background:var(--accent);flex:none;position:relative}
  .pulse::after{content:"";position:absolute;inset:-4px;border-radius:50%;border:1px solid var(--accent);
    animation:ring 2s ease-out infinite;opacity:var(--mo)}
  @keyframes ring{0%{transform:scale(.6);opacity:calc(.9*var(--mo))}100%{transform:scale(1.9);opacity:0}}
  .val.warn{color:var(--amber)}

  .split{display:grid;grid-template-columns:1.55fr 1fr;gap:14px;margin-bottom:16px}
  .pnl{background:linear-gradient(180deg,var(--panel),var(--steel2));border:1px solid var(--line);border-radius:9px;overflow:hidden}
  .pnl-h{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 13px;border-bottom:1px solid var(--line);background:#10151b}
  .pnl-h .t{font-family:var(--display);font-size:17px;letter-spacing:1.5px;display:flex;align-items:center;gap:8px}
  .live{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 6px var(--accent);
    animation:beat 1.6s ease-in-out infinite;opacity:calc(.4 + .6*var(--mo))}
  @keyframes beat{50%{transform:scale(1.5);filter:brightness(1.4)}}
  select.gsel{font-family:var(--mono);font-size:11px;background:#0b0f14;color:var(--accent-dim);
    border:1px solid var(--line2);border-radius:5px;padding:5px 8px;cursor:pointer}
  #graphhost{position:relative;overflow:hidden;width:100%;background:#0a0d11}
  .gframe{height:430px;border:0;background:#0a0d11;display:block}
  .sbtoggle{font-family:var(--mono);font-size:10px;color:var(--accent-dim);border:1px solid var(--line2);
    border-radius:5px;padding:5px 9px;cursor:pointer;white-space:nowrap}
  .sbtoggle:hover{border-color:var(--accent-dim);color:var(--accent)}
  .ghead-r{display:flex;gap:8px;align-items:center}
  .gmiss{height:430px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;
    color:var(--muted);font-family:var(--mono);font-size:12px;text-align:center;padding:20px}
  .gmiss code{color:var(--accent-dim)}

  .urg{padding:8px;display:flex;flex-direction:column;gap:7px;max-height:430px;overflow:auto}
  .uitem{display:flex;gap:10px;padding:9px 10px;background:var(--steel);border:1px solid var(--line);
    border-left:3px solid var(--line2);border-radius:0 6px 6px 0;cursor:pointer;transition:border-color .15s,transform .05s}
  .uitem:hover{border-color:var(--line2);transform:translateX(2px)}
  .uitem.critical{border-left-color:var(--red)} .uitem.warn{border-left-color:var(--amber)}
  .uitem.parked{border-left-color:var(--grey)} .uitem.active{border-left-color:var(--accent-dim)}
  .uitem .udot{width:8px;height:8px;border-radius:50%;margin-top:5px;flex:none}
  .udot.critical{background:var(--red);box-shadow:0 0 5px var(--red);animation:pp 1.4s infinite}
  .udot.warn{background:var(--amber);box-shadow:0 0 5px var(--amber)}
  .udot.parked{background:var(--grey)} .udot.active{background:var(--accent-dim)}
  @keyframes pp{50%{opacity:calc(1 - .65*var(--mo))}}
  .uitem .ut{min-width:0}
  .uitem .ul{font-family:var(--mono);font-size:9px;letter-spacing:.5px;text-transform:uppercase;color:var(--dim);display:flex;justify-content:space-between;gap:6px}
  .uitem .ul .sev{color:var(--muted)}
  .uitem .ux{font-size:12px;color:var(--txt);margin-top:2px;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}

  .seclab{font-family:var(--mono);font-size:9.5px;letter-spacing:2px;text-transform:uppercase;color:var(--dim);margin:6px 0 10px}

  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
  .gl{background:linear-gradient(180deg,var(--panel),var(--steel2));border:1px solid var(--line);border-radius:9px;
    padding:15px 16px;cursor:pointer;transition:border-color .15s,transform .06s}
  .gl:hover{border-color:var(--accent-dim);transform:translateY(-2px)}
  .gl-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
  .gl-name{font-family:var(--display);font-size:30px;letter-spacing:1.5px;line-height:.95;display:flex;align-items:center;gap:9px}
  .pdot{width:10px;height:10px;border-radius:50%;flex:none}
  .pdot.hot{background:var(--green);box-shadow:0 0 7px var(--green);animation:pp 1.5s infinite}
  .pdot.cooling{background:var(--amber);box-shadow:0 0 6px var(--amber)}
  .pdot.idle{background:var(--dim)}
  .hb{font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;padding:3px 8px;border-radius:20px;border:1px solid var(--line2);white-space:nowrap}
  .hb.healthy{color:var(--green);border-color:#1d5a16} .hb.attention{color:var(--amber);border-color:#5a4a16} .hb.critical{color:var(--red);border-color:#5a1d1d}
  .repoln{font-family:var(--mono);font-size:10px;color:var(--muted);margin:8px 0 2px}
  .counts{display:flex;gap:14px;font-family:var(--mono);font-size:10.5px;color:var(--muted);margin:10px 0}
  .counts b{font-family:var(--display);font-size:18px;letter-spacing:1px;color:var(--txt);margin-right:4px;font-weight:400}
  .counts .c-flag b{color:var(--amber)}
  .mom{display:flex;align-items:flex-end;gap:2px;height:24px;margin:6px 0 4px}
  .mom i{flex:1;min-height:2px;border-radius:1px;background:var(--line2)}
  .mom i.on{background:var(--accent-dim)}
  .mom.hot i.on{animation:breathe 3s ease-in-out infinite}
  @keyframes breathe{50%{filter:brightness(calc(1 + .5*var(--mo)))}}
  .momword{font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase}
  .momword.hot{color:var(--green)} .momword.cooling{color:var(--amber)} .momword.idle{color:var(--dim)}
  .focusln{font-size:12.5px;color:var(--txt);background:var(--steel);border-left:2px solid var(--accent-dim);
    padding:7px 10px;border-radius:0 5px 5px 0;margin:9px 0;min-height:34px}
  .focusln .k{font-family:var(--mono);font-size:8px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);display:block;margin-bottom:2px}
  .focusln .none{color:var(--muted)}
  .gl-bot{display:flex;align-items:center;justify-content:space-between;margin-top:10px}
  .tally{display:flex;gap:5px;flex-wrap:wrap}
  .tdot{width:8px;height:8px;border-radius:50%}
  .tdot.green{background:var(--green)} .tdot.amber{background:var(--amber)} .tdot.red{background:var(--red)}
  .enter{font-family:var(--mono);font-size:10px;color:var(--accent-dim);letter-spacing:.5px}

  .metarow{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
  .meta{flex:1;min-width:200px;display:flex;align-items:center;gap:10px;background:var(--steel2);border:1px solid var(--line);
    border-radius:7px;padding:9px 13px;opacity:.8;cursor:pointer}
  .meta:hover{opacity:1;border-color:var(--line2)}
  .meta .mn{font-family:var(--display);font-size:18px;letter-spacing:1px;color:var(--muted)}
  .meta .md{font-family:var(--mono);font-size:9.5px;color:var(--dim);margin-left:auto}
  .meta.static{cursor:default}
  .meta.static:hover{opacity:.8;border-color:var(--line)}

  #drill{display:none}
  .back{font-family:var(--mono);font-size:11px;color:var(--accent-dim);cursor:pointer;display:inline-flex;gap:7px;
    align-items:center;padding:7px 12px;border:1px solid var(--line2);border-radius:6px;background:var(--steel);margin:16px 0}
  .back:hover{border-color:var(--accent-dim);color:var(--accent)}
  .d-h{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:4px}
  .d-h .dn{font-family:var(--display);font-size:46px;letter-spacing:2px}
  .dlink{font-family:var(--mono);font-size:10px;color:var(--accent-dim);border:1px solid var(--line2);border-radius:5px;padding:4px 9px;cursor:pointer}
  .dlink.off{color:var(--dim);border-style:dashed;cursor:default}
  .sa{background:linear-gradient(180deg,var(--panel),var(--steel2));border:1px solid var(--line);border-radius:9px;padding:15px 16px}
  .sa h4{margin:0 0 3px;font-family:var(--display);font-size:22px;letter-spacing:1px;display:flex;align-items:center;gap:9px}
  .sa .age{font-family:var(--mono);font-size:9.5px;color:var(--muted);margin-bottom:11px}
  .tasks{list-style:none;margin:0;padding:0}
  .tasks li{display:flex;gap:9px;padding:5px 0;font-size:12.5px;border-top:1px solid var(--line)}
  .tasks li:first-child{border-top:0}
  .tk{width:8px;height:8px;border-radius:50%;margin-top:5px;flex:none}
  .tk.focus{background:var(--green);box-shadow:0 0 5px var(--green)} .tk.next{background:var(--accent-dim)}
  .tk.done{background:var(--dim)} .tk.blocked{background:var(--red);box-shadow:0 0 5px var(--red)} .tk.parked{background:var(--grey)}
  .tasks li.done{color:var(--dim);text-decoration:line-through}
  .tasks .tg{font-family:var(--mono);font-size:8px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);align-self:center;margin-left:auto;flex:none}
  .donecard h4{color:var(--accent-dim)}
  .commit{display:flex;gap:9px;font-family:var(--mono);font-size:11px;padding:5px 0;border-top:1px solid var(--line)}
  .commit:first-of-type{border-top:0} .commit .h{color:var(--accent-dim)} .commit .dt{color:var(--dim)} .commit .s{color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

  footer{margin-top:30px;border-top:1px solid var(--line);padding-top:12px;font-family:var(--mono);
    font-size:10px;color:var(--dim);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
  footer code{color:var(--muted)}
  @media(max-width:880px){.split{grid-template-columns:1fr}.telem{grid-template-columns:1fr 1fr}}
</style>
</head>
<body data-motion="on">
<div class="cmdbar">
  <div class="logo" onclick="goHome()">AGENTIC<b>·</b>OS</div>
  <div class="prompt" aria-disabled="true" title="phase 3 — a static file:// page has no backend; regenerate via the CLI">
    <span class="pk">⌘</span> <span>command palette — not wired yet</span> <span class="p3">phase 3</span></div>
  <span class="cmdgrp">
    <span class="qbtn" aria-disabled="true" title="phase 3 · needs local server">CAPTURE</span>
    <span class="qbtn" aria-disabled="true" title="phase 3 · needs local server">REPORT</span>
    <span class="qbtn" aria-disabled="true" title="phase 3 · needs local server">FOCUS</span>
    <span class="cmdnote">phase 3 · needs local server</span>
  </span>
  <span class="motionbtn" id="mobtn" onclick="toggleMotion()">◉ motion</span>
</div>

<div class="wrap">
  <section id="home">
    <div class="telem" id="telem"></div>
    <div class="split">
      <div class="pnl">
        <div class="pnl-h">
          <div class="t"><span class="live"></span> CODE-GRAPH</div>
          <div class="ghead-r">
            <span class="sbtoggle" id="sbtoggle" onclick="toggleSidebar()" title="show search / node-info / communities">‹ panel</span>
            <select class="gsel" id="gsel" onchange="swapGraph(this.value)"></select>
          </div>
        </div>
        <div id="graphhost"></div>
      </div>
      <div class="pnl">
        <div class="pnl-h"><div class="t">⚠ NEEDS ATTENTION</div></div>
        <div class="urg" id="urg"></div>
      </div>
    </div>
    <div class="seclab">active projects</div>
    <div class="grid" id="grid"></div>
    <div class="seclab" style="margin-top:18px">meta · infrastructure</div>
    <div class="metarow" id="metarow"></div>
  </section>

  <section id="drill">
    <div class="back" onclick="goHome()">← mission control</div>
    <div id="drillbody"></div>
  </section>

  <footer id="foot"></footer>
</div>

<script>
const DATA = /*__DATA__*/null;
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const byId = id => DATA.domains.find(d=>d.domain===id);

function toggleMotion(){
  const b=document.body, on=b.getAttribute('data-motion')==='on';
  b.setAttribute('data-motion', on?'off':'on');
  document.getElementById('mobtn').textContent=(on?'○ motion':'◉ motion');
}

function renderTelem(){
  const t=DATA.telemetry;
  const cell=(lab,val,sub,cls)=>`<div class="cell"><div class="lab">${lab}</div><div class="val ${cls||''}">${val}</div><div class="sub">${sub||''}</div></div>`;
  const swept = t.lastSweptHours!=null ? (t.lastSweptHours<48?t.lastSweptHours+'h':(Math.round(t.lastSweptHours/24)+'d')) : '—';
  document.getElementById('telem').innerHTML =
    `<div class="cell agent"><div class="lab">agent</div>
       <div class="row1"><span class="pulse"></span><span class="state">${esc(t.agentState)}</span></div>
       <div class="sub">last swept ${swept} ago · ${t.flags} flags · ${t.running} running</div></div>`
    + cell('active projects', t.activeProjects, 'with a repo')
    + cell('code-graphs', t.codeGraphs, 'generated')
    + cell('flags', t.flags, 'blocked + parked', t.flags>0?'warn':'')
    + cell('parked', t.parked, 'deferred', t.parked>0?'warn':'')
    + cell('open items', t.openItems, 'next-actions');
}

function renderGraph(){
  const gp=DATA.graphPanel;
  const sel=document.getElementById('gsel');
  if(!gp || !gp.projects.length){ document.getElementById('graphhost').innerHTML='<div class="gmiss">no code-graphs</div>'; sel.style.display='none'; return; }
  sel.innerHTML = gp.projects.map(p=>`<option value="${p.domain}">${esc(p.label)}${p.exists?'':' · not generated'}</option>`).join('');
  swapGraph(gp.default || gp.projects[0].domain);
}
let sidebarOpen=false;  /* default COLLAPSED: graph maximized; graphify's 280px side panel (search/node-info/communities) is clipped */
function toggleSidebar(){
  sidebarOpen=!sidebarOpen;
  const b=document.getElementById('sbtoggle');
  b.textContent=sidebarOpen?'panel ›':'‹ panel';
  b.title=sidebarOpen?'hide search / node-info / communities (maximize graph)':'show search / node-info / communities';
  const cur=document.getElementById('gsel').value;
  if(cur) swapGraph(cur);   /* reload the iframe at the new width so graphify re-fits its layout (it has no resize handler) */
}
function swapGraph(domain){
  const gp=DATA.graphPanel, p=gp.projects.find(x=>x.domain===domain);
  const host=document.getElementById('graphhost');
  document.getElementById('gsel').value=domain;
  if(p && p.exists){
    /* collapsed: over-size the iframe by graphify's 280px #sidebar (+border) and let #graphhost{overflow:hidden} clip it
       off the right — the graph (#graph{flex:1}) then fills the freed width. expanded: iframe = host width, sidebar shows. */
    const w = sidebarOpen ? '100%' : 'calc(100% + 282px)';
    host.innerHTML=`<iframe class="gframe" style="width:${w}" src="${esc(p.src)}" title="${esc(p.label)} code-graph" loading="lazy"></iframe>`;
  } else { host.innerHTML=`<div class="gmiss">graph not generated for <b>${esc(p?p.label:domain)}</b><br>run <code>graphify extract &lt;repo&gt;</code> then re-run the dashboard extractor</div>`; }
}

function renderUrgent(){
  const u=DATA.urgent;
  document.getElementById('urg').innerHTML = u.length ? u.map(i=>
    `<div class="uitem ${i.severity}" onclick="enter('${i.domain}')">
       <span class="udot ${i.severity}"></span>
       <div class="ut"><div class="ul"><span>${esc(i.label)}</span><span class="sev">${esc(i.severity)}</span></div>
       <div class="ux">${esc(i.text)}</div></div></div>`).join('')
    : '<div class="gmiss" style="height:auto;padding:30px">nothing urgent · all clear</div>';
}

function momentum(m){
  const max=Math.max(1,...m.bars);
  const bars=m.bars.map(v=>`<i class="${v>0?'on':''}" style="height:${Math.max(2,Math.round(v/max*24))}px"></i>`).join('');
  return `<div class="mom ${m.state}">${bars}</div><div class="momword ${m.state}">▸ ${esc(m.word)} · ${m.total} commits/${m.days}d</div>`;
}
function glimpse(d){
  const c=d.counts;
  const repo = d.repo ? d.repo.name+(d.repo.exists?'':' · missing') : 'vault-only';
  const flags = c.blocked+c.parked;
  const tally = d.subAreaTally.map(t=>`<span class="tdot ${t.status}" title="${esc(t.subArea)}"></span>`).join('');
  const focus = d.mostUrgent && d.mostUrgent.next
    ? `<span class="k">current focus${d.mostUrgent.subArea?(' · '+esc(d.mostUrgent.subArea)):''}</span>${esc(d.mostUrgent.next)}`
    : `<span class="k">current focus</span><span class="none">none set</span>`;
  return `<div class="gl" onclick="enter('${d.domain}')">
    <div class="gl-top">
      <div class="gl-name"><span class="pdot ${d.momentum.state}"></span>${esc(d.domain)}</div>
      <span class="hb ${d.healthStatus==='green'?'healthy':d.healthStatus==='amber'?'attention':'critical'}">${esc(d.health)}</span>
    </div>
    <div class="repoln">${esc(repo)}</div>
    <div class="counts"><span><b>${c.inFlight}</b>in&#8209;flight</span><span><b>${c.next}</b>next</span><span class="${flags?'c-flag':''}"><b>${flags}</b>blocked/parked</span></div>
    ${momentum(d.momentum)}
    <div class="focusln">${focus}</div>
    <div class="gl-bot"><div class="tally">${tally}</div><span class="enter">enter →</span></div>
  </div>`;
}
function renderGrid(){
  const k=DATA.domains.filter(d=>d.kind==='knowledge');
  const m=DATA.domains.filter(d=>d.kind==='meta');
  document.getElementById('grid').innerHTML=k.map(glimpse).join('');
  document.getElementById('metarow').innerHTML = m.map(d=>
    `<div class="meta" onclick="enter('${d.domain}')"><span class="mn">${esc(d.domain)}</span>
       <span class="md">${esc(d.title)} · ${d.subAreas.length} area${d.subAreas.length!==1?'s':''}</span></div>`).join('')
    + `<div class="meta static" title="this dashboard — generated, no detail page"><span class="mn">dashboard</span><span class="md">this surface · phase 1 · v4</span></div>`;
}

function subCard(sa){
  const tasks=[];
  (sa.focusItems||[]).forEach(t=>tasks.push(`<li><span class="tk focus"></span><span>${esc(t)}</span><span class="tg">focus</span></li>`));
  (sa.nextItems||[]).forEach(n=>tasks.push(`<li class="${n.done?'done':''}"><span class="tk ${n.done?'done':'next'}"></span><span>${esc(n.text)}</span><span class="tg">${n.done?'done':'next'}</span></li>`));
  (sa.blockedItems||[]).forEach(t=>tasks.push(`<li><span class="tk blocked"></span><span>${esc(t)}</span><span class="tg">blocked</span></li>`));
  (sa.parkedItems||[]).forEach(t=>tasks.push(`<li><span class="tk parked"></span><span>${esc(t)}</span><span class="tg">parked</span></li>`));
  const body = tasks.length?`<ul class="tasks">${tasks.join('')}</ul>`:`<div class="focusln"><span class="none">no tasks set — ${sa.knowledgePopulated}/${sa.knowledgeFiles} knowledge files</span></div>`;
  return `<div class="sa"><h4><span class="tdot ${sa.freshness}"></span>${esc(sa.subArea||'(flat)')}</h4>
    <div class="age">${sa.lastUpdated?('updated '+esc(sa.lastUpdated.replace('T',' '))+' · '+sa.ageDays+'d'):'never'} · ${sa.knowledgePopulated}/${sa.knowledgeFiles} knowledge${sa.hasSkills?' · skills':''}</div>
    ${body}</div>`;
}
function doneCard(d){
  if(!d.recentCommits || !d.recentCommits.length) return '';
  return `<div class="sa donecard"><h4>✓ done recently</h4><div class="age">last ${d.recentCommits.length} commits · ${esc(d.repo?d.repo.name:'')}</div>`
    + d.recentCommits.map(c=>`<div class="commit"><span class="h">${esc(c.hash)}</span><span class="dt">${esc(c.date)}</span><span class="s">${esc(c.subject)}</span></div>`).join('')+`</div>`;
}
function enter(id){
  const d=byId(id); if(!d) return;
  const gbtn=d.graph&&d.graph.exists?`<span class="dlink" onclick="openRel('${esc(d.graph.html)}')">▦ ${esc(d.graph.name)} graph</span>`:(d.graph?`<span class="dlink off">▦ graph not generated</span>`:'');
  const bbtn=d.backlog&&d.backlog.exists?`<span class="dlink" onclick="window.open('${esc(d.backlog.fileUrl)}','_blank')" title="${esc(d.backlog.path)}">📋 backlog ↗</span>`:'';
  document.getElementById('drillbody').innerHTML =
    `<div class="d-h"><div class="dn">${esc(d.domain)}</div>
       <span class="hb ${d.healthStatus==='green'?'healthy':d.healthStatus==='amber'?'attention':'critical'}">${esc(d.health)}</span>
       ${gbtn}${bbtn}</div>
     <div class="repoln" style="margin-bottom:14px">${esc(d.title)}${d.router?(' · '+esc(d.router)):''}${d.repo?(' · '+esc(d.repo.name)):''}</div>
     <div class="grid">${d.subAreas.map(subCard).join('')}${doneCard(d)}</div>`;
  document.getElementById('home').style.display='none';
  document.getElementById('drill').style.display='';
  location.hash='d/'+id; window.scrollTo(0,0);
}
function goHome(){
  document.getElementById('drill').style.display='none';
  document.getElementById('home').style.display='';
  location.hash=''; window.scrollTo(0,0);
}
function openRel(rel){ window.open('../../'+rel,'_blank'); }

function route(){
  const h=location.hash.replace(/^#/,'');
  if(h.startsWith('d/')){ const id=h.slice(2); if(byId(id)){ enter(id); return; } }
  goHome();
}
function init(){
  renderTelem(); renderGraph(); renderUrgent(); renderGrid();
  document.getElementById('foot').innerHTML =
    `<span>generated ${esc(DATA.generatedAt.replace('T',' '))} · ${esc(DATA.version)} · static · read-only</span>`+
    `<span>regenerate: <code>python3 _system/dashboard/extract_dashboard.py</code> · triggers = phase 3</span>`;
  window.addEventListener('hashchange', route);
  route();
}
init();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
