#!/usr/bin/env bash
#
# Run the six web builders against one brief, then score each finished page
# with the Impeccable critique pack.
#
#   run-matrix.sh <gascity-dir>
#
# One rig, named experiment, holds every builder. Gas City has no rig type
# field, so "experiment" is the shape experiment_rig.py writes into that
# rig's [[rigs]] block: all five packs imported, formulas_dir pointed at
# experiments/formulas, one session at a time, and the critique agents
# working in a directory that contains only the page under test.
#
# Variants are the rows of experiments/variants.tsv. Each variant is checked
# out as its own branch of the one repository, cut from the brief commit,
# because the builder prompts name site/index.html and docs/ at the
# repository root. A formula variable cannot move those paths.
#
# Arms run one at a time. factory's discover and review steps wait for a
# human to approve on Telegram; if that approval is still missing after
# APPROVAL_GRACE seconds, the arm is recorded as blocked and its session is
# suspended so the next arm can use the subscription. Nothing here sends
# the approval.
#
# Writes <gascity-dir>/compare/results/<utc-date>-builders/scoreboard.md

set -euo pipefail

GASTCITY=$(cd "${1:?usage: run-matrix.sh <gascity-dir>}" && pwd)
CITY=${GC_CITY_PATH:-/opt/gascity/city}
PACKS=/opt/gascity/packs
PROJECTS=/opt/gascity/projects
API=${IMPECCABLE_API:-http://127.0.0.1:8372/v0/city/factory}
BRIEF=$GASTCITY/experiments/brief.md
VARIANTS=$GASTCITY/experiments/variants.tsv
RIG=experiment
PREFIX=xpr
DIR=$PROJECTS/$RIG
SCORE_DIR=$DIR/.score
API_DIR=$DIR
MODEL=claude-sonnet-5
APPROVAL_GRACE=${APPROVAL_GRACE:-1200}
BUILD_TIMEOUT=${BUILD_TIMEOUT:-2700}
FACTORY_TIMEOUT=${FACTORY_TIMEOUT:-3600}
SCORE_TIMEOUT=${SCORE_TIMEOUT:-1800}
DATE=$(date -u +%F)
# A restarted supervisor keeps the directory that already holds sling files,
# so it waits on the workflow it already started instead of opening a second one.
if [ -n "${RESULTS_DIR:-}" ]; then
  OUT=$RESULTS_DIR
else
  OUT=""
  for candidate in "$GASTCITY"/compare/results/*-builders; do
    [ -d "$candidate" ] || continue
    if [ ! -f "$candidate/scoreboard.md" ] && compgen -G "$candidate/sling-*.json" > /dev/null; then
      OUT=$candidate
    fi
  done
  if [ -z "$OUT" ]; then
    OUT=$GASTCITY/compare/results/${DATE}-builders
  fi
fi
mkdir -p "$OUT" "$OUT/pages"
DATE=$(basename "$OUT")
DATE=${DATE%-builders}
STATUS=$OUT/status.tsv
if [ ! -s "$STATUS" ]; then
  printf 'arm\tbuild\tbuild_workflow\tscore_workflow\tnote\n' > "$STATUS"
fi
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ -f "$OUT/started.txt" ]; then
  START=$(cat "$OUT/started.txt")
else
  printf '%s\n' "$START" > "$OUT/started.txt"
fi

log() { printf '\n== %s\n' "$*" | tee -a "$OUT/run.log" >&2; }

install_packs() {
  log "installing coder and the impeccable-build formula"
  rm -rf "$PACKS/coder"
  cp -R "$GASTCITY/packs/coder" "$PACKS/coder"
  mkdir -p "$PACKS/impeccable-native/formulas" "$PACKS/impeccable-native/agents/runner"
  cp "$GASTCITY/packs/impeccable-native/formulas/build-native.toml" "$PACKS/impeccable-native/formulas/"
  cp "$GASTCITY/packs/impeccable-native/agents/runner/agent.toml" "$PACKS/impeccable-native/agents/runner/"
  cp "$GASTCITY/packs/impeccable-native/agents/runner/prompt.template.md" "$PACKS/impeccable-native/agents/runner/"
  if [ ! -d "$PACKS/impeccable-native/claude-build/.claude" ]; then
    log "impeccable-native claude-build is missing; the impeccable-build arm cannot run"
  fi
  if [ ! -d "$PACKS/impeccable" ]; then
    cp -R "$GASTCITY/packs/impeccable" "$PACKS/impeccable"
  fi
  (cd "$CITY" && gc lint "$PACKS/coder" && gc lint "$PACKS/impeccable-native")
}

commit_as() {
  # A no-op commit prints "nothing to commit" on stdout even with -q, and
  # that text would be captured by callers that read this function's output.
  git -C "$1" -c user.name=builder-experiment -c user.email=experiment@localhost commit -qm "$2" >/dev/null 2>&1 || true
}

prepare_project() {
  if [ ! -d "$DIR/.git" ]; then
    mkdir -p "$DIR/docs"
    cp "$BRIEF" "$DIR/docs/brief.md"
    printf '.gc/\n.impeccable/\n.score/\n.claude/\narms/\nnode_modules/\n' > "$DIR/.gitignore"
    git -C "$DIR" init -q -b main
    git -C "$DIR" add -A
    commit_as "$DIR" "Experiment brief"
  else
    git -C "$DIR" checkout -f main
    mkdir -p "$DIR/docs"
    cp "$BRIEF" "$DIR/docs/brief.md"
    git -C "$DIR" add docs/brief.md >/dev/null
    commit_as "$DIR" "Refresh experiment brief"
  fi
}

register_experiment() {
  if ! (cd "$CITY" && gc rig list) | grep -q "^  ${RIG}:"; then
    log "registering rig $RIG ($PREFIX) with every builder pack"
    # See setup-rigs.sh: bd init against a fresh database on this server needs
    # the migration consent, and the prefix must not be an SQL reserved word.
    (cd "$CITY" && BD_ALLOW_REMOTE_MIGRATE=1 gc rig add "$DIR" \
      --name "$RIG" --prefix "$PREFIX" \
      --include "$PACKS/onepage" \
      --include "$PACKS/factory" \
      --include "$PACKS/coder" \
      --include "$PACKS/impeccable" \
      --include "$PACKS/impeccable-native" \
      --default-branch main) >&2
  else
    log "rig $RIG already registered"
  fi
  python3 "$GASTCITY/run/experiment_rig.py" \
    "$CITY/city.toml" "$RIG" "$GASTCITY/experiments/formulas" "$SCORE_DIR"
}

sling_json() {
  local target=$1
  shift
  (cd "$CITY" && gc sling "$target" "$@" --json)
}

workflow_of() {
  python3 -c 'import json,sys
raw=sys.stdin.read()
start=raw.find("{")
data=json.loads(raw[start:])
print(data.get("workflow_id") or data.get("bead_id") or "")'
}

create_work_bead() {
  local arm=$1
  (cd "$DIR" && bd create "Build the landing page ($arm)" --body-file docs/brief.md --json) \
    | python3 -c 'import json,sys
raw=sys.stdin.read()
start=raw.find("{")
if start < 0:
    start=raw.find("[")
data=json.loads(raw[start:])
if isinstance(data, list):
    data=data[0]
print(data["id"])'
}

# Prints one line: <state> <note>
# state is closed, blocked, failed, or timeout.
# The runs API stays 503 while its projection warms, so the bead store is
# the source the loop actually uses.
wait_run() {
  local root=$1 dir=$2 timeout=$3 factory=$4
  python3 - "$root" "$dir" "$timeout" "$factory" "$APPROVAL_GRACE" "$API" << 'PY'
import json, subprocess, sys, time, urllib.request
root, project, timeout, factory, grace, api = sys.argv[1:]
timeout, grace = int(timeout), int(grace)
factory = factory == "yes"
approval_since = {}
use_api = True

def from_api():
    req = urllib.request.Request(api + f"/runs/{root}/steps", headers={"X-GC-Request": "1"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp).get("steps") or []

def load_bead(bead):
    raw = subprocess.check_output(["bd", "show", bead, "--json"], cwd=project, stderr=subprocess.DEVNULL)
    data = json.loads(raw)
    return data[0] if isinstance(data, list) else data

def from_beads():
    seen = set()
    steps = []
    def walk(bead):
        if bead in seen:
            return
        seen.add(bead)
        body = load_bead(bead)
        for dep in body.get("dependencies") or []:
            walk(dep["id"])
        meta = body.get("metadata") or {}
        steps.append({
            "id": body.get("id"),
            "title": body.get("title") or "",
            "status": body.get("status") or "",
            "assignee": body.get("assignee") or meta.get("assignee") or meta.get("gc.session_id") or "",
        })
    walk(root)
    return steps

deadline = time.time() + timeout
while time.time() < deadline:
    try:
        steps = from_api() if use_api else from_beads()
    except Exception as exc:
        use_api = False
        try:
            steps = from_beads()
        except Exception as inner:
            print(f"poll {root}: {exc}; beads: {inner}", file=sys.stderr)
            time.sleep(15)
            continue
    if not steps:
        time.sleep(15)
        continue
    done = True
    for step in steps:
        status = (step.get("status") or "").lower()
        if status not in ("completed", "closed", "failed"):
            done = False
        title = step.get("title") or ""
        if factory and status in ("in_progress", "in-progress", "hooked"):
            if title.startswith("Discover") or "reviewed" in title.lower():
                approval_since.setdefault(step["id"], time.time())
                if time.time() - approval_since[step["id"]] >= grace:
                    assignee = step.get("assignee") or ""
                    print(f"blocked\t{step['id']} {title} still {status} after {grace}s assignee={assignee}")
                    sys.exit(0)
            else:
                approval_since.pop(step["id"], None)
    if done:
        failed = [s for s in steps if (s.get("status") or "").lower() == "failed"]
        if failed:
            print(f"failed\t{[s['id'] for s in failed]}")
        else:
            print("closed\tall steps closed")
        sys.exit(0)
    time.sleep(20)
print("timeout\tdeadline reached")
PY
}

suspend_workflow() {
  local root=$1
  [ -n "$root" ] || return 0
  local id
  while IFS= read -r id; do
    [ -n "$id" ] || continue
    log "suspending $id"
    (cd "$CITY" && gc session suspend "$id") || true
  done < <(python3 - "$root" "$API_DIR" << 'PY'
import json, subprocess, sys
root, project = sys.argv[1:]
seen = set()
found = []

def load(bead):
    raw = subprocess.check_output(["bd", "show", bead, "--json"], cwd=project, stderr=subprocess.DEVNULL)
    data = json.loads(raw)
    return data[0] if isinstance(data, list) else data

def walk(bead):
    if bead in seen:
        return
    seen.add(bead)
    body = load(bead)
    for dep in body.get("dependencies") or []:
        walk(dep["id"])
    meta = body.get("metadata") or {}
    assignee = body.get("assignee") or meta.get("assignee") or meta.get("gc.session_id") or ""
    if assignee and "/" not in assignee and assignee not in found:
        found.append(assignee)

try:
    walk(root)
except Exception as exc:
    print(f"suspend walk {root}: {exc}", file=sys.stderr)
for assignee in found:
    print(assignee)
PY
)
}

checkout_arm() {
  local arm=$1 resume=$2
  if [ "$resume" = yes ]; then
    # A failed checkout must not reset the branch: the in-progress tree is
    # the run being resumed.
    git -C "$DIR" checkout "arm/$arm"
  else
    git -C "$DIR" checkout -f -B "arm/$arm" "$BRIEF_COMMIT"
  fi
  # The skill install is untracked. Leave it in place only for the arm that
  # reads it, so the other builders do not see Impeccable's Claude build.
  rm -rf "$DIR/.claude"
  if [ "$arm" = "impeccable-build" ] && [ -d "$PACKS/impeccable-native/claude-build/.claude" ]; then
    mkdir -p "$DIR/.claude"
    cp -R "$PACKS/impeccable-native/claude-build/.claude/." "$DIR/.claude/"
  fi
}

find_page() {
  local dir=$1
  if [ -f "$dir/site/index.html" ]; then
    printf '%s\n' "$dir/site/index.html"
    return
  fi
  if [ -f "$dir/index.html" ]; then
    printf '%s\n' "$dir/index.html"
    return
  fi
  find "$dir" -name index.html \
    -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.impeccable/*' \
    -not -path '*/.score/*' -not -path '*/.claude/*' \
    -print -quit 2>/dev/null || true
}

stage_score_page() {
  local page=$1
  mkdir -p "$SCORE_DIR"
  find "$SCORE_DIR" -mindepth 1 -maxdepth 1 ! -name .impeccable -exec rm -rf {} +
  cp "$page" "$SCORE_DIR/index.html"
}

score_page() {
  local arm=$1
  log "scoring $arm"
  local json root state
  json=$(sling_json "$RIG/impeccable.conductor" critique --formula --var target=index.html)
  printf '%s\n' "$json" > "$OUT/sling-score-$arm.json"
  root=$(printf '%s' "$json" | workflow_of)
  state=$(wait_run "$root" "$API_DIR" "$SCORE_TIMEOUT" no || true)
  printf '%s\n' "$root"
  printf '%s\n' "$state" > "$OUT/score-$arm.state"
}

record() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$STATUS"
}

install_packs
prepare_project
if [ -f "$OUT/brief.commit" ]; then
  BRIEF_COMMIT=$(cat "$OUT/brief.commit")
else
  BRIEF_COMMIT=$(git -C "$DIR" rev-parse HEAD)
  printf '%s\n' "$BRIEF_COMMIT" > "$OUT/brief.commit"
fi
register_experiment

while IFS=$'\t' read -r arm agent formula mode timeout_class; do
  case "$arm" in
    ""|\#*) continue ;;
    arm) continue ;;
  esac
  log "arm $arm"
  if [ "$timeout_class" = "factory" ]; then
    timeout=$FACTORY_TIMEOUT
  else
    timeout=$BUILD_TIMEOUT
  fi

  if grep -q "^${arm}	" "$STATUS"; then
    log "arm $arm already recorded; skipping"
    continue
  fi
  root=""
  resume=no
  if [ -f "$OUT/sling-$arm.json" ]; then
    root=$(workflow_of < "$OUT/sling-$arm.json" || true)
    if [ -n "$root" ]; then
      log "resuming workflow $root"
      resume=yes
    fi
  fi
  checkout_arm "$arm" "$resume"
  json=""
  if [ -n "$root" ]; then
    :
  elif [ "$mode" = "convoy" ]; then
    bead=$(create_work_bead "$arm")
    log "work bead $bead"
    json=$(sling_json "$RIG/$agent" "$bead" --on "$formula") || json=""
  elif [ "$arm" = "onepage" ]; then
    json=$(sling_json "$RIG/$agent" "$formula" --formula --var "build_model=$MODEL") || json=""
  elif [ "$arm" = "factory" ]; then
    json=$(sling_json "$RIG/$agent" "$formula" --formula \
      --var "discover_model=$MODEL" --var "write_tests_model=$MODEL" \
      --var "implement_model=$MODEL" --var "review_model=$MODEL" \
      --var "verification_doc_model=$MODEL" --var "deliver_model=$MODEL") || json=""
  else
    json=$(sling_json "$RIG/$agent" "$formula" --formula) || json=""
  fi
  if [ -n "$json" ]; then
    printf '%s\n' "$json" > "$OUT/sling-$arm.json"
    root=$(printf '%s' "$json" | workflow_of || true)
  fi
  if [ -z "$root" ]; then
    record "$arm" sling-failed "" "" "sling produced no workflow id"
    continue
  fi
  log "workflow $root"
  factory=no
  [ "$arm" = "factory" ] && factory=yes
  state=$(wait_run "$root" "$API_DIR" "$timeout" "$factory")
  build_state=${state%%$'\t'*}
  note=${state#*$'\t'}
  log "$arm build $build_state ($note)"
  suspend_workflow "$root"
  if [ "$build_state" = "blocked" ]; then
    record "$arm" blocked "$root" "" "$note"
    continue
  fi
  if [ "$build_state" != "closed" ]; then
    record "$arm" "$build_state" "$root" "" "$note"
    continue
  fi
  page=$(find_page "$DIR")
  if [ -z "$page" ]; then
    record "$arm" no-page "$root" "" "no index.html to score"
    continue
  fi
  mkdir -p "$OUT/pages/$arm"
  cp "$page" "$OUT/pages/$arm/index.html"
  stage_score_page "$page"
  score_root=$(score_page "$arm")
  suspend_workflow "$score_root"
  score_state=$(cat "$OUT/score-$arm.state")
  record "$arm" closed "$root" "$score_root" "$page; score ${score_state%%$'\t'*}"
done < "$VARIANTS"

score_args=()
while IFS= read -r spec; do
  [ -n "$spec" ] && score_args+=(--arm "$spec")
done < <(python3 - "$STATUS" "$SCORE_DIR" "$DIR" << 'PY'
import os, sys
status, score_dir, project = sys.argv[1:]
for line in open(status, encoding="utf-8").read().splitlines()[1:]:
    arm, _build, _wf, score_wf, _note = (line.split("\t") + [""] * 5)[:5]
    for base in (score_dir, project):
        report = os.path.join(base, ".impeccable", "gc", score_wf, "report.md")
        if score_wf and os.path.isfile(report):
            print(f"{arm}:{score_wf}:{base}")
            break
PY
)

{
  echo "# Builder experiment $DATE"
  echo
  echo "Brief: experiments/brief.md. Rig: $RIG. Model pin: $MODEL. Started: $START."
  echo
  echo "## Build status"
  echo
  echo "| Arm | Build | Workflow | Score workflow | Note |"
  echo "|---|---|---|---|---|"
  # bash read collapses a tab-tab empty field, so parse the TSV in Python.
  python3 - "$STATUS" << 'PY'
import sys
rows = open(sys.argv[1], encoding="utf-8").read().splitlines()
for line in rows[1:]:
    arm, build, build_wf, score_wf, note = (line.split("\t") + [""] * 5)[:5]
    cells = [arm, build, build_wf or "-", score_wf or "-", note or "-"]
    print("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
PY
  echo
  if [ "${#score_args[@]}" -gt 0 ]; then
    python3 "$GASTCITY/compare/collect.py" --city "$CITY" --api "$API" --since "$START" --scoreboard \
      --json "$OUT/collection.json" "${score_args[@]}"
  else
    echo "No critique finished, so there is no score table."
  fi
} > "$OUT/scoreboard.md"

log "wrote $OUT/scoreboard.md"
