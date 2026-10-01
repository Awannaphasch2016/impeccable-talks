#!/usr/bin/env python3
"""Human routing for the experiment rig's approval formula.

pending lists open human gates whose other needs are already closed, joins
each gate to the role in routes.toml, and prints the members who hold that
role. respond checks the member's role and is the only caller of
bd gate resolve. A member without the role exits non-zero and does not
resolve. Gate assignees stay empty. The approver is the --reason text and,
when bd accepts it, the process actor. respond prints which of those the
close event actually stored.

release closes a ready shell iteration that has no assignee and asks the
city control dispatcher to run that step's check. It does not resolve gates.

shield removes pool routing from the workflow root, the human gates, the
gate steps, and the shell iterations so a claim cannot stamp .assignee.
Ralph controls stay routed to the control dispatcher.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CITY = os.environ.get("GC_CITY_PATH", "/opt/gascity/city")
PROJECTS = os.environ.get("PROJECTS", "/opt/gascity/projects")
RIG = os.environ.get("RIG", "experiment")
PROJECT = os.path.join(PROJECTS, RIG)
SHELL_STEPS = ("plan", "review", "finish")
GATE_STEPS = ("plan-approve", "review-approve-dev", "review-approve-pm")
# Pool claim reads gc.routed_to and then stamps .assignee. These are the
# keys ApplyGraphRouteBinding writes. Ralph controls keep theirs so the
# control dispatcher can still run the check.
ROUTE_KEYS = (
    "gc.routed_to",
    "gc.execution_routed_to",
    "gc.session_id",
    "gc.sessionId",
    "gc.session_name",
    "gc.sessionName",
)


def load_simple_toml(path):
    """Read the assignment tables these two files use. The city host is Python 3.10."""
    data = {}
    table = data
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                table = data
                for key in line[1:-1].split("."):
                    table = table.setdefault(key, {})
                continue
            if "=" not in line:
                raise SystemExit(f"{path}: cannot read {raw.rstrip()}")
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                items = []
                if inner:
                    items = [part.strip().strip('"').strip("'") for part in inner.split(",")]
                table[key] = items
            else:
                table[key] = value.strip('"').strip("'")
    return data


def org_roles():
    loaded = load_simple_toml(os.path.join(HERE, "org.toml"))
    members = loaded.get("members") or {}
    roles = {}
    for name, body in members.items():
        held = body.get("roles") if isinstance(body, dict) else []
        roles[name] = list(held or [])
    return roles


def routes():
    loaded = load_simple_toml(os.path.join(HERE, "routes.toml"))
    table = loaded.get("routes") or {}
    return {str(key): str(value) for key, value in table.items()}


def eligible(member, role, members):
    return role in members.get(member, [])


def run_bd(args, check=True):
    result = subprocess.run(
        ["bd", *args],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.stderr.write(result.stdout)
        raise SystemExit(result.returncode or 1)
    return result


def parse_json(raw):
    """First JSON value in bd output. Later text is a warning, not more JSON."""
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw):
        if char not in "{[":
            continue
        try:
            value, _end = decoder.raw_decode(raw[index:])
        except json.JSONDecodeError:
            continue
        return value
    return None


def as_list(data):
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return [data]


def bead_meta(bead):
    value = bead.get("metadata") or {}
    if not isinstance(value, dict):
        return {}
    return {str(key): "" if item is None else str(item) for key, item in value.items()}


def bead_id(bead):
    return str(bead.get("id") or "")


def bead_status(bead):
    return str(bead.get("status") or "")


def bead_assignee(bead):
    return str(bead.get("assignee") or "").strip()


def show_bead(bead_id_value):
    result = run_bd(["show", bead_id_value, "--json"])
    beads = as_list(parse_json(result.stdout))
    if not beads:
        raise SystemExit(f"bd show {bead_id_value} returned no bead")
    return beads[0]


def list_beads():
    # Gate issues are omitted unless --include-gates is set. --flat keeps
    # every row in one array, including blocked and closed beads.
    result = run_bd(
        ["list", "--all", "--include-gates", "--flat", "--json", "--limit", "0"],
    )
    found = {}
    for bead in as_list(parse_json(result.stdout)):
        identity = bead_id(bead)
        if identity:
            found[identity] = bead
    return list(found.values())


def bead_ref(bead):
    return str(bead.get("ref") or bead_meta(bead).get("ref") or "")


def workflow_beads(run):
    beads = list_beads()
    roots = []
    for bead in beads:
        fields = bead_meta(bead)
        if fields.get("gc.var.run") != run:
            continue
        ref = bead_ref(bead)
        if ref not in {"", "approval"} and not ref.startswith("approval."):
            continue
        roots.append(bead)
    root_ids = {bead_id(bead) for bead in roots}
    selected = []
    for bead in beads:
        identity = bead_id(bead)
        fields = bead_meta(bead)
        in_run = identity in root_ids or fields.get("gc.root_bead_id") in root_ids
        if not in_run:
            in_run = any(identity.startswith(root + ".") for root in root_ids)
        if in_run:
            selected.append(show_bead(identity))
    if not selected:
        raise SystemExit(f"no approval workflow for run {run}")
    return selected


def step_key(bead):
    fields = bead_meta(bead)
    if fields.get("gc.step_id"):
        return fields["gc.step_id"]
    ref = str(bead.get("ref") or "")
    if ref.startswith("approval."):
        ref = ref[len("approval."):]
    if ".gate-" in ref:
        return ref.rsplit(".gate-", 1)[-1]
    if ".iteration." in ref:
        return ref.split(".iteration.", 1)[0]
    return ref


def is_iteration(bead):
    fields = bead_meta(bead)
    ref = fields.get("gc.step_ref") or str(bead.get("ref") or "")
    return ".iteration." in ref or bool(fields.get("gc.iteration"))


def is_gate_bead(bead):
    issue_type = str(bead.get("issue_type") or bead.get("type") or "")
    await_type = str(bead.get("await_type") or bead_meta(bead).get("await_type") or "")
    title = str(bead.get("title") or "")
    description = str(bead.get("description") or "")
    if await_type == "human":
        return True
    if issue_type == "gate":
        return True
    if title.startswith("Gate:"):
        return True
    return description.startswith("Async gate for step ")


def gate_step(bead):
    description = str(bead.get("description") or "")
    prefix = "Async gate for step "
    if description.startswith(prefix):
        return description[len(prefix):].strip()
    title = str(bead.get("title") or "")
    if title.startswith("Gate:"):
        parts = title.split()
        if parts:
            return parts[-1]
    return step_key(bead)


def dep_records(bead_id_value, direction):
    result = run_bd(
        ["dep", "list", bead_id_value, f"--direction={direction}", "--json"],
    )
    data = parse_json(result.stdout)
    return [item for item in as_list(data) if isinstance(item, dict)]


def dep_status(record, known):
    status = str(record.get("status") or "")
    if status:
        return status
    identity = str(
        record.get("depends_on_id")
        or record.get("id")
        or record.get("issue_id")
        or ""
    )
    if identity in known:
        return bead_status(known[identity])
    if identity:
        try:
            return bead_status(show_bead(identity))
        except SystemExit:
            return ""
    return ""


def other_needs_closed(step_bead, gate_id, known):
    records = dep_records(bead_id(step_bead), "down")
    for record in records:
        dep_type = str(record.get("type") or record.get("dependency_type") or "")
        if dep_type not in {"blocks", "conditional-blocks", "waits-for"}:
            continue
        dependency = str(record.get("depends_on_id") or record.get("id") or "")
        if dependency == gate_id:
            continue
        if dep_status(record, known) != "closed":
            return False
    return True


def gated_steps(gate, known):
    """Steps this gate blocks. The blocks edge points from the step to the gate."""
    found = []
    for bead in known.values():
        if bead_id(bead) == bead_id(gate) or is_gate_bead(bead):
            continue
        for record in dep_records(bead_id(bead), "down"):
            dependency = str(record.get("depends_on_id") or record.get("id") or "")
            dep_type = str(record.get("type") or record.get("dependency_type") or "")
            if dep_type not in {"blocks", "conditional-blocks"}:
                continue
            if dependency == bead_id(gate):
                found.append(bead)
                break
    return found


def pending_gates(run):
    beads = workflow_beads(run)
    known = {bead_id(bead): bead for bead in beads}
    # List rows omit description. Show each open gate so the step id is readable.
    opened = []
    for bead in beads:
        if bead_status(bead) == "closed":
            continue
        if not is_gate_bead(bead):
            continue
        full = show_bead(bead_id(bead))
        known[bead_id(full)] = full
        opened.append(full)
    role_of = routes()
    members = org_roles()
    lines = []
    for gate in opened:
        if bead_status(gate) == "closed":
            continue
        step = gate_step(gate)
        if step not in role_of:
            continue
        waiters = gated_steps(gate, known)
        if not waiters:
            continue
        if not all(other_needs_closed(waiter, bead_id(gate), known) for waiter in waiters):
            continue
        if any(bead_status(waiter) == "closed" for waiter in waiters):
            continue
        role = role_of[step]
        names = sorted(name for name in members if eligible(name, role, members))
        lines.append((step, role, names, bead_id(gate)))
    lines.sort(key=lambda item: item[0])
    return lines


def command_pending(run):
    for step, role, names, _gate in pending_gates(run):
        print(f"step={step} role={role} members={','.join(names)}")


def close_event_text(gate):
    shown = run_bd(["show", gate, "--json"], check=False)
    history = run_bd(["history", gate, "--events"], check=False)
    comments = run_bd(["comments", gate, "--json"], check=False)
    parts = [
        shown.stdout,
        shown.stderr,
        history.stdout,
        history.stderr,
        comments.stdout,
        comments.stderr,
    ]
    return "\n".join(part for part in parts if part)


def record_close(member, gate, run):
    text = close_event_text(gate)
    reason_stored = f"approved by {member}" in text
    actor_stored = f"closed by {member}" in text.lower()
    for line in text.splitlines():
        lowered = line.lower()
        if member not in line:
            continue
        if "reason" in lowered or "approved by" in lowered:
            continue
        if "actor" in lowered or "user" in lowered or "closed_by" in lowered or "closed by" in lowered:
            actor_stored = True
    if not actor_stored:
        # A JSON event may store the actor in a field whose key is not on the
        # same line as the value. Accept a decoded object that names the member
        # outside the reason string.
        data = parse_json(text)
        blob = json.dumps(data) if data is not None else ""
        if f'"{member}"' in blob and f"approved by {member}" not in blob:
            actor_stored = True
    stored = []
    if reason_stored:
        stored.append("reason")
    if actor_stored:
        stored.append("actor")
    summary = ",".join(stored) if stored else "neither"
    print(f"close-record: {summary}")
    print(text.rstrip())
    beads_dir = os.path.join(PROJECT, ".beads")
    if os.path.isdir(os.path.dirname(beads_dir)):
        folder = os.path.join(PROJECT, run)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "close-record.txt"), "a", encoding="utf-8") as handle:
            handle.write(f"{gate} {member} stored={summary}\n")
    return reason_stored


def close_gate_step(gate, member, known):
    """Closing the gate unblocks its step. The step is not session work, so close it here."""
    for waiter in gated_steps(gate, known):
        if bead_status(waiter) == "closed":
            continue
        if bead_assignee(waiter):
            raise SystemExit(f"{bead_id(waiter)} has assignee {bead_assignee(waiter)}")
        if step_key(waiter) not in GATE_STEPS:
            continue
        result = run_bd(
            [
                "--actor",
                member,
                "close",
                bead_id(waiter),
                "--reason",
                f"approved by {member}; the gate step has no session assignee",
            ],
            check=False,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            raise SystemExit(result.returncode or 1)


def command_respond(member, step, run):
    members = org_roles()
    if member not in members:
        sys.stderr.write(f"{member} is not in the organization\n")
        raise SystemExit(1)
    role = routes().get(step)
    if role is None:
        sys.stderr.write(f"{step} is not a routed gate\n")
        raise SystemExit(1)
    if not eligible(member, role, members):
        sys.stderr.write(f"{member} does not hold {role}\n")
        raise SystemExit(1)
    matches = [item for item in pending_gates(run) if item[0] == step]
    if not matches:
        sys.stderr.write(f"{step} is not pending for run {run}\n")
        raise SystemExit(1)
    _step, _role, _names, gate = matches[0]
    shown = show_bead(gate)
    if bead_assignee(shown):
        raise SystemExit(f"{gate} has assignee {bead_assignee(shown)}")
    result = run_bd(
        [
            "--actor",
            member,
            "gate",
            "resolve",
            gate,
            "--reason",
            f"approved by {member}",
        ],
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.stderr.write(result.stdout)
        raise SystemExit(result.returncode or 1)
    beads = workflow_beads(run)
    known = {bead_id(bead): bead for bead in beads}
    known[gate] = show_bead(gate)
    close_gate_step(gate, member, known)
    record_close(member, gate, run)
    print(f"resolved {step} as {member}")


def command_release(run):
    beads = workflow_beads(run)
    known = {bead_id(bead): bead for bead in beads}
    for step in SHELL_STEPS:
        iterations = [
            bead for bead in beads
            if step_key(bead) == step and is_iteration(bead) and bead_meta(bead).get("gc.kind") != "spec"
        ]
        controls = [
            bead for bead in beads
            if step_key(bead) == step and bead_meta(bead).get("gc.kind") == "ralph"
        ]
        for iteration in iterations:
            if bead_assignee(iteration):
                raise SystemExit(
                    f"{bead_id(iteration)} has session assignee {bead_assignee(iteration)}"
                )
            if bead_status(iteration) == "closed":
                continue
            if not other_needs_closed(iteration, "", known):
                continue
            result = run_bd(
                [
                    "close",
                    bead_id(iteration),
                    "--reason",
                    "City shell check runs after this unassigned iteration closes",
                ],
                check=False,
            )
            if result.returncode != 0:
                sys.stderr.write(result.stderr)
                raise SystemExit(result.returncode or 1)
            iteration["status"] = "closed"
        for control in controls:
            if bead_assignee(control):
                raise SystemExit(
                    f"{bead_id(control)} has session assignee {bead_assignee(control)}"
                )
            if bead_status(control) == "closed":
                print(f"released {step} already")
                continue
            if not any(bead_status(iteration) == "closed" for iteration in iterations):
                continue
            result = subprocess.run(
                ["gc", "--city", CITY, "--rig", RIG, "convoy", "control", bead_id(control)],
                cwd=CITY,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                sys.stderr.write(result.stderr)
                sys.stderr.write(result.stdout)
                raise SystemExit(result.returncode or 1)
            print(f"released {step}")


def command_shield(run):
    """Drop pool routing from gates, gate steps, shell iterations, and the root.

    A sling to a pool agent leaves gc.routed_to set and .assignee empty until
    a slot claims the bead. Gate beads are type gate, so a claim can set
    .assignee. Shell iterations and the workflow root are the same kind of
    claim. Ralph controls stay routed to the control dispatcher.
    """
    for bead in workflow_beads(run):
        fields = bead_meta(bead)
        if fields.get("gc.kind") == "ralph":
            continue
        step = step_key(bead)
        root_id = fields.get("gc.root_bead_id")
        root = fields.get("gc.var.run") == run and (not root_id or root_id == bead_id(bead))
        watch = (
            root
            or is_gate_bead(bead)
            or step in GATE_STEPS
            or (step in SHELL_STEPS and is_iteration(bead))
        )
        if not watch:
            continue
        present = [key for key in ROUTE_KEYS if fields.get(key)]
        if not present:
            print(f"shield {bead_id(bead)} already")
            continue
        args = ["update", bead_id(bead)]
        for key in present:
            args.extend(["--unset-metadata", key])
        run_bd(args)
        print(f"shield {bead_id(bead)}")


def command_audit(run):
    failed = False
    for bead in workflow_beads(run):
        step = step_key(bead)
        watched = step in SHELL_STEPS or step in GATE_STEPS or is_gate_bead(bead)
        if not watched:
            continue
        assignee = bead_assignee(bead)
        if not assignee:
            full = show_bead(bead_id(bead))
            assignee = bead_assignee(full)
        if assignee:
            sys.stderr.write(f"{bead_id(bead)} {step} assignee={assignee}\n")
            failed = True
    if failed:
        raise SystemExit(1)


def main():
    if not os.path.isdir(PROJECT):
        raise SystemExit(f"{PROJECT} does not exist")
    parser = argparse.ArgumentParser(description="Route approval gates on the experiment rig")
    sub = parser.add_subparsers(dest="command", required=True)
    pending = sub.add_parser("pending")
    pending.add_argument("--run", required=True)
    respond = sub.add_parser("respond")
    respond.add_argument("--as", dest="member", required=True)
    respond.add_argument("--step", required=True)
    respond.add_argument("--run", required=True)
    release = sub.add_parser("release")
    release.add_argument("--run", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("--run", required=True)
    shield = sub.add_parser("shield")
    shield.add_argument("--run", required=True)
    args = parser.parse_args()
    if args.command == "pending":
        command_pending(args.run)
    elif args.command == "respond":
        command_respond(args.member, args.step, args.run)
    elif args.command == "release":
        command_release(args.run)
    elif args.command == "audit":
        command_audit(args.run)
    elif args.command == "shield":
        command_shield(args.run)


if __name__ == "__main__":
    main()
