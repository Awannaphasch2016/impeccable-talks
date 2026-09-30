#!/usr/bin/env python3
"""City check script for the approval formula.

The control dispatcher runs this after the shell iteration closes. It writes
one file for the step and does not start a session. gc.step_id selects the
file: plan -> plan.txt, review -> review.txt, finish -> done.txt. The run
directory is gc.var.run on the workflow root.
"""

import json
import os
import subprocess
import sys

FILES = {
    "plan": "plan.txt",
    "review": "review.txt",
    "finish": "done.txt",
}


def parse_json(raw):
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw):
        if char not in "{[":
            continue
        try:
            value, _end = decoder.raw_decode(raw[index:])
        except json.JSONDecodeError:
            continue
        return value
    raise SystemExit(raw.strip() or "bd show returned no JSON")


def as_bead(data):
    if isinstance(data, list):
        if not data:
            raise SystemExit("bd show returned no bead")
        return data[0]
    return data


def show(bead_id, project):
    result = subprocess.run(
        ["bd", "show", bead_id, "--json"],
        check=True,
        capture_output=True,
        text=True,
        cwd=project or None,
    )
    return as_bead(parse_json(result.stdout))


def meta(bead):
    value = bead.get("metadata") or {}
    if not isinstance(value, dict):
        return {}
    return {str(key): "" if item is None else str(item) for key, item in value.items()}


def main():
    bead_id = os.environ.get("GC_BEAD_ID", "").strip()
    if not bead_id:
        raise SystemExit("GC_BEAD_ID is empty")
    beads_dir = os.environ.get("BEADS_DIR", "").strip()
    if not beads_dir:
        raise SystemExit("BEADS_DIR is empty")
    project = os.path.dirname(beads_dir)
    bead = show(bead_id, project)
    fields = meta(bead)
    step = fields.get("gc.step_id", "")
    filename = FILES.get(step)
    if filename is None:
        raise SystemExit(f"gc.step_id {step!r} is not a shell write")
    root_id = fields.get("gc.root_bead_id", "")
    if not root_id:
        raise SystemExit(f"{bead_id} has no gc.root_bead_id")
    run = meta(show(root_id, project)).get("gc.var.run", "")
    if not run or run in {".", ".."} or "/" in run or "\\" in run:
        raise SystemExit(f"gc.var.run {run!r} is not a single directory name")
    destination = os.path.join(project, run, filename)
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, "w", encoding="utf-8") as handle:
        handle.write(run + "\n")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or "")
        sys.stderr.write(exc.stdout or "")
        raise SystemExit(exc.returncode or 1)
