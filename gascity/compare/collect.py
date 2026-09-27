#!/usr/bin/env python3
"""Compare one Impeccable critique run per arm on a Gas City host.

    collect.py --arm native:<workflow-id>:<project-dir> --arm pack:<workflow-id>:<project-dir> \
               [--city /opt/gascity/city] [--api http://127.0.0.1:8372/v0/city/factory] \
               [--since 2026-09-27T15:50:00Z] [--json out.json]

For each arm it reads three sources that already exist on the host:

  * the city's event stream (.gc/events.jsonl) for step start/close times and
    which session ran which step;
  * the step beads through the supervisor API for outcome and close notes;
  * Claude Code's own transcripts under ~/.claude/projects/<cwd-slug>/,
    including sub-agent transcripts, for tokens, tool calls, models, and the
    set of files each conversation read or wrote.

The last one is what makes the isolation claim checkable: a conversation that
never issued a Read on assessment-b.md never saw it, whatever the prompt said.

Runs anywhere python3 is; no third-party packages.
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

ISO = "%Y-%m-%dT%H:%M:%S"

# Files the critique workflow passes between agents. Who may read which one is
# the isolation contract the pack claims to enforce.
WORKFLOW_FILES = ("packet.md", "assessment-a.md", "assessment-b.md", "report.md")
ROLE_BY_WRITE = {
    "packet.md": "conductor (prepare)",
    "assessment-a.md": "design-reviewer",
    "assessment-b.md": "evidence-collector",
    "report.md": "conductor (synthesize) / runner",
}
FORBIDDEN = {
    "design-reviewer": {"assessment-b.md", "report.md"},
    "evidence-collector": {"assessment-a.md", "report.md"},
    "conductor (prepare)": {"assessment-a.md", "assessment-b.md", "report.md"},
}


def parse_ts(value):
    if not value:
        return None
    value = value.rstrip("Z")
    if "." in value:
        head, frac = value.split(".", 1)
        value = f"{head}.{frac[:6]}"
        fmt = ISO + ".%f"
    else:
        fmt = ISO
    try:
        return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def api_get(base, path):
    req = urllib.request.Request(f"{base}{path}", headers={"X-GC-Request": "1"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def cwd_slug(project_dir):
    return os.path.abspath(project_dir).replace("/", "-")


def load_events(city, run_id, since):
    steps = defaultdict(dict)
    sessions = set()
    path = os.path.join(city, ".gc", "events.jsonl")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = parse_ts(ev.get("ts") or ev.get("time"))
            if since and ts and ts < since:
                continue
            kind = ev.get("type") or ev.get("kind")
            if kind == "execution.step_started" and ev.get("run_id") == run_id:
                sid = ev["step_id"]
                steps[sid]["bead"] = ev.get("subject")
                steps[sid]["started"] = ts
                steps[sid]["session"] = ev.get("session_id")
                steps[sid]["actor"] = ev.get("actor")
                steps[sid]["depends_on"] = ev.get("depends_on_step_ids") or []
                sessions.add(ev.get("session_id"))
            elif kind == "bead.updated":
                payload = ev.get("payload") or {}
                meta = payload.get("metadata") or {}
                if meta.get("gc.root_bead_id") == run_id and payload.get("status") == "closed":
                    sid = meta.get("gc.step_ref") or payload.get("id")
                    for k, v in steps.items():
                        if v.get("bead") == payload.get("id"):
                            sid = k
                    steps[sid].setdefault("bead", payload.get("id"))
                    if "closed" not in steps[sid]:
                        steps[sid]["closed"] = ts
    return steps, sessions


def enrich_steps(api, steps):
    for sid, st in steps.items():
        bead = st.get("bead")
        if not bead:
            continue
        try:
            b = api_get(api, f"/bead/{bead}")
        except Exception as exc:  # noqa: BLE001
            st["error"] = str(exc)
            continue
        meta = b.get("metadata") or {}
        st["status"] = b.get("status")
        st["outcome"] = meta.get("gc.outcome")
        st["note"] = meta.get("impeccable.note") or meta.get("factory.note")
        st["run_target"] = meta.get("gc.run_target")
        st["title"] = b.get("title")


def read_transcript(path):
    usage = Counter()
    tools = Counter()
    files_read, files_written = set(), set()
    models = Counter()
    first, last = None, None
    turns = 0
    task_prompts = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = parse_ts(e.get("timestamp"))
            if ts:
                first = ts if first is None or ts < first else first
                last = ts if last is None or ts > last else last
            msg = e.get("message") or {}
            if e.get("type") == "assistant":
                turns += 1
                u = msg.get("usage") or {}
                for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
                    usage[k] += int(u.get(k) or 0)
                if msg.get("model"):
                    models[msg["model"]] += 1
                for block in msg.get("content") or []:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name = block.get("name", "?")
                    tools[name] += 1
                    inp = block.get("input") or {}
                    if name in ("Read", "Glob", "Grep") and inp.get("file_path" if name == "Read" else "path"):
                        files_read.add(inp.get("file_path") or inp.get("path"))
                    if name in ("Write", "Edit", "MultiEdit", "NotebookEdit") and inp.get("file_path"):
                        files_written.add(inp["file_path"])
                    if name == "Bash":
                        cmd = inp.get("command", "")
                        written_here = None
                        # step.sh result and heredocs are the pack's write path.
                        if "step.sh" in cmd and " result " in cmd:
                            rest = cmd.split(" result ", 1)[1].split()
                            written_here = rest[1] if len(rest) > 1 else "?"
                            files_written.add(f"(step.sh result) {written_here}")
                        for token in cmd.replace("'", " ").replace('"', " ").replace(";", " ").split():
                            base = os.path.basename(token)
                            if base in WORKFLOW_FILES and base != written_here:
                                files_read.add(f"(bash) {base}")
                            elif token.endswith("*.md") and (".impeccable/gc" in token or "$WORK" in token or "WORK" in token):
                                files_read.add("(bash) *.md (every workflow file)")
                    if name in ("Task", "Agent"):
                        task_prompts.append({
                            "subagent_type": inp.get("subagent_type"),
                            "description": inp.get("description"),
                            "prompt_chars": len(inp.get("prompt") or ""),
                        })
    return {
        "path": path,
        "is_subagent": "/subagents/" in path,
        "first": first,
        "last": last,
        "assistant_turns": turns,
        "usage": dict(usage),
        "tools": dict(tools),
        "models": dict(models),
        "files_read": sorted(files_read),
        "files_written": sorted(files_written),
        "task_calls": task_prompts,
    }


def transcripts_for(project_dir, since):
    root = os.path.join(os.path.expanduser("~"), ".claude", "projects", cwd_slug(project_dir))
    out = []
    for path in glob.glob(os.path.join(root, "**", "*.jsonl"), recursive=True):
        mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
        if since and mtime < since:
            continue
        t = read_transcript(path)
        if t["assistant_turns"] == 0:
            continue
        sidecar = path + ".gcmeta"
        if os.path.exists(sidecar):
            with open(sidecar, encoding="utf-8") as fh:
                t["gc_session"] = fh.read().strip()
        out.append(t)
    out.sort(key=lambda t: t["first"] or datetime.max.replace(tzinfo=timezone.utc))
    return out


def workflow_files(project_dir, run_id):
    d = os.path.join(project_dir, ".impeccable", "gc", run_id)
    files = {}
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as fh:
                    files[name] = fh.read()
    snapshots = sorted(glob.glob(os.path.join(project_dir, ".impeccable", "critique", "*.md")))
    return files, snapshots


def role_of(t):
    for name, role in ROLE_BY_WRITE.items():
        if any(name in w for w in t["files_written"]):
            return role
    return "sub-agent" if t["is_subagent"] else "session"


def workflow_touches(t):
    touched = set()
    for p in list(t["files_read"]):
        base = os.path.basename(p.replace("(bash) ", ""))
        if base in WORKFLOW_FILES:
            touched.add(base)
        if "every workflow file" in p:
            touched.update(WORKFLOW_FILES)
    return touched


def orchestration_gaps(steps):
    """Seconds between a step's last dependency closing and the step starting."""
    gaps = {}
    for sid, st in steps.items():
        deps = st.get("depends_on") or []
        if not deps or not st.get("started"):
            continue
        closes = [steps[d]["closed"] for d in deps if d in steps and steps[d].get("closed")]
        if len(closes) == len(deps):
            gaps[sid] = (st["started"] - max(closes)).total_seconds()
    return gaps


def fmt_dt(a, b):
    if not a or not b:
        return "-"
    return f"{(b - a).total_seconds():.0f}s"


def summarize(arm):
    total = Counter()
    tools = Counter()
    for t in arm["transcripts"]:
        total.update(t["usage"])
        tools.update(t["tools"])
    firsts = [t["first"] for t in arm["transcripts"] if t["first"]]
    lasts = [t["last"] for t in arm["transcripts"] if t["last"]]
    return {
        "conversations": len(arm["transcripts"]),
        "subagent_conversations": sum(1 for t in arm["transcripts"] if t["is_subagent"]),
        "assistant_turns": sum(t["assistant_turns"] for t in arm["transcripts"]),
        "usage": dict(total),
        "tools": dict(tools),
        "task_calls": sum(len(t["task_calls"]) for t in arm["transcripts"]),
        "wall": fmt_dt(min(firsts), max(lasts)) if firsts and lasts else "-",
        "orchestration_gap_s": round(sum(orchestration_gaps(arm["steps"]).values())),
        "step_work_s": round(sum((s["closed"] - s["started"]).total_seconds() for s in arm["steps"].values() if s.get("started") and s.get("closed"))),
    }


def parse_verdict(report):
    """Pull the comparable numbers out of a conductor report.md.

    The total line is the synthesized score. Priority counts come from the
    tagged issue headings. Detector findings are whatever count the report
    states; a report that never mentions findings leaves the cell blank.
    """
    total = maximum = None
    match = re.search(r"\*\*(\d+)\s*/\s*(\d+)\*\*", report)
    if match:
        total, maximum = int(match.group(1)), int(match.group(2))
    priorities = Counter(re.findall(r"\*\*\[P([0-3])\]", report))
    findings = None
    found = re.search(r"(\d+)\s+(?:findings|warnings)", report, re.IGNORECASE)
    if found:
        findings = int(found.group(1))
    return {
        "total": total,
        "max": maximum,
        "priorities": priorities,
        "findings": findings,
    }


def render_scoreboard(arms):
    """One row per critique. The verdict is report.md, not the reviewer draft."""
    lines = [
        "# Builder scoreboard",
        "",
        "Each row is one Impeccable critique of a page a builder produced. "
        "The score is the conductor's report. A difference of one heuristic "
        "is within the swing already seen on a single unchanged page.",
        "",
        "| Arm | Score | Percent | P0 | P1 | P2 | P3 | Detector findings | Critique wall | Output tokens |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for arm in arms:
        verdict = parse_verdict(arm["files"].get("report.md", ""))
        if verdict["total"] is None or not verdict["max"]:
            score, percent = "-", "-"
        else:
            score = f"{verdict['total']}/{verdict['max']}"
            percent = f"{round(100 * verdict['total'] / verdict['max'])}%"
        pri = verdict["priorities"]
        findings = "-" if verdict["findings"] is None else str(verdict["findings"])
        lines.append(
            f"| {arm['name']} | {score} | {percent} | "
            f"{pri.get('0', 0)} | {pri.get('1', 0)} | {pri.get('2', 0)} | {pri.get('3', 0)} | "
            f"{findings} | {arm['summary']['wall']} | {arm['summary']['usage'].get('output_tokens', 0):,} |"
        )
    lines.append("")
    return "\n".join(lines)


def render(arms):
    lines = ["# Impeccable critique: native Claude sub-agents vs Gas City pack", ""]
    lines.append("| Metric | " + " | ".join(a["name"] for a in arms) + " |")
    lines.append("|---|" + "---|" * len(arms))
    rows = [
        ("Workflow", lambda a: a["run_id"]),
        ("Steps (closed/total)", lambda a: f"{sum(1 for s in a['steps'].values() if s.get('closed'))}/{len(a['steps'])}"),
        ("Wall clock (first to last transcript entry)", lambda a: a["summary"]["wall"]),
        ("Claude conversations", lambda a: str(a["summary"]["conversations"])),
        ("  of which Task sub-agents", lambda a: str(a["summary"]["subagent_conversations"])),
        ("Task tool calls", lambda a: str(a["summary"]["task_calls"])),
        ("Assistant turns", lambda a: str(a["summary"]["assistant_turns"])),
        ("Sum of step durations", lambda a: f"{a['summary']['step_work_s']}s"),
        ("Orchestration gap (dep closed to step started)", lambda a: f"{a['summary']['orchestration_gap_s']}s"),
        ("Input tokens (uncached)", lambda a: f"{a['summary']['usage'].get('input_tokens', 0):,}"),
        ("Cache write tokens", lambda a: f"{a['summary']['usage'].get('cache_creation_input_tokens', 0):,}"),
        ("Cache read tokens", lambda a: f"{a['summary']['usage'].get('cache_read_input_tokens', 0):,}"),
        ("Output tokens", lambda a: f"{a['summary']['usage'].get('output_tokens', 0):,}"),
        ("Total input incl. cache", lambda a: f"{sum(a['summary']['usage'].get(k, 0) for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens')):,}"),
        ("Tool calls", lambda a: str(sum(a["summary"]["tools"].values()))),
        ("report.md produced", lambda a: "yes" if "report.md" in a["files"] else "no"),
        ("Snapshots in .impeccable/critique", lambda a: str(len(a["snapshots"]))),
    ]
    for label, fn in rows:
        lines.append(f"| {label} | " + " | ".join(fn(a) for a in arms) + " |")
    lines.append("")

    for a in arms:
        lines.append(f"## {a['name']} ({a['run_id']})")
        lines.append("")
        lines.append("### Steps")
        lines.append("")
        lines.append("| Step | Agent | Started | Duration | Outcome | Note |")
        lines.append("|---|---|---|---|---|---|")
        for sid, st in sorted(a["steps"].items(), key=lambda kv: kv[1].get("started") or datetime.max.replace(tzinfo=timezone.utc)):
            lines.append(
                f"| {sid} | {st.get('run_target') or st.get('actor') or '-'} | "
                f"{st['started'].strftime('%H:%M:%S') if st.get('started') else '-'} | "
                f"{fmt_dt(st.get('started'), st.get('closed'))} | {st.get('outcome') or st.get('status') or '-'} | "
                f"{(st.get('note') or '').replace('|', '/')[:120]} |"
            )
        lines.append("")
        lines.append("### Conversations (Claude Code transcripts)")
        lines.append("")
        lines.append("| # | Role | Turns | In | Cache r/w | Out | Duration | Tools | Workflow files touched | Wrote |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for i, t in enumerate(a["transcripts"], 1):
            u = t["usage"]
            top_tools = ", ".join(f"{k}x{v}" for k, v in sorted(t["tools"].items(), key=lambda kv: -kv[1])[:5])
            lines.append(
                f"| {i} | {role_of(t)} | {t['assistant_turns']} | "
                f"{u.get('input_tokens', 0):,} | {u.get('cache_read_input_tokens', 0):,}/{u.get('cache_creation_input_tokens', 0):,} | "
                f"{u.get('output_tokens', 0):,} | {fmt_dt(t['first'], t['last'])} | {top_tools} | "
                f"{'; '.join(sorted(workflow_touches(t))) or '-'} | "
                f"{'; '.join(os.path.basename(p) for p in t['files_written']) or '-'} |"
            )
        lines.append("")
        audit = []
        for t in a["transcripts"]:
            role = role_of(t)
            forbidden = FORBIDDEN.get(role)
            if forbidden is None:
                continue
            leaked = sorted(workflow_touches(t) & forbidden)
            audit.append((role, leaked))
        if audit:
            lines.append("### Isolation audit")
            lines.append("")
            lines.append("Which workflow files each role's conversation actually opened (Read tool or shell), against what it was allowed to see.")
            lines.append("")
            for role, leaked in audit:
                verdict = f"read forbidden file(s): {', '.join(leaked)}" if leaked else "clean"
                lines.append(f"- {role}: {verdict}")
            lines.append("")
        gaps = orchestration_gaps(a["steps"])
        if gaps:
            lines.append("### Orchestration gaps")
            lines.append("")
            for sid, g in gaps.items():
                lines.append(f"- {sid}: started {g:.0f}s after its last dependency closed")
            lines.append("")
        if a["files"].get("report.md"):
            head = a["files"]["report.md"].strip().splitlines()
            lines.append("### report.md (first lines)")
            lines.append("")
            lines.append("```")
            lines.extend(head[:12])
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", required=True, help="name:workflow-id:project-dir")
    ap.add_argument("--city", default=os.environ.get("GC_CITY_PATH", "/opt/gascity/city"))
    ap.add_argument("--api", default=os.environ.get("IMPECCABLE_API", "http://127.0.0.1:8372/v0/city/factory"))
    ap.add_argument("--since", default=None, help="ISO timestamp; ignore events and transcripts older than this")
    ap.add_argument("--json", default=None, help="also write the raw collection here")
    ap.add_argument("--scoreboard", action="store_true",
                    help="print one row per arm from report.md instead of the full comparison")
    args = ap.parse_args()
    since = parse_ts(args.since) if args.since else None

    arms = []
    for spec in args.arm:
        name, run_id, project = spec.split(":", 2)
        steps, _ = load_events(args.city, run_id, since)
        enrich_steps(args.api, steps)
        files, snapshots = workflow_files(project, run_id)
        arm = {
            "name": name,
            "run_id": run_id,
            "project": project,
            "steps": steps,
            "transcripts": transcripts_for(project, since),
            "files": files,
            "snapshots": snapshots,
        }
        arm["summary"] = summarize(arm)
        arms.append(arm)

    body = render_scoreboard(arms) if args.scoreboard else render(arms)
    sys.stdout.write(body + "\n")
    if args.json:
        def default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return str(o)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(arms, fh, indent=2, default=default)


if __name__ == "__main__":
    main()
