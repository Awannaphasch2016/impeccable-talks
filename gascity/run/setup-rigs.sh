#!/usr/bin/env bash
#
# Build the two comparison rigs on a Gas City host and start one critique in
# each. Run on the host as the city user, from anywhere:
#
#   setup-rigs.sh <staged-packs-dir> [target-file]
#
# <staged-packs-dir> holds the generated `impeccable/` and `impeccable-native/`
# packs (the output of gascity/convert). The target file defaults to the city's
# landing page, taken from its last commit so both arms critique identical
# bytes.
#
# Arm A (native): a copy of the target with Impeccable's own Claude Code build
#   installed in .claude/; one unrestricted Gas City agent runs the skill, which
#   spawns its assessors through Claude Code's Task tool.
# Arm B (pack):   the same copy; the converted pack's formula fans the
#   assessors out as separate Gas City agents.
#
# Idempotent for the rigs: rerunning replaces the pack files and re-slings a
# fresh workflow; existing rigs are left registered.

set -euo pipefail

STAGED=${1:?usage: setup-rigs.sh <staged-packs-dir> [target-file]}
TARGET_SRC=${2:-}
CITY=${GC_CITY_PATH:-/opt/gascity/city}
PACKS=/opt/gascity/packs
PROJECTS=/opt/gascity/projects
SITE=/opt/gascity/site

log() { printf '\n== %s\n' "$*"; }

# 1. Install the packs where the agent.toml env blocks expect them.
log "installing packs under $PACKS"
for pack in impeccable impeccable-native; do
  rm -rf "$PACKS/$pack"
  cp -R "$STAGED/$pack" "$PACKS/$pack"
  chmod +x "$PACKS/$pack"/scripts/*.sh
done
chmod +x "$PACKS/impeccable/skill/scripts/impeccable"

# 2. Identical target bytes for both arms.
tmp_target=$(mktemp)
if [ -n "$TARGET_SRC" ]; then
  cp "$TARGET_SRC" "$tmp_target"
else
  git -C "$SITE" show HEAD:index.html > "$tmp_target"
fi

make_project() {
  local name=$1
  local dir="$PROJECTS/$name"
  if [ -d "$dir/.git" ]; then
    log "project $name exists; refreshing index.html only"
    cp "$tmp_target" "$dir/index.html"
    git -C "$dir" add index.html
    git -C "$dir" -c user.name=impeccable-compare -c user.email=compare@localhost \
      commit -qm "Refresh target" || true
    return
  fi
  log "creating project $name"
  mkdir -p "$dir"
  cp "$tmp_target" "$dir/index.html"
  cat > "$dir/.gitignore" <<'EOF'
.gc/
.impeccable/gc/
EOF
  git -C "$dir" init -q -b main
  git -C "$dir" add -A
  git -C "$dir" -c user.name=impeccable-compare -c user.email=compare@localhost \
    commit -qm "Baseline target for Impeccable comparison"
}

make_project impeccable-native
make_project impeccable-pack

# 3. Arm A gets Impeccable's Claude Code build; arm B gets nothing but the pack.
#    The build is what `npx impeccable install --providers=claude
#    --scope=project` would lay down; the converter reproduces it from source
#    (--claude-out) so the arm does not depend on the bundle download.
log "installing Impeccable's Claude build into impeccable-native"
(
  cd "$PROJECTS/impeccable-native"
  rm -rf .claude/skills/impeccable .claude/agents
  mkdir -p .claude
  cp -R "$STAGED/impeccable-native/claude-build/.claude/." .claude/
  chmod +x .claude/skills/impeccable/scripts/impeccable
  ls .claude/agents .claude/skills/impeccable | head -20
  git add -A
  git -c user.name=impeccable-compare -c user.email=compare@localhost \
    commit -qm "Install Impeccable Claude Code build" || true
)

# 4. Register the rigs.
cd "$CITY"
register() {
  local name=$1 pack=$2 prefix=$3
  if gc rig list 2>/dev/null | grep -q "^  $name:"; then
    log "rig $name already registered"
    return
  fi
  log "registering rig $name with pack $pack"
  # Explicit prefix: the derived one for impeccable-native is "in", an SQL
  # reserved word, which is a poor Dolt database name.
  #
  # BD_ALLOW_REMOTE_MIGRATE=1: gc rig add pre-creates the rig's empty Dolt
  # database and runs `bd init --force` against it with a 5s migration bound;
  # on a loaded host the migration stops partway (v56 of v66 observed) and
  # bd's shared-store gate then refuses the half-migrated database. The consent
  # lets bd finish migrating that new, empty database. It touches no other
  # database on the server. See gascity's test/acceptance/helpers
  # LegacyInitEnv for the same reasoning.
  BD_ALLOW_REMOTE_MIGRATE=1 gc rig add "$PROJECTS/$name" --name "$name" --prefix "$prefix" \
    --include "$PACKS/$pack" --default-branch main
}
register impeccable-native impeccable-native imn
register impeccable-pack impeccable imp

gc lint "$PACKS/impeccable"
gc lint "$PACKS/impeccable-native"

# 5. Start one critique per arm.
log "slinging critique-native on impeccable-native"
gc sling impeccable-native/impeccable-native.runner critique-native --formula --var target=index.html --json | tee /tmp/sling-native.json
log "slinging critique on impeccable-pack"
gc sling impeccable-pack/impeccable.conductor critique --formula --var target=index.html --json | tee /tmp/sling-pack.json

log "done; watch with: gc status; tail -f $CITY/.gc/events.jsonl"
