#!/usr/bin/env python3
"""Keep one rig in city.toml in the experiment shape.

Gas City rigs have no type field. An experiment rig is the convention this
script writes into the rig's [[rigs]] block: formulas_dir, a single active
session, and a page-only work directory for the three critique agents.
"""

import sys

REQUIRED_IMPORTS = (
    "onepage",
    "factory",
    "coder",
    "impeccable",
    "impeccable-native",
)
CRITIQUE_AGENTS = (
    "impeccable.conductor",
    "impeccable.design-reviewer",
    "impeccable.evidence-collector",
)


def toml_str(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def rig_spans(text):
    import re

    starts = [m.start() for m in re.finditer(r"(?m)^\[\[rigs\]\][ \t]*$", text)]
    spans = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        spans.append((start, end))
    return spans


def block_name(block):
    import re

    match = re.search(r'(?m)^name\s*=\s*"([^"]+)"\s*$', block)
    return match.group(1) if match else ""


def split_preamble(block):
    """Separate the rig's own keys from the nested tables that follow.

    A key written after [rigs.imports.*] belongs to that import, not the rig.
    """
    lines = block.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if i == 0:
            continue
        stripped = line.strip()
        if stripped.startswith("["):
            return "".join(lines[:i]), "".join(lines[i:])
    return block, ""


def upsert_scalar(preamble, key, rendered):
    import re

    line = f"{key} = {rendered}\n"
    pattern = re.compile(rf"(?m)^{re.escape(key)}\s*=.*\n")
    if pattern.search(preamble):
        return pattern.sub(line, preamble, count=1)
    if preamble and not preamble.endswith("\n"):
        preamble += "\n"
    return preamble + line


def upsert_patches(rest, score_dir):
    import re

    rendered = toml_str(score_dir)
    for agent in CRITIQUE_AGENTS:
        pattern = re.compile(
            rf"\[\[rigs\.patches\]\]\nagent\s*=\s*\"{re.escape(agent)}\"\nwork_dir\s*=\s*\".*\"\n"
        )
        repl = f'[[rigs.patches]]\nagent = "{agent}"\nwork_dir = {rendered}\n'
        if pattern.search(rest):
            rest = pattern.sub(repl, rest, count=1)
        else:
            if rest and not rest.endswith("\n"):
                rest += "\n"
            rest += repl
    return rest


def ensure_text(text, name, formulas_dir, score_dir):
    match = None
    for start, end in rig_spans(text):
        block = text[start:end]
        if block_name(block) == name:
            match = (start, end, block)
            break
    if match is None:
        raise SystemExit(f"rig {name!r} is not in city.toml; register it before patching")
    start, end, block = match
    missing = [binding for binding in REQUIRED_IMPORTS if f"[rigs.imports.{binding}]" not in block]
    if missing:
        raise SystemExit(
            f"rig {name} is missing imports: {', '.join(missing)}. "
            "Remove it and let run-matrix.sh register it with every builder pack."
        )
    preamble, rest = split_preamble(block)
    preamble = upsert_scalar(preamble, "formulas_dir", toml_str(formulas_dir))
    preamble = upsert_scalar(preamble, "max_active_sessions", "1")
    rest = upsert_patches(rest, score_dir)
    new_block = preamble + rest
    if not new_block.endswith("\n"):
        new_block += "\n"
    return text[:start] + new_block + text[end:]


def ensure_file(path, name, formulas_dir, score_dir):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    updated = ensure_text(text, name, formulas_dir, score_dir)
    if updated != text:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)


def self_test():
    import tomllib

    other = (
        '[[rigs]]\n'
        'name = "bakery"\n'
        'prefix = "ba"\n'
        '[rigs.imports]\n'
        '[rigs.imports.factory]\n'
        'source = "/opt/gascity/packs/factory"\n'
        '\n'
    )
    experiment = (
        '[[rigs]]\n'
        'name = "experiment"\n'
        'prefix = "xpr"\n'
        'default_branch = "main"\n'
        '[rigs.imports]\n'
        '[rigs.imports.onepage]\n'
        'source = "/opt/gascity/packs/onepage"\n'
        '[rigs.imports.factory]\n'
        'source = "/opt/gascity/packs/factory"\n'
        '[rigs.imports.coder]\n'
        'source = "/opt/gascity/packs/coder"\n'
        '[rigs.imports.impeccable]\n'
        'source = "/opt/gascity/packs/impeccable"\n'
        '[rigs.imports.impeccable-native]\n'
        'source = "/opt/gascity/packs/impeccable-native"\n'
        '\n'
    )
    tail = '[[rigs]]\nname = "other"\nprefix = "ot"\n'
    first = ensure_text(other + experiment + tail, "experiment", "/formulas", "/score")
    second = ensure_text(first, "experiment", "/formulas-2", "/score-2")
    data = tomllib.loads(second)
    rigs = {rig["name"]: rig for rig in data["rigs"]}
    assert rigs["bakery"]["prefix"] == "ba", rigs["bakery"]
    assert "patches" not in rigs["bakery"]
    assert rigs["other"]["prefix"] == "ot"
    experiment_rig = rigs["experiment"]
    assert experiment_rig["formulas_dir"] == "/formulas-2"
    assert experiment_rig["max_active_sessions"] == 1
    assert list(experiment_rig["imports"]["impeccable-native"]) == ["source"]
    agents = [patch["agent"] for patch in experiment_rig["patches"]]
    assert agents == list(CRITIQUE_AGENTS), agents
    assert {patch["work_dir"] for patch in experiment_rig["patches"]} == {"/score-2"}
    try:
        ensure_text(other, "experiment", "/formulas", "/score")
    except SystemExit as exc:
        assert "not in city.toml" in str(exc)
    else:
        raise SystemExit("missing rig should fail")
    print("experiment_rig self-test ok")


def main(argv):
    if len(argv) == 2 and argv[1] == "--self-test":
        self_test()
        return 0
    if len(argv) != 5:
        print(
            "usage: experiment_rig.py <city.toml> <rig-name> <formulas-dir> <score-dir>",
            file=sys.stderr,
        )
        return 2
    ensure_file(argv[1], argv[2], argv[3], argv[4])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
