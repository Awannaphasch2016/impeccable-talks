#!/usr/bin/env bash
#
# Run the six web builders against one brief, then score each finished page
# with the Impeccable critique pack.
#
#   run-matrix.sh <gascity-dir>
#
# <gascity-dir> contains experiments/brief.md, packs/coder, and
# packs/impeccable plus packs/impeccable-native. factory and onepage are
# already installed on the city host at /opt/gascity/packs.
#
# Arms run one at a time. factory's discover and review steps wait for a
# human to approve on Telegram; if that approval is still missing after
# APPROVAL_GRACE seconds, the arm is recorded as blocked and its session is
# suspended so the next arm can use the subscription. Nothing here sends
# the approval.
#
# Writes <gascity-dir>/compare/results/<utc-date>-builders/scoreboard.md

set -euo pipefail

GASTCITY=${1:?usage: run-matrix.sh <gascity-dir>}
CITY=${GC_CITY_PATH:-/opt/gascity/city}
PACKS=/opt/gascity/packs
PROJECTS=/opt/gascity/projects
API=${IMPECCABLE_API:-http://127.0.0.1:8372/v0/city/factory}
BRIEF=$GASTCITY/experiments/brief.md
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
mkdir -p "$OUT"
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

# name, prefix, score prefix, pack, agent, formula, mode (formula|convoy), timeout
ARMS=(
  "onepage eop sop onepage onepage.builder onepage formula $BUILD_TIMEOUT"
  "factory efa sfa factory factory.discoverer website-factory formula $FACTORY_TIMEOUT"
  "mol-do-work emd smd coder coder.coder mol-do-work convoy $BUILD_TIMEOUT"
  "mol-scoped-work ems sms coder coder.coder mol-scoped-work convoy $BUILD_TIMEOUT"
  "mol-polecat-commit emc smc coder coder.coder mol-polecat-commit convoy $BUILD_TIMEOUT"
  "impeccable-build eib sib impeccable-native impeccable-native.runner build-native formula $BUILD_TIMEOUT"
)

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
  git -C "$1" -c user.name=builder-experiment -c user.email=experiment@localhost commit -qm "$2" || true
}

prepare_project() {
  local name=$1
  local dir=$PROJECTS/$name
  if [ ! -d "$dir/.git" ]; then
    mkdir -p "$dir/docs"
    cp "$BRIEF" "$dir/docs/brief.md"
    printf '.gc/\n.impeccable/\nnode_modules/\n' > "$dir/.gitignore"
    git -C "$dir" init -q -b main
    git -C "$dir" add -A
    commit_as "$dir" "Experiment brief"
  else
    mkdir -p "$dir/docs"
    cp "$BRIEF" "$dir/docs/brief.md"
    git -C "$dir" add docs/brief.md
    commit_as "$dir" "Refresh experiment brief"
  fi
  printf '%s\n' "$dir"
}

register_rig() {
  local name=$1 prefix=$2 pack=$3
  if (cd "$CITY" && gc rig list) | grep -q "^  ${name}:"; then
    log "rig $name already registered"
    return
  fi
  log "registering rig $name ($prefix) with $pack"
  # See setup-rigs.sh: bd init against a fresh database on this server needs
  # the migration consent, and the prefix must not be an SQL reserved word.
  (cd "$CITY" && BD_ALLOW_REMOTE_MIGRATE=1 gc rig add "$PROJECTS/$name" \
    --name "$name" --prefix "$prefix" --include "$PACKS/$pack" --default-branch main) >&2
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
  local dir=$1
  (cd "$dir" && bd create "Build the landing page" --body-file docs/brief.md --json) \
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

suspend_assignee() {
  local note=$1
  local assignee
  assignee=$(printf '%s' "$note" | sed -n 's/.*assignee=\([^ ]*\).*/\1/p')
  if [ -n "$assignee" ]; then
    (cd "$CITY" && gc session suspend "$assignee") || true
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
  find "$dir" -name index.html -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.impeccable/*' | head -1
}

score_page() {
  local arm=$1 score_prefix=$2 page=$3
  local name=score-$arm
  local dir=$PROJECTS/$name
  rm -rf "$dir"
  mkdir -p "$dir"
  cp "$page" "$dir/index.html"
  printf '.gc/\n.impeccable/\n' > "$dir/.gitignore"
  git -C "$dir" init -q -b main
  git -C "$dir" add -A
  commit_as "$dir" "Page built by $arm"
  register_rig "$name" "$score_prefix" impeccable
  log "scoring $arm"
  local json root state
  json=$(sling_json "$name/impeccable.conductor" critique --formula --var target=index.html)
  printf '%s\n' "$json" > "$OUT/sling-score-$arm.json"
  root=$(printf '%s' "$json" | workflow_of)
  state=$(wait_run "$root" "$dir" "$SCORE_TIMEOUT" no || true)
  printf '%s\n' "$root"
  printf '%s\n' "$state" > "$OUT/score-$arm.state"
}

record() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >> "$STATUS"
}

install_packs

for spec in "${ARMS[@]}"; do
  set -- $spec
  arm=$1 prefix=$2 score_prefix=$3 pack=$4 agent=$5 formula=$6 mode=$7 timeout=$8
  log "arm $arm"
  dir=$(prepare_project "exp-$arm")
  if [ "$arm" = "impeccable-build" ] && [ -d "$PACKS/impeccable-native/claude-build/.claude" ]; then
    rm -rf "$dir/.claude"
    mkdir -p "$dir/.claude"
    cp -R "$PACKS/impeccable-native/claude-build/.claude/." "$dir/.claude/"
    git -C "$dir" add .claude
    commit_as "$dir" "Install Impeccable Claude build"
  fi
  register_rig "exp-$arm" "$prefix" "$pack"

  if grep -q "^${arm}	" "$STATUS"; then
    log "arm $arm already recorded; skipping"
    continue
  fi
  root=""
  if [ -f "$OUT/sling-$arm.json" ]; then
    root=$(workflow_of < "$OUT/sling-$arm.json" || true)
    if [ -n "$root" ]; then
      log "resuming workflow $root"
    fi
  fi
  json=""
  if [ -n "$root" ]; then
    :
  elif [ "$mode" = "convoy" ]; then
    bead=$(create_work_bead "$dir")
    log "work bead $bead"
    json=$(sling_json "exp-$arm/$agent" "$bead" --on "$formula") || json=""
  elif [ "$arm" = "onepage" ]; then
    json=$(sling_json "exp-$arm/$agent" "$formula" --formula --var "build_model=$MODEL") || json=""
  elif [ "$arm" = "factory" ]; then
    json=$(sling_json "exp-$arm/$agent" "$formula" --formula \
      --var "discover_model=$MODEL" --var "write_tests_model=$MODEL" \
      --var "implement_model=$MODEL" --var "review_model=$MODEL" \
      --var "verification_doc_model=$MODEL" --var "deliver_model=$MODEL") || json=""
  else
    json=$(sling_json "exp-$arm/$agent" "$formula" --formula) || json=""
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
  state=$(wait_run "$root" "$dir" "$timeout" "$factory")
  build_state=${state%%$'\t'*}
  note=${state#*$'\t'}
  log "$arm build $build_state ($note)"
  if [ "$build_state" = "blocked" ]; then
    suspend_assignee "$note"
    record "$arm" blocked "$root" "" "$note"
    continue
  fi
  if [ "$build_state" != "closed" ]; then
    record "$arm" "$build_state" "$root" "" "$note"
    continue
  fi
  page=$(find_page "$dir")
  if [ -z "$page" ]; then
    record "$arm" no-page "$root" "" "no index.html to score"
    continue
  fi
  score_root=$(score_page "$arm" "$score_prefix" "$page")
  score_state=$(cat "$OUT/score-$arm.state")
  record "$arm" closed "$root" "$score_root" "$page; score ${score_state%%$'\t'*}"
done

score_args=()
while IFS=$'\t' read -r arm build build_wf score_wf note; do
  [ "$arm" = "arm" ] && continue
  if [ -n "$score_wf" ] && [ -f "$PROJECTS/score-$arm/.impeccable/gc/$score_wf/report.md" ]; then
    score_args+=(--arm "$arm:$score_wf:$PROJECTS/score-$arm")
  fi
done < "$STATUS"

{
  echo "# Builder experiment $DATE"
  echo
  echo "Brief: experiments/brief.md. Model pin: $MODEL. Started: $START."
  echo
  echo "## Build status"
  echo
  echo "| Arm | Build | Workflow | Score workflow | Note |"
  echo "|---|---|---|---|---|"
  while IFS=$'\t' read -r arm build build_wf score_wf note; do
    [ "$arm" = "arm" ] && continue
    echo "| $arm | $build | ${build_wf:-"-"} | ${score_wf:-"-"} | ${note:-"-"} |"
  done < "$STATUS"
  echo
  if [ "${#score_args[@]}" -gt 0 ]; then
    python3 "$GASTCITY/compare/collect.py" --city "$CITY" --api "$API" --since "$START" --scoreboard \
      --json "$OUT/collection.json" "${score_args[@]}"
  else
    echo "No critique finished, so there is no score table."
  fi
} > "$OUT/scoreboard.md"

log "wrote $OUT/scoreboard.md"
