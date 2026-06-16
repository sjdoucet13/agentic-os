# Automations — Trigger Bindings

Binds skills (`_ops/skills/`) to triggers. **Trigger execution logic is deferred**
(roadmap) — this table fixes the shape now. Each row = one automation.

| Automation | Skill | Trigger (planned) | Target | Notes |
|---|---|---|---|---|
| capture-inbox | `capture` | dashboard button / hotkey | chosen domain | fast raw capture |
| morning-report | `status-report` | dashboard button (later: schedule) | `all` | the REPORT moment |
| graph-refresh-mad | `graph-refresh` | git post-commit on `mad-custom-tx` | `_graphs/mad-custom-tx/` | deferred: needs Graphify + hook |
| graph-refresh-zus | `graph-refresh` | git post-commit on `zus-legacy` | `_graphs/zus-legacy/` | deferred: needs Graphify + hook |

## Rules
- Automations run skills; they carry no domain knowledge themselves.
- Scheduled automations must use **external** scheduling (systemd/pm2), not Claude
  Code's session cron, so they survive session restarts (see roadmap).
- Any automation that writes must use atomic (temp-then-rename) writes.
