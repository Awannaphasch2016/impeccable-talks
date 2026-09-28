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
# experiments/formulas, no session cap, each builder that owns one variant
# working in that variant's worktree, and the critique agents working in
# .score.
#
# Variants are the rows of experiments/variants.tsv. The prompts write
# site/index.html at the repository root, so each variant gets its own git
# worktree on arm/<name>, cut from the brief commit by gc worktree ensure,
# before any of them is slung. The script then slings every row and only
# afterwards polls. coder.coder is shared by the three mol formulas, so
# those work beads name the worktree. The factory row slings
# website-factory, which formulas_dir replaces with the implement step:
# it reads docs/brief.md and writes site/index.html. Nothing here sends a
# Telegram approval.
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
# gc worktree ensure refuses a path inside a registered worktree, and the
# project checkout is one. The arm checkouts sit beside it.
WT_ROOT=$PROJECTS/${RIG}-worktrees
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
    printf '.gc/\n.impeccable/\n.score/\n.worktrees/\n.claude/\narms/\nnode_modules/\n' > "$DIR/.gitignore"
    git -C "$DIR" init -q -b main
    git -C "$DIR" add -A
    commit_as "$DIR" "Experiment brief"
  else
    git -C "$DIR" checkout -f main
    mkdir -p "$DIR/docs"
    rm -rf "$DIR/.claude"
    cp "$BRIEF" "$DIR/docs/brief.md"
    printf '.gc/\n.impeccable/\n.score/\n.worktrees/\n.claude/\narms/\nnode_modules/\n' > "$DIR/.gitignore"
    git -C "$DIR" add docs/brief.md .gitignore >/dev/null
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
  mkdir -p "$SCORE_DIR" "$WT_ROOT"
  python3 "$GASTCITY/run/experiment_rig.py" \
    "$CITY/city.toml" "$RIG" "$GASTCITY/experiments/formulas" "$SCORE_DIR" \
    "$WT_ROOT" "$GASTCITY/experiments/prompts/factory-builder.md"
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

create_bead() {
  local title=$1 body=$2
  local id
  id=$(cd "$DIR" && bd create "$title" --body-file "$body" --silent)
  id=$(printf '%s' "$id" | tr -d '[:space:]')
  if [ -z "$id" ]; then
    echo "bd create produced no id for $title" >&2
    return 1
  fi
  printf '%s\n' "$id"
}

# mol-scoped-work and mol-polecat-commit treat metadata.work_dir as a
# temporary worktree and delete it when they finish. The experiment worktree
# is named in the bead text instead, so that cleanup cannot remove it.
write_assignment() {
  local arm=$1 dest=$2
  {
    printf '%s\n' \
      "The first command you run is:" \
      "" \
      "cd $WT_ROOT/$arm" \
      "" \
      "Every later command runs in that directory. Write only inside that directory." \
      "Read docs/brief.md there. It is the specification. The brief is closed." \
      "Write the page it describes as site/index.html in that directory: valid HTML, CSS in the file, and no request to another host." \
      "Commit it there. Done when that file exists and git status in that directory is clean." \
      "" \
      "The brief follows." \
      ""
    cat "$BRIEF"
  } > "$dest"
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

drop_worktree() {
  local path=$1 branch=$2
  local current
  current=$(git -C "$DIR" rev-parse --abbrev-ref HEAD)
  if [ "$current" = "$branch" ]; then
    git -C "$DIR" checkout -f main
  fi
  if git -C "$DIR" worktree list --porcelain | grep -Fxq "worktree $path"; then
    git -C "$DIR" worktree remove --force "$path"
  fi
  if [ -e "$path" ]; then
    rm -rf "$path"
  fi
  git -C "$DIR" worktree prune
  if git -C "$DIR" show-ref --verify --quiet "refs/heads/$branch"; then
    git -C "$DIR" branch -D "$branch"
  fi
}

# resume=yes reuses the bead id already bound to the worktree. A fresh arm
# deletes the old worktree and branch first: gc worktree ensure checks an
# existing branch out again and does not reset it to the brief, and
# gc worktree cleanup refuses commits that are not merged into the base.
ensure_worktree() {
  local arm=$1 resume=$2
  local path branch bead_file bead body json
  path=$WT_ROOT/$arm
  branch=arm/$arm
  bead_file=$OUT/worktree-$arm.bead
  mkdir -p "$WT_ROOT"
  if [ "$resume" != yes ]; then
    drop_worktree "$path" "$branch"
    rm -f "$bead_file"
  fi
  if [ -s "$bead_file" ]; then
    bead=$(tr -d '[:space:]' < "$bead_file")
  elif [ "$resume" = yes ]; then
    return 2
  else
    body=$OUT/worktree-$arm.md
    printf 'Worktree %s for experiment arm %s.\n' "$path" "$arm" > "$body"
    bead=$(create_bead "Worktree $branch" "$body")
    printf '%s\n' "$bead" > "$bead_file"
  fi
  if ! json=$(cd "$CITY" && gc worktree ensure \
    --repo "$DIR" \
    --root "$WT_ROOT" \
    --path "$path" \
    --branch "$branch" \
    --base "$BRIEF_COMMIT" \
    --base-sha "$BRIEF_COMMIT" \
    --bead "$bead" \
    --store-ref experiment \
    --creator run-matrix \
    --owner experiment \
    --generation 1 \
    --lifecycle active \
    --json); then
    return 1
  fi
  printf '%s\n' "$json" > "$OUT/worktree-$arm.json"
  # The skill install is untracked. It belongs only in the arm that reads it.
  if [ "$arm" = "impeccable-build" ] && [ -d "$PACKS/impeccable-native/claude-build/.claude" ]; then
    mkdir -p "$path/.claude"
    cp -R "$PACKS/impeccable-native/claude-build/.claude/." "$path/.claude/"
  fi
}

sling_arm() {
  local arm=$1 agent=$2 formula=$3 mode=$4
  local json="" body bead
  if [ "$mode" = "convoy" ]; then
    body=$OUT/assignment-$arm.md
    write_assignment "$arm" "$body"
    bead=$(create_bead "Build the landing page ($arm)" "$body")
    log "work bead $bead"
    json=$(sling_json "$RIG/$agent" "$bead" --on "$formula") || json=""
  elif [ "$arm" = "onepage" ]; then
    json=$(sling_json "$RIG/$agent" "$formula" --formula --var "build_model=$MODEL") || json=""
  else
    json=$(sling_json "$RIG/$agent" "$formula" --formula) || json=""
  fi
  printf '%s\n' "$json"
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
  local arm=$1 page=$2
  mkdir -p "$SCORE_DIR/$arm" "$OUT/pages/$arm"
  cp "$page" "$OUT/pages/$arm/index.html"
  cp "$page" "$SCORE_DIR/$arm/index.html"
}

sling_score() {
  local arm=$1
  local json root
  if [ -f "$OUT/sling-score-$arm.json" ]; then
    root=$(workflow_of < "$OUT/sling-score-$arm.json" || true)
    if [ -n "$root" ]; then
      printf '%s\n' "$root"
      return 0
    fi
  fi
  log "scoring $arm"
  json=$(sling_json "$RIG/impeccable.conductor" critique --formula --var "target=$arm/index.html") || json=""
  printf '%s\n' "$json" > "$OUT/sling-score-$arm.json"
  printf '%s\n' "$json" | workflow_of
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

: > "$OUT/pending.tsv"
python3 - "$VARIANTS" "$STATUS" > "$OUT/pending.tsv" << 'PY'
import sys
variants, status = sys.argv[1:]
done = set()
for line in open(status, encoding="utf-8").read().splitlines()[1:]:
    if line.strip():
        done.add(line.split("\t", 1)[0])
for raw in open(variants, encoding="utf-8"):
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split("\t")
    if parts[0] == "arm" or parts[0] in done:
        continue
    if len(parts) != 5:
        raise SystemExit(f"bad variant row: {line}")
    print("\t".join(parts))
PY

: > "$OUT/inflight.tsv"
while IFS=$'\t' read -r arm agent formula mode timeout_class; do
  [ -n "$arm" ] || continue
  log "sling $arm"
  if [ "$timeout_class" = "factory" ]; then
    timeout=$FACTORY_TIMEOUT
  else
    timeout=$BUILD_TIMEOUT
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
  code=0
  ensure_worktree "$arm" "$resume" || code=$?
  if [ "$code" != 0 ]; then
    if [ "$code" = 2 ]; then
      record "$arm" worktree-failed "" "" "resume is missing the worktree bead id"
    else
      record "$arm" worktree-failed "" "" "gc worktree ensure failed for arm/$arm"
    fi
    continue
  fi
  if [ -z "$root" ]; then
    json=$(sling_arm "$arm" "$agent" "$formula" "$mode")
    if [ -n "$json" ]; then
      printf '%s\n' "$json" > "$OUT/sling-$arm.json"
      root=$(printf '%s' "$json" | workflow_of || true)
    fi
  fi
  if [ -z "$root" ]; then
    record "$arm" sling-failed "" "" "sling produced no workflow id"
    continue
  fi
  log "workflow $root"
  printf '%s\t%s\t%s\n' "$arm" "$timeout" "$root" >> "$OUT/inflight.tsv"
done < "$OUT/pending.tsv"

: > "$OUT/to-score.tsv"
while IFS=$'\t' read -r arm timeout root; do
  [ -n "$arm" ] || continue
  log "waiting for $arm ($root)"
  state=$(wait_run "$root" "$API_DIR" "$timeout" no)
  build_state=${state%%$'\t'*}
  note=${state#*$'\t'}
  log "$arm build $build_state ($note)"
  suspend_workflow "$root"
  if [ "$build_state" != "closed" ]; then
    record "$arm" "$build_state" "$root" "" "$note"
    continue
  fi
  page=$(find_page "$WT_ROOT/$arm")
  if [ -z "$page" ]; then
    record "$arm" no-page "$root" "" "no index.html to score"
    continue
  fi
  stage_score_page "$arm" "$page"
  printf '%s\t%s\t%s\n' "$arm" "$root" "$page" >> "$OUT/to-score.tsv"
done < "$OUT/inflight.tsv"

: > "$OUT/scoring.tsv"
while IFS=$'\t' read -r arm root page; do
  [ -n "$arm" ] || continue
  score_root=$(sling_score "$arm")
  if [ -z "$score_root" ]; then
    record "$arm" closed "$root" "" "$page; critique sling produced no workflow id"
    continue
  fi
  printf '%s\t%s\t%s\n' "$arm" "$root" "$score_root" >> "$OUT/scoring.tsv"
done < "$OUT/to-score.tsv"

while IFS=$'\t' read -r arm root score_root; do
  [ -n "$arm" ] || continue
  log "waiting for critique $arm ($score_root)"
  state=$(wait_run "$score_root" "$API_DIR" "$SCORE_TIMEOUT" no)
  printf '%s\n' "$state" > "$OUT/score-$arm.state"
  suspend_workflow "$score_root"
  record "$arm" closed "$root" "$score_root" "$WT_ROOT/$arm; score ${state%%$'\t'*}"
done < "$OUT/scoring.tsv"

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
  echo "Each variant ran in its own worktree under ${RIG}-worktrees/, and the critiques ran together."
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
