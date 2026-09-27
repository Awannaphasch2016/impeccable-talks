# Impeccable on Gas City

A converter that turns [pbakaus/impeccable](https://github.com/pbakaus/impeccable)'s
Claude Code sub-agent system into a [Gas City](https://github.com/gastownhall/gascity)
pack, plus the rigs and collector used to compare the two ways of running the
same critique:

- **native**: one unrestricted Claude Code session with Impeccable's own
  `.claude/` build installed. The skill spawns Assessment A and B itself through
  Claude Code's `Agent` (Task) tool. Gas City is only the launcher.
- **pack**: the converted pack. Each role is a Gas City agent in its own tmux
  pane and Claude process; a formula does the fan-out and the join; files in a
  per-workflow directory are the only channel between them.

Impeccable itself adds nothing for Gas City; the mapping is done entirely here,
the way Impeccable's own `scripts/lib/transformers/` maps the skill onto Codex,
Cursor, Copilot and the rest.

## Layout

```
gascity/
  convert/
    impeccable-to-gascity.mjs   CLI (Node 18+, no dependencies)
    lib/text.mjs                provider blocks, placeholders, Go-template escaping, section slicing
    lib/agents.mjs              frontmatter -> agent record; tools -> --disallowedTools
    lib/emit.mjs                pack writer (pack.toml, agents/, formulas/, fragments, scripts, skill/)
    lib/claude.mjs              reproduces Impeccable's own .claude/ build for the native arm
    templates/                  fragment, synthetic agent prompts, formula, step.sh, baseline pack
  packs/
    impeccable/                 generated pack (7 agents, critique formula, compiled skill)
    impeccable-native/          generated baseline pack (1 agent) + claude-build/.claude
  run/setup-rigs.sh             host-side: two projects, two rigs, one critique each
  compare/collect.py            host-side: events + beads + Claude transcripts -> comparison
  compare/results/              one directory per comparison run, with both reports
```

## What maps to what

| Impeccable (Claude Code) | Gas City pack |
|---|---|
| the skill as a whole | one pack (`pack.toml`, schema 2) |
| `skill/agents/<name>.md` | `agents/<name>/agent.toml` + `prompt.template.md` |
| frontmatter `tools:` | `args = ["--disallowedTools", <every gated tool not listed>]`, enforced by Claude Code |
| frontmatter `effort:`, `model:` | `option_defaults = { effort, model }` |
| frontmatter `max-turns` | noted; a step is bounded by the formula's `timeout` instead |
| critique parent context, Setup half | `conductor` agent, step `prepare`, output `packet.md` |
| critique parent context, synthesis half | `conductor` agent, step `synthesize`, output `report.md` |
| Assessment A sub-agent | `design-reviewer` agent, step `assess-a`, output `assessment-a.md` |
| Assessment B sub-agent | `evidence-collector` agent, step `assess-b`, output `assessment-b.md` |
| "spawn A and B in parallel" | two steps with `needs = ["prepare"]`; the orchestrator routes both at once |
| Task tool return value | `step.sh result <id> <file>`; the next step reads the file |
| `AskUserQuestion` | tool disallowed; questions appended to `report.md` under `## Questions for the user` |
| `<claude>` / `<codex>` provider blocks | `<claude>` kept (the harness under Gas City is Claude Code), others dropped |
| `{{scripts_path}}`, `{{ask_instruction}}`, `{{command_prefix}}` | pack-local launcher path, unattended wording, `gc sling <rig>/impeccable.conductor <formula> --formula` |
| `~/.claude/projects/*.jsonl` | left in place; Gas City's `sessionlog` reads them, and so does `collect.py` |

The assessor and synthesis prompts are not rewritten. `lib/emit.mjs` slices the
`### Assessment A`, `### Assessment B`, `### Generate Combined Critique Report`,
`### Persist the Snapshot` and `### Ask the User` sections out of
`skill/reference/critique.md` at conversion time, so the pack tracks upstream
text. Any `{{` that survives placeholder replacement is escaped for Go
`text/template`, which `gc prime` uses to render prompts.

Four upstream agents (`finish-reviewer`, `asset-producer`, `documenter`,
`manual-edit-applier`) are converted mechanically and are available to future
formulas (`polish` is the obvious next one); only `critique` is wired today.

## Regenerate

```bash
git clone --depth 1 https://github.com/pbakaus/impeccable /tmp/impeccable
node gascity/convert/impeccable-to-gascity.mjs \
  --source /tmp/impeccable \
  --out gascity/packs/impeccable \
  --baseline-out gascity/packs/impeccable-native \
  --claude-out gascity/packs/impeccable-native/claude-build \
  --install-path /opt/gascity/packs/impeccable \
  --api-url http://127.0.0.1:8372/v0/city/factory
```

`--install-path` and `--api-url` are baked into each `agent.toml` `[env]`
block (`IMPECCABLE_PACK`, `IMPECCABLE_API`) so the city's own `city.toml`
needs no edit. `city.toml.example` in the pack shows the `[workspace.env]`
alternative.

## Run the comparison on a Gas City host

```bash
tar czf /tmp/packs.tgz -C gascity/packs impeccable impeccable-native
scp /tmp/packs.tgz gascity/run/setup-rigs.sh gascity/compare/collect.py host:/tmp/
ssh host 'mkdir -p /tmp/packs-staging && tar xzf /tmp/packs.tgz -C /tmp/packs-staging \
  && bash /tmp/setup-rigs.sh /tmp/packs-staging'
# ... wait for both workflows (gc status; tail -f <city>/.gc/events.jsonl) ...
ssh host 'python3 /tmp/collect.py \
  --arm native:<imn-workflow>:/opt/gascity/projects/impeccable-native \
  --arm pack:<imp-workflow>:/opt/gascity/projects/impeccable-pack \
  --since <ISO start time> --json /tmp/compare.json'
```

`setup-rigs.sh` copies the same `index.html` into two fresh git repos, installs
the reproduced `.claude/` build into the native one, registers both as rigs
(`gc rig add --include <pack>`), lints the packs, and slings one formula per
rig. It passes `BD_ALLOW_REMOTE_MIGRATE=1` to `gc rig add`; the comment in the
script explains why (a known Gas City edge where the new rig's empty Dolt
database is left half-migrated).

`collect.py` reads three things that already exist on the host: the city's
`.gc/events.jsonl` (step start/close, dependencies), the step beads through the
supervisor API (outcome, close notes), and Claude Code's transcripts under
`~/.claude/projects/<cwd-slug>/` including `subagents/`. From the transcripts
it sums tokens per conversation, counts tool calls, and records which workflow
files each conversation opened, which is what makes the isolation claim
checkable rather than asserted.

## Results: 2026-09-27, critique of one landing page

Full output in [`compare/results/2026-09-27-critique-index-html/`](compare/results/2026-09-27-critique-index-html/).
Target: a 5 KB static landing page (`target-index.html`), no DESIGN.md, no
PRODUCT.md, no browser tool on the host. Same model and effort in both arms.

| | native | pack |
|---|---|---|
| Score | 21/32 Acceptable | 19/28 Acceptable |
| Priority issues | 0 P0, 3 P1, 2 P2 | 1 P0, 3 P1, 1 P2 |
| Same five issues found | yes: dead CTA and nav links, product never shown, no proof or closing CTA, template identity, cramped mobile header | |
| Detector findings surfaced | 4 (icon-tile-stack x3, kicker-above-heading x1) | same 4 |
| Claude conversations | 3 (1 session + 2 sub-agents) | 4 (4 sessions) |
| Wall clock | 235s | 352s |
| Sum of step durations | 218s | 276s |
| Orchestration gap | 0s | 132s (39s + 39s + 54s between a step closing and its dependant starting) |
| Total input tokens incl. cache | 2.94M | 3.99M |
| Output tokens | 40k | 74k |

What the numbers say:

- The pack arm produced an equivalent critique. The eight heuristics both
  arms scored got identical marks; the totals differ only because the pack's
  reviewer marked H9 (Error Recovery) n/a where the native one scored it 2,
  which is why the denominators differ (28 vs 32) and the percentages match
  (68% vs 66%). The same five priority issues came out of both, with two
  severity calls differing: the dead primary CTA is P0 in the pack and P1
  natively, and the template-default visual identity is P1 in the pack
  (detector-confirmed) and P2 natively. Detector rules, persona choices and
  questions are the same in substance.
- The extra time in the pack arm is harness overhead, not model work. Of its
  352s, 132s is the reconciler noticing a closed step and spawning the next
  session; take that out and the two arms did their model work in the same
  time (220s vs 218s). Token-wise the pack costs one extra conversation
  (`prepare`, 0.6M cached input) plus each agent re-reading its ~20 KB prompt
  template instead of sharing one cached parent context.
- Isolation held and is auditable. From the transcripts: `design-reviewer`
  opened only `packet.md`; `evidence-collector` opened only `packet.md`;
  the `synthesize` step is the only conversation that opened both assessments.
  In the native arm the same is true by construction (sub-agents have no
  filesystem trail of reading each other), but there is nothing outside the
  parent's own prompt saying so.
- Permission enforcement differs in kind. Native: one session with every tool,
  `--dangerously-skip-permissions`. Pack: each agent launched with the tools
  its upstream frontmatter did not list removed by `--disallowedTools`
  (`design-reviewer` cannot Write or Edit; nobody can call `Agent`/Task or
  `AskUserQuestion`). Both arms still run under `permission_mode =
  unrestricted` so that no prompt can block an unattended pane; moving
  read-only agents to `full-auto` (`--permission-mode dontAsk`) with an
  explicit allow list is the next step and needs a test that `step.sh`'s Bash
  calls still pass.

## Known limits

- Only `critique` is wired as a formula. `polish` (finish-reviewer gate plus
  edit loop), `document` (documenter) and `live` (manual-edit-applier) need
  their own formulas; the agents already exist in the pack.
- Transcripts of every agent land in the same `~/.claude/projects/<cwd>/`
  directory because all sessions share `HOME` and `cwd`. A per-agent
  `CLAUDE_CONFIG_DIR` would separate them but also relocates Claude Code's
  credentials, so it was not applied. The `Isolation` section of the shared
  prompt fragment plus `--disallowedTools` is what stands between agents
  today; the audit in `collect.py` is how you check it held.
- `reply.sh`/Telegram is not wired for these rigs; the report and the
  questions for the user end in `report.md` and the persisted snapshot.
- `gc rig add` on the reference host needed `BD_ALLOW_REMOTE_MIGRATE=1`
  (see `run/setup-rigs.sh`).
- `collect.py` reports tokens, not dollars; the transcripts on the host carry
  no cost field and pricing for the pinned model is not in the repo.
