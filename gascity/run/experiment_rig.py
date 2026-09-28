#!/usr/bin/env python3
"""Keep one rig in city.toml in the experiment shape.

Gas City rigs have no type field. An experiment rig is the convention this
script writes into the rig's [[rigs]] block: formulas_dir, no session cap,
a work directory per builder that has its own worktree, and a page directory
for the critique agents. factory.builder also gets the experiment prompt,
which reads docs/brief.md.
"""

import os
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
# Agents that each own one variant. coder.coder is absent on purpose: three
# mol formulas share it, so one work_dir cannot tell them apart.
BUILDER_WORKTREES = (
    ("onepage.builder", "onepage"),
    ("factory.builder", "factory"),
    ("impeccable-native.runner", "impeccable-build"),
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


def delete_scalar(preamble, key):
    import re

    return re.compile(rf"(?m)^{re.escape(key)}\s*=.*\n").sub("", preamble)


def patch_text(agent, work_dir, prompt):
    lines = [
        "[[rigs.patches]]",
        f'agent = "{agent}"',
        f"work_dir = {toml_str(work_dir)}",
    ]
    if prompt:
        lines.append(f"prompt_template = {toml_str(prompt)}")
    return "\n".join(lines) + "\n"


def upsert_patches(rest, worktree_root, score_dir, factory_prompt):
    import re

    wanted = []
    for agent, leaf in BUILDER_WORKTREES:
        prompt = factory_prompt if agent == "factory.builder" else None
        wanted.append((agent, os.path.join(worktree_root, leaf), prompt))
    for agent in CRITIQUE_AGENTS:
        wanted.append((agent, score_dir, None))
    for agent, work_dir, prompt in wanted:
        block = patch_text(agent, work_dir, prompt)
        pattern = re.compile(
            rf"\[\[rigs\.patches\]\]\nagent\s*=\s*\"{re.escape(agent)}\"\n(?:.*\n)*?(?=\[\[|\Z)"
        )
        if pattern.search(rest):
            rest = pattern.sub(block, rest, count=1)
        else:
            if rest and not rest.endswith("\n"):
                rest += "\n"
            rest += block
    return rest


def ensure_text(text, name, formulas_dir, score_dir, worktree_root, factory_prompt):
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
    preamble = delete_scalar(preamble, "max_active_sessions")
    rest = upsert_patches(rest, worktree_root, score_dir, factory_prompt)
    new_block = preamble + rest
    if not new_block.endswith("\n"):
        new_block += "\n"
    return text[:start] + new_block + text[end:]


def ensure_file(path, name, formulas_dir, score_dir, worktree_root, factory_prompt):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    updated = ensure_text(text, name, formulas_dir, score_dir, worktree_root, factory_prompt)
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
        'max_active_sessions = 1\n'
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
    first = ensure_text(other + experiment + tail, "experiment", "/formulas", "/score", "/wt", "/prompt.md")
    second = ensure_text(first, "experiment", "/formulas-2", "/score-2", "/wt-2", "/prompt-2.md")
    data = tomllib.loads(second)
    rigs = {rig["name"]: rig for rig in data["rigs"]}
    assert rigs["bakery"]["prefix"] == "ba", rigs["bakery"]
    assert "patches" not in rigs["bakery"]
    assert rigs["other"]["prefix"] == "ot"
    experiment_rig = rigs["experiment"]
    assert experiment_rig["formulas_dir"] == "/formulas-2"
    assert "max_active_sessions" not in experiment_rig
    assert list(experiment_rig["imports"]["impeccable-native"]) == ["source"]
    by_agent = {patch["agent"]: patch for patch in experiment_rig["patches"]}
    assert by_agent["onepage.builder"]["work_dir"] == "/wt-2/onepage"
    assert by_agent["factory.builder"]["work_dir"] == "/wt-2/factory"
    assert by_agent["factory.builder"]["prompt_template"] == "/prompt-2.md"
    assert "prompt_template" not in by_agent["onepage.builder"]
    assert by_agent["impeccable-native.runner"]["work_dir"] == "/wt-2/impeccable-build"
    for agent in CRITIQUE_AGENTS:
        assert by_agent[agent]["work_dir"] == "/score-2"
    try:
        ensure_text(other, "experiment", "/formulas", "/score", "/wt", "/prompt.md")
    except SystemExit as exc:
        assert "not in city.toml" in str(exc)
    else:
        raise SystemExit("missing rig should fail")
    print("experiment_rig self-test ok")


def main(argv):
    if len(argv) == 2 and argv[1] == "--self-test":
        self_test()
        return 0
    if len(argv) != 7:
        print(
            "usage: experiment_rig.py <city.toml> <rig-name> <formulas-dir> "
            "<score-dir> <worktree-root> <factory-prompt>",
            file=sys.stderr,
        )
        return 2
    ensure_file(argv[1], argv[2], argv[3], argv[4], argv[5], argv[6])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
