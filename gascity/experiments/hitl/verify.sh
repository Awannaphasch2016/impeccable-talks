#!/usr/bin/env bash
#
# Sling the approval formula twice and check the gates.
# The rig must already be registered. This script does not create a store and
# does not install Dolt or bd. RIG selects the registered rig (default: experiment).

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
CITY=${GC_CITY_PATH:-/opt/gascity/city}
PROJECTS=${PROJECTS:-/opt/gascity/projects}
RIG=${RIG:-experiment}
export RIG
DIR=$PROJECTS/$RIG
HITL=$ROOT/gascity/experiments/hitl/hitl.py
AGENT=$RIG/factory.builder

log() { printf '%s\n' "$*" >&2; }
fail() { printf 'fail: %s\n' "$*" >&2; exit 1; }

rig_registered() {
  (cd "$CITY" && gc rig list) 2>&1 | awk -v rig="$RIG" '
    $0 !~ /unknown rig/ {
      line = $0
      sub(/^[[:space:]]+/, "", line)
      if (index(line, rig) == 1) {
        rest = substr(line, length(rig) + 1, 1)
        if (rest == "" || rest !~ /[[:alnum:]_]/) found = 1
      }
    }
    END { exit !found }
  '
}

if ! rig_registered; then
  printf '%s is not registered. Run gascity/run/run-matrix.sh to register it.\n' "$RIG" >&2
  exit 1
fi

if [ ! -d "$DIR" ]; then
  fail "$DIR does not exist. Run gascity/run/run-matrix.sh to register it."
fi

sling() {
  local run=$1
  local json id
  json=$(cd "$CITY" && gc sling "$AGENT" approval --formula --var "run=$run" --json) || true
  [ -n "$json" ] || fail "sling run=$run produced no output"
  id=$(printf '%s' "$json" | python3 -c '
import json, sys
raw = sys.stdin.read()
start = raw.find("{")
data = json.loads(raw[start:])
print(data.get("workflow_id") or data.get("bead_id") or data.get("root_id") or "")
')
  log "sling run=$run workflow=${id:-unknown}"
  hitl shield --run "$run"
}

hitl() {
  python3 "$HITL" "$@"
}

members_of() {
  local step=$1
  local line
  line=$(printf '%s\n' "$PENDING" | awk -F 'members=' -v step="step=$step " '$0 ~ step { print $2 }')
  printf '%s\n' "$line"
}

has_member() {
  local list=$1 name=$2
  [[ ",$list," == *",$name,"* ]]
}

assert_file() {
  local path=$1
  [ -f "$path" ] || fail "missing $path"
}

assert_absent() {
  local path=$1
  [ ! -e "$path" ] || fail "unexpected $path"
}

refresh_pending() {
  PENDING=$(hitl pending --run "$RUN")
}

assert_only_step() {
  local step=$1
  local count
  count=$(printf '%s\n' "$PENDING" | awk 'NF { n++ } END { print n+0 }')
  [ "$count" = 1 ] || fail "pending for $RUN is not only one gate: $PENDING"
  printf '%s\n' "$PENDING" | grep -q "step=$step " || fail "pending is not $step: $PENDING"
}

assert_members() {
  local step=$1
  shift
  local list
  list=$(members_of "$step")
  local name
  for name in "$@"; do
    case $name in
      !*)
        name=${name#!}
        if has_member "$list" "$name"; then
          fail "$step offers $name ($list)"
        fi
        ;;
      *)
        if ! has_member "$list" "$name"; then
          fail "$step does not offer $name ($list)"
        fi
        ;;
    esac
  done
}

reject() {
  local member=$1 step=$2
  local code=0
  set +e
  hitl respond --as "$member" --step "$step" --run "$RUN"
  code=$?
  set -e
  [ "$code" -ne 0 ] || fail "$member was allowed to close $step"
}

accept() {
  local member=$1 step=$2
  local out
  out=$(hitl respond --as "$member" --step "$step" --run "$RUN")
  printf '%s\n' "$out"
  printf '%s\n' "$out" | grep -q "approved by $member" || fail "close event for $step does not record approved by $member"
}

gate_open() {
  local step=$1
  refresh_pending
  printf '%s\n' "$PENDING" | grep -q "step=$step " || fail "$step is not open"
}

release_until() {
  local file=$1
  local i
  hitl release --run "$RUN"
  for i in 1 2 3 4 5 6 7 8 9 10; do
    [ -f "$file" ] && return 0
    sleep 1
  done
  fail "city check did not write $file"
}

run_roles() {
  RUN=roles
  sling roles
  hitl audit --run "$RUN"
  release_until "$DIR/$RUN/plan.txt"
  assert_file "$DIR/$RUN/plan.txt"
  assert_absent "$DIR/$RUN/review.txt"
  assert_absent "$DIR/$RUN/done.txt"
  refresh_pending
  assert_only_step plan-approve
  assert_members plan-approve alice carol '!bob' '!dave'

  reject bob plan-approve
  refresh_pending
  assert_only_step plan-approve
  assert_absent "$DIR/$RUN/review.txt"

  reject dave plan-approve
  refresh_pending
  assert_only_step plan-approve

  accept alice plan-approve
  release_until "$DIR/$RUN/review.txt"
  assert_file "$DIR/$RUN/review.txt"
  refresh_pending
  printf '%s\n' "$PENDING" | grep -q "step=review-approve-dev " || fail "developer gate is hidden: $PENDING"
  printf '%s\n' "$PENDING" | grep -q "step=review-approve-pm " || fail "project-manager gate is hidden: $PENDING"
  assert_members review-approve-dev bob carol '!alice' '!dave'
  assert_members review-approve-pm alice carol '!bob' '!dave'

  reject alice review-approve-dev
  gate_open review-approve-dev

  reject bob review-approve-pm
  gate_open review-approve-pm

  accept alice review-approve-pm
  gate_open review-approve-dev
  assert_absent "$DIR/$RUN/done.txt"

  accept bob review-approve-dev
  release_until "$DIR/$RUN/done.txt"
  assert_file "$DIR/$RUN/done.txt"
  hitl audit --run "$RUN"
  log "roles ok"
}

run_carol() {
  RUN=carol
  sling carol
  hitl audit --run "$RUN"
  release_until "$DIR/$RUN/plan.txt"
  accept carol plan-approve
  release_until "$DIR/$RUN/review.txt"
  accept carol review-approve-dev
  accept carol review-approve-pm
  release_until "$DIR/$RUN/done.txt"
  assert_file "$DIR/$RUN/done.txt"
  hitl audit --run "$RUN"
  log "carol ok"
}

run_roles
run_carol
log "ok"
