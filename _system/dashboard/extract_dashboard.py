#!/usr/bin/env python3
"""
agentic-os Dev Dashboard — Phase 1 EXTRACTOR (data-driven generator).

Reads the LIVE vault and writes, into _system/dashboard/ ONLY:
  - dashboard-data.json   the DATA layer (inspect / extend here)
  - dashboard.html        the RENDERER; DATA is inlined at generate-time so the
                          page works from file:// with no fetch/CORS problems.

ARCHITECTURE: two separated layers. This script is the extractor; dashboard.html
renders FROM the data. No project data is hand-written into the HTML — add a field
here and the renderer surfaces it. That is the whole point.

SINGLE-WRITER / READ-ONLY RULE: this script READS the vault and writes ONLY to
_system/dashboard/. It never writes into data/, domain folders, or _graphs/. The
dashboard is strictly a read-surface; it never authors vault content.

RUN MODEL (Phase 1): generator, not server. Refresh = re-run this script.
  $ python3 _system/dashboard/extract_dashboard.py
No server, no sockets, no working trigger buttons (those are Phase 3).

FRESHNESS THRESHOLDS (by most-recent file mtime within a sub-area):
  green  < 3 days   |   amber  3–10 days   |   red  > 10 days
(Tune GREEN_DAYS / AMBER_DAYS below.)

CANDIDATE FUTURE FIELDS — the owner expects to want more after living with v1.
Add to the per-sub-area dict in scan_sub_area() (the renderer iterates fields
generically where it can):
  - momentum        : file-changes or commits per week (velocity)
  - openTodos       : count of unchecked "- [ ]" across knowledge/now
  - decisions/gotchas counts per knowledge file
  - lastCommit      : `git log -1` for the domain's repo (if wired later)
  - graphStats      : node/edge counts read from _graphs/<g>/graphify-out/graph.json
  - priority/pinned : an owner-set `PRIORITY:` marker in now.md
The schema is per-sub-area objects with room for new keys; growth is a one-liner.
"""

import os
import re
import json
import datetime
import pathlib

# --- config -----------------------------------------------------------------
VAULT = pathlib.Path(__file__).resolve().parents[2]   # _system/dashboard/ -> vault root
OUT_DIR = VAULT / "_system" / "dashboard"
GREEN_DAYS, AMBER_DAYS = 3, 10
RHYTHM_DAYS = 14

# Meta-domains (vault infrastructure, not knowledge domains).
META = {"_ops", "_system"}
# Top-level entries that are never domains.
SKIP_TOP = {"_graphs", "_recon", ".git", ".obsidian", "_system"}  # _system handled explicitly below
# Domain -> code-graph dir under _graphs/ (config, NOT project data).
GRAPH_DIR = {"mad": "mad-custom-tx", "zus": "zus-legacy", "fugro": "PM_Auto"}

NOW = datetime.datetime.now()
SKELETON = re.compile(r"_\(none.*?\)_|_\(empty.*?\)_", re.I)


# --- helpers ----------------------------------------------------------------
def mtime(p: pathlib.Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def newest_mtime(root: pathlib.Path) -> float:
    """Most-recent mtime of any file under root (the sub-area's 'last touched')."""
    best = mtime(root)
    if root.is_dir():
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                best = max(best, mtime(pathlib.Path(dp) / f))
    return best


def age_days(ts: float) -> float:
    if not ts:
        return 9999.0
    return (NOW - datetime.datetime.fromtimestamp(ts)).total_seconds() / 86400.0


def freshness(days: float) -> str:
    if days < GREEN_DAYS:
        return "green"
    if days <= AMBER_DAYS:
        return "amber"
    return "red"


def iso(ts: float):
    if not ts:
        return None
    return datetime.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def clean(s: str) -> str:
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)   # [[path|alias]] -> alias
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"[*`_]", "", s)
    return s.strip()


def md_sections(text: str) -> dict:
    """Split a markdown doc into {section_title: [lines]} keyed by '## ' headings."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            cur = m.group(1).strip().lower()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return out


def parse_now(path: pathlib.Path) -> dict:
    """Extract state / next / blocked / parked from a now.md (None if absent)."""
    res = {"state": None, "next": None, "blocked": False, "blockedText": None, "parked": False}
    if not path.is_file():
        return res
    text = path.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"\bPARKED\b", text):
        res["parked"] = True
    secs = md_sections(text)

    def bullets(key):
        out = []
        for line in secs.get(key, []):
            m = re.match(r"^\s*-\s*(\[[ xX]\]\s*)?(.*)", line)
            if m and m.group(2).strip():
                done = bool(m.group(1) and m.group(1).strip().lower() == "[x]")
                out.append((done, m.group(2).strip()))
        return out

    # Current focus -> first non-skeleton bullet
    for _done, txt in bullets("current focus"):
        if not SKELETON.search(txt):
            res["state"] = clean(txt)[:160]
            break
    # Next actions -> first UNCHECKED item (the live next step)
    for done, txt in bullets("next actions"):
        if not done and not SKELETON.search(txt):
            res["next"] = clean(txt)[:160]
            break
    # Blocked -> any real (non-skeleton) item
    for _done, txt in bullets("blocked"):
        if not SKELETON.search(txt):
            res["blocked"] = True
            res["blockedText"] = clean(txt)[:160]
            break
    return res


def claude_title(domain_dir: pathlib.Path):
    p = domain_dir / "CLAUDE.md"
    if p.is_file():
        for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"^#\s+(.*)", line)
            if m:
                return clean(m.group(1))[:90]
    return None


def count_knowledge(path: pathlib.Path):
    """(total knowledge .md, populated ones) for a sub-area's knowledge/ dir."""
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


# --- scanners ---------------------------------------------------------------
def scan_sub_area(domain, sub, path: pathlib.Path) -> dict:
    now = parse_now(path / "now.md")
    ts = newest_mtime(path)
    days = age_days(ts)
    ktotal, kpop = count_knowledge(path)
    rel = path.relative_to(VAULT).as_posix()
    return {
        "subArea": sub,                       # None for flat domains
        "state": now["state"],
        "next": now["next"],
        "blocked": now["blocked"],
        "blockedText": now["blockedText"],
        "parked": now["parked"],
        "lastUpdated": iso(ts),
        "ageDays": round(days, 1),
        "freshness": freshness(days),
        "knowledgeFiles": ktotal,
        "knowledgePopulated": kpop,
        "hasNow": (path / "now.md").is_file(),
        "hasSkills": (path / "skills").is_dir(),
        "paths": {"dir": rel,
                  "now": f"{rel}/now.md" if (path / "now.md").is_file() else None,
                  "knowledge": f"{rel}/knowledge" if (path / "knowledge").is_dir() else None},
        # room for future per-sub-area keys (see header note)
    }


def rhythm(domain_dir: pathlib.Path) -> list:
    """Per-day file-change counts over the last RHYTHM_DAYS (oldest..newest)."""
    buckets = [0] * RHYTHM_DAYS
    today = NOW.date()
    for dp, _dn, fn in os.walk(domain_dir):
        for f in fn:
            d = datetime.date.fromtimestamp(mtime(pathlib.Path(dp) / f))
            delta = (today - d).days
            if 0 <= delta < RHYTHM_DAYS:
                buckets[RHYTHM_DAYS - 1 - delta] += 1
    return buckets


STATUS_RANK = {"green": 0, "amber": 1, "red": 2}
HEALTH = {"green": "healthy", "amber": "attention", "red": "critical"}


def worst_status(sa):
    st = sa["freshness"]
    if sa["blocked"] or sa["parked"]:
        st = "red" if st == "red" else "amber"
    return st


def scan_domain(d: dict) -> dict:
    did = d["id"]
    ddir = VAULT / did
    kind = "meta" if did in META else "knowledge"
    # discover sub-areas: immediate subdirs holding knowledge/ or now.md
    subs = []
    for child in sorted(p for p in ddir.iterdir() if p.is_dir()):
        if (child / "knowledge").is_dir() or (child / "now.md").is_file():
            subs.append(scan_sub_area(did, child.name, child))
    if not subs:  # flat domain (fugro, personal) or meta — treat the domain dir itself as one area
        subs = [scan_sub_area(did, None, ddir)]

    statuses = [worst_status(sa) for sa in subs]
    health_status = max(statuses, key=lambda s: STATUS_RANK[s]) if statuses else "green"

    # mostUrgent = worst (blocked/stalest) sub-area's next-action — "where do I look"
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

    newest = newest_mtime(ddir)
    graph = None
    if did in GRAPH_DIR:
        ghtml = VAULT / "_graphs" / GRAPH_DIR[did] / "graphify-out" / "graph.html"
        graph = {"name": GRAPH_DIR[did],
                 "html": ghtml.relative_to(VAULT).as_posix(),
                 "exists": ghtml.is_file()}

    return {
        "domain": did,
        "kind": kind,
        "title": claude_title(ddir) or did,
        "router": f"{did}/CLAUDE.md" if (ddir / "CLAUDE.md").is_file() else None,
        "health": HEALTH[health_status],
        "healthStatus": health_status,
        "mostUrgent": most,
        "subAreaTally": [{"subArea": sa["subArea"] or "(flat)", "status": worst_status(sa)} for sa in subs],
        "lastUpdated": iso(newest),
        "freshness": freshness(age_days(newest)),
        "rhythm": rhythm(ddir),
        "graph": graph,
        "subAreas": subs,
    }


def discover_domains() -> list:
    found = []
    for child in sorted(p for p in VAULT.iterdir() if p.is_dir()):
        name = child.name
        if name in SKIP_TOP:
            continue
        if (child / "CLAUDE.md").is_file() or (child / "knowledge").is_dir() or (child / "now.md").is_file():
            found.append(name)
    found += ["_ops", "_system"]
    seen, out = set(), []
    for did in found:
        if did not in seen and (VAULT / did).is_dir():
            seen.add(did)
            out.append({"id": did})
    return out


# --- build + write ----------------------------------------------------------
def atomic_write(path: pathlib.Path, text: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)   # atomic on same filesystem (restart-safe)


def main():
    domains = [scan_domain(d) for d in discover_domains()]
    data = {
        "schemaVersion": 1,
        "generatedAt": NOW.isoformat(timespec="seconds"),
        "vaultPath": str(VAULT),
        "obsidianVaultPath": r"\\wsl.localhost\Ubuntu\home\sdoucet\projects\agentic-os",
        "freshnessThresholds": {"greenDays": GREEN_DAYS, "amberDays": AMBER_DAYS, "rhythmDays": RHYTHM_DAYS},
        "phase": 1,
        "domains": domains,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(OUT_DIR / "dashboard-data.json", json.dumps(data, indent=2))

    inlined = json.dumps(data).replace("</", "<\\/")    # safe inside <script>
    html = HTML_TEMPLATE.replace("/*__DATA__*/null", inlined)
    atomic_write(OUT_DIR / "dashboard.html", html)

    print(f"[dashboard] {len(domains)} domains -> {OUT_DIR}/dashboard-data.json + dashboard.html")
    for d in domains:
        print(f"  {d['domain']:9} {d['kind']:9} health={d['health']:9} "
              f"sub-areas={len(d['subAreas'])} fresh={d['freshness']}")


# --- renderer (static template; DATA injected at /*__DATA__*/null) ----------
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>agentic-os · dev dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{
    --steel:#0e1116; --steel2:#151a21; --panel:#1b212b;
    --line:#2b3441; --line2:#3a4756;
    --txt:#cdd6e2; --muted:#7d8a9c; --dim:#566374;
    --accent:#39FF14; --accent-dim:#2bbf10;
    --green:#39FF14; --amber:#f0b400; --red:#ff4d4d;
    --display:'Bebas Neue',Impact,'Arial Narrow',sans-serif;
    --body:'Inter',system-ui,sans-serif;
    --mono:'JetBrains Mono',ui-monospace,monospace;
  }
  *{box-sizing:border-box}
  body{margin:0;background:linear-gradient(180deg,#0b0e12,#0e1116 220px);color:var(--txt);
       font-family:var(--body);font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1180px;margin:0 auto;padding:22px 20px 60px}
  header{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
         border-bottom:1px solid var(--line);padding-bottom:14px}
  .brand{font-family:var(--display);font-size:40px;letter-spacing:2px;line-height:.9}
  .brand b{color:var(--accent)}
  .brand small{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.5px;color:var(--muted);margin-top:6px}
  .meta-r{text-align:right;font-family:var(--mono);font-size:11px;color:var(--muted)}
  .meta-r code{color:var(--accent-dim)}
  .cmd{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:14px 0 22px}
  .cmd .lbl{font-family:var(--mono);font-size:10px;color:var(--dim);letter-spacing:1px;text-transform:uppercase;margin-right:4px}
  .btn{font-family:var(--display);letter-spacing:1.5px;font-size:15px;padding:7px 14px;border-radius:4px;
       border:1px solid var(--line2);background:var(--panel);color:var(--muted);position:relative;cursor:not-allowed;opacity:.62}
  .btn .ph{display:block;font-family:var(--mono);font-size:8px;letter-spacing:1px;color:var(--dim);margin-top:1px}
  .lvltag{font-family:var(--mono);font-size:10px;color:var(--dim);letter-spacing:1px;text-transform:uppercase;margin:0 0 12px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}
  .card{background:linear-gradient(180deg,var(--panel),var(--steel2));border:1px solid var(--line);
        border-radius:8px;padding:15px 16px;transition:border-color .15s,transform .05s}
  .card.click{cursor:pointer}
  .card.click:hover{border-color:var(--accent-dim);transform:translateY(-1px)}
  .card.meta{opacity:.86}
  .c-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
  .dname{font-family:var(--display);font-size:30px;letter-spacing:1.5px;line-height:.95}
  .dtag{font-family:var(--mono);font-size:10px;color:var(--muted);margin-top:3px}
  .health{font-family:var(--mono);font-size:10px;letter-spacing:1px;text-transform:uppercase;
          padding:3px 8px;border-radius:20px;border:1px solid var(--line2);white-space:nowrap}
  .health.healthy{color:var(--green);border-color:#1d5a16}
  .health.attention{color:var(--amber);border-color:#5a4a16}
  .health.critical{color:var(--red);border-color:#5a1d1d}
  .tally{display:flex;gap:6px;flex-wrap:wrap;margin:13px 0 10px}
  .pill{display:flex;align-items:center;gap:5px;font-family:var(--mono);font-size:10px;color:var(--muted);
        background:var(--steel);border:1px solid var(--line);border-radius:5px;padding:3px 7px}
  .dot{width:8px;height:8px;border-radius:50%;flex:none}
  .dot.green{background:var(--green);box-shadow:0 0 5px var(--green)}
  .dot.amber{background:var(--amber);box-shadow:0 0 5px var(--amber)}
  .dot.red{background:var(--red);box-shadow:0 0 5px var(--red)}
  .urgent{font-size:12.5px;color:var(--txt);background:var(--steel);border-left:2px solid var(--accent-dim);
          padding:7px 10px;border-radius:0 5px 5px 0;margin:6px 0 10px}
  .urgent .k{font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);display:block;margin-bottom:2px}
  .urgent .none{color:var(--muted)}
  .c-bot{display:flex;align-items:center;justify-content:space-between;margin-top:10px;gap:10px}
  .spark{display:flex;align-items:flex-end;gap:2px;height:22px}
  .spark i{width:5px;background:var(--line2);border-radius:1px;display:block;min-height:2px}
  .spark i.hot{background:var(--accent-dim)}
  .glink{font-family:var(--mono);font-size:10px;color:var(--accent-dim);border:1px solid var(--line2);
         border-radius:4px;padding:3px 8px;cursor:pointer}
  .glink.off{color:var(--dim);cursor:default;border-style:dashed}
  #detail{display:none}
  .back{font-family:var(--mono);font-size:11px;color:var(--accent-dim);cursor:pointer;display:inline-flex;gap:6px;align-items:center;margin-bottom:14px}
  .d2head{display:flex;align-items:baseline;gap:14px;margin-bottom:4px;flex-wrap:wrap}
  .d2head .dname{font-size:44px}
  .sa{background:linear-gradient(180deg,var(--panel),var(--steel2));border:1px solid var(--line);border-radius:8px;padding:14px 15px}
  .sa h4{margin:0 0 2px;font-family:var(--display);font-size:21px;letter-spacing:1px;display:flex;align-items:center;gap:8px}
  .sa .age{font-family:var(--mono);font-size:10px;color:var(--muted);margin-bottom:10px}
  .row{margin:7px 0;font-size:13px}
  .row .k{font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);display:block}
  .row .v{color:var(--txt)} .row .v.empty{color:var(--dim)}
  .flags{display:flex;gap:6px;margin-top:9px;flex-wrap:wrap}
  .flag{font-family:var(--mono);font-size:9px;letter-spacing:1px;text-transform:uppercase;padding:2px 7px;border-radius:4px;border:1px solid}
  .flag.blocked{color:var(--red);border-color:#5a1d1d}
  .flag.parked{color:var(--amber);border-color:#5a4a16}
  .flag.kn{color:var(--muted);border-color:var(--line2)}
  .flag.sk{color:var(--accent-dim);border-color:#1d5a16}
  footer{margin-top:34px;border-top:1px solid var(--line);padding-top:12px;
         font-family:var(--mono);font-size:10.5px;color:var(--dim);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
  footer code{color:var(--muted)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">AGENTIC&middot;OS <b>DASHBOARD</b><small id="genline"></small></div>
    <div class="meta-r" id="metar"></div>
  </header>

  <div class="cmd">
    <span class="lbl">command&nbsp;panel</span>
    <span class="btn">REGENERATE<span class="ph">trigger · phase 3</span></span>
    <span class="btn">CAPTURE<span class="ph">trigger · phase 3</span></span>
    <span class="btn">REPORT<span class="ph">trigger · phase 3</span></span>
    <span class="btn">RECONCILE<span class="ph">trigger · phase 3</span></span>
    <span class="btn">FOCUS<span class="ph">trigger · phase 3</span></span>
  </div>

  <section id="overview">
    <div class="lvltag">level 1 · overview — click a domain to drill in</div>
    <div class="grid" id="ovgrid"></div>
  </section>

  <section id="detail">
    <div class="back" onclick="showOverview()">&larr; all domains</div>
    <div id="detailbody"></div>
  </section>

  <footer id="foot"></footer>
</div>

<script>
const DATA = /*__DATA__*/null;

const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const dot = s => `<span class="dot ${s}"></span>`;

function sparkline(arr){
  const max = Math.max(1, ...arr);
  return `<div class="spark" title="file changes · last ${arr.length}d">`+
    arr.map(v=>`<i class="${v>0?'hot':''}" style="height:${Math.max(2, Math.round(v/max*22))}px"></i>`).join('')+`</div>`;
}

function domainCard(d){
  const tally = d.subAreaTally.map(t=>`<span class="pill">${dot(t.status)}${esc(t.subArea)}</span>`).join('');
  const u = d.mostUrgent;
  const urgent = u && (u.next||u.subArea)
    ? `<div class="urgent"><span class="k">where to look · ${esc(u.reason)}${u.subArea?(' · '+esc(u.subArea)):''}</span>${u.next?esc(u.next):'<span class="none">no next-action set</span>'}</div>`
    : `<div class="urgent"><span class="k">where to look</span><span class="none">all current · no flags</span></div>`;
  const glink = d.graph
    ? (d.graph.exists
        ? `<span class="glink" onclick="event.stopPropagation();openGraph('${esc(d.graph.html)}')">&#9638; code-graph</span>`
        : `<span class="glink off">&#9638; no graph</span>`)
    : `<span class="glink off">&mdash;</span>`;
  return `<div class="card click ${d.kind==='meta'?'meta':''}" onclick="showDetail('${d.domain}')">
    <div class="c-top">
      <div><div class="dname">${esc(d.domain)}</div><div class="dtag">${esc(d.title)}</div></div>
      <span class="health ${d.healthStatus==='green'?'healthy':d.healthStatus==='amber'?'attention':'critical'}">${esc(d.health)}</span>
    </div>
    <div class="tally">${tally}</div>
    ${urgent}
    <div class="c-bot">${sparkline(d.rhythm)}${glink}</div>
  </div>`;
}

function subAreaCard(sa){
  const flags = [];
  if(sa.blocked) flags.push(`<span class="flag blocked">blocked</span>`);
  if(sa.parked)  flags.push(`<span class="flag parked">parked</span>`);
  flags.push(`<span class="flag kn">${sa.knowledgePopulated}/${sa.knowledgeFiles} knowledge</span>`);
  if(sa.hasSkills) flags.push(`<span class="flag sk">skills</span>`);
  const v = (x)=> x ? `<span class="v">${esc(x)}</span>` : `<span class="v empty">&mdash; not set</span>`;
  return `<div class="sa">
    <h4>${dot(sa.freshness)}${esc(sa.subArea||'(flat)')}</h4>
    <div class="age">${sa.lastUpdated?('updated '+esc(sa.lastUpdated.replace('T',' '))+' · '+sa.ageDays+'d'):'never'}</div>
    <div class="row"><span class="k">state · current focus</span>${v(sa.state)}</div>
    <div class="row"><span class="k">next action</span>${v(sa.next)}</div>
    ${sa.blocked?`<div class="row"><span class="k">blocked</span><span class="v">${esc(sa.blockedText)}</span></div>`:''}
    <div class="flags">${flags.join('')}</div>
  </div>`;
}

function showOverview(){
  document.getElementById('overview').style.display='';
  document.getElementById('detail').style.display='none';
  window.scrollTo(0,0);
}
function showDetail(id){
  const d = DATA.domains.find(x=>x.domain===id);
  const gbtn = d.graph && d.graph.exists
    ? `<span class="glink" onclick="openGraph('${esc(d.graph.html)}')">&#9638; open ${esc(d.graph.name)} code-graph</span>` : '';
  document.getElementById('detailbody').innerHTML =
    `<div class="d2head"><div class="dname">${esc(d.domain)}</div>
       <span class="health ${d.healthStatus==='green'?'healthy':d.healthStatus==='amber'?'attention':'critical'}">${esc(d.health)}</span>
       ${gbtn}</div>
     <div class="dtag" style="margin-bottom:16px">${esc(d.title)}${d.router?(' · '+esc(d.router)):''}</div>
     <div class="grid">${d.subAreas.map(subAreaCard).join('')}</div>`;
  document.getElementById('overview').style.display='none';
  document.getElementById('detail').style.display='';
  window.scrollTo(0,0);
}
function openGraph(rel){
  window.open('../../'+rel, '_blank');   // graph.html lives under the vault, relative to _system/dashboard/
}

function init(){
  document.getElementById('ovgrid').innerHTML = DATA.domains.map(domainCard).join('');
  document.getElementById('genline').textContent =
    'generated '+DATA.generatedAt.replace('T',' ')+' · phase '+DATA.phase+' · static · read-only';
  document.getElementById('metar').innerHTML =
    'fresh thresholds: <code>green&lt;'+DATA.freshnessThresholds.greenDays+'d · amber&le;'+DATA.freshnessThresholds.amberDays+'d</code><br>'+
    'vault: <code>'+esc(DATA.vaultPath)+'</code>';
  document.getElementById('foot').innerHTML =
    '<span>regenerate: <code>python3 _system/dashboard/extract_dashboard.py</code></span>'+
    '<span>read-only surface · writes only to _system/dashboard/ · triggers = phase 3</span>';
}
init();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
