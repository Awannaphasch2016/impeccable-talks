#!/usr/bin/env node
// Convert Impeccable's Claude Code sub-agent system into a Gas City pack.
//
//   node gascity/convert/impeccable-to-gascity.mjs \
//     --source /path/to/pbakaus-impeccable \
//     --out gascity/packs/impeccable \
//     [--pack-name impeccable] \
//     [--install-path /opt/gascity/packs/impeccable] \
//     [--api-url http://127.0.0.1:8372/v0/city/factory] \
//     [--baseline-out gascity/packs/impeccable-native] \
//     [--baseline-install-path /opt/gascity/packs/impeccable-native]
//
// What maps to what:
//   skill/agents/*.md            -> agents/<name>/{agent.toml,prompt.template.md}
//   frontmatter tools:           -> --disallowedTools for everything not listed
//   frontmatter effort:/model:   -> option_defaults
//   critique.md parent context   -> conductor agent (prepare + synthesize)
//   critique.md Assessment A / B -> design-reviewer / evidence-collector agents
//   "spawn A and B in parallel"  -> formulas/critique.toml steps with shared needs
//   Task tool return value       -> step.sh result <file>, read by the next step
//   AskUserQuestion              -> questions appended to report.md
//   skill/SKILL.src.md, reference/, scripts/ -> skill/ (compiled for Claude tags)
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { agentFromImpeccable, syntheticAgents } from './lib/agents.mjs';
import { emitPack, emitBaselinePack } from './lib/emit.mjs';
import { gascityPlaceholders } from './lib/text.mjs';

function parseArgs(argv) {
  const args = {
    'pack-name': 'impeccable',
    'install-path': '/opt/gascity/packs/impeccable',
    'api-url': 'http://127.0.0.1:8372/v0/city/factory',
    'baseline-pack-name': 'native',
    'baseline-install-path': '/opt/gascity/packs/impeccable-native',
  };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (!a.startsWith('--')) throw new Error(`unexpected argument ${a}`);
    const key = a.slice(2);
    const eq = key.indexOf('=');
    if (eq !== -1) args[key.slice(0, eq)] = key.slice(eq + 1);
    else args[key] = argv[++i];
  }
  for (const req of ['source', 'out']) {
    if (!args[req]) throw new Error(`--${req} is required`);
  }
  return args;
}

function sourceVersion(source) {
  const parts = [];
  const versionFile = path.join(source, 'skill', 'scripts', 'VERSION');
  if (fs.existsSync(versionFile)) parts.push(`skill ${fs.readFileSync(versionFile, 'utf8').trim()}`);
  try {
    const sha = execSync('git rev-parse --short HEAD', { cwd: source, stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim();
    if (sha) parts.push(`commit ${sha}`);
  } catch {
    // not a git checkout; the VERSION file is enough
  }
  return parts.join(', ') || 'unknown version';
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const source = path.resolve(args.source);
  const out = path.resolve(args.out);
  const agentsDir = path.join(source, 'skill', 'agents');
  if (!fs.existsSync(agentsDir)) throw new Error(`${agentsDir} not found; --source must be an Impeccable checkout`);

  const converted = fs.readdirSync(agentsDir)
    .filter((f) => f.endsWith('.md'))
    .sort()
    .map((f) => agentFromImpeccable(fs.readFileSync(path.join(agentsDir, f), 'utf8'), f));
  const agents = [...syntheticAgents(), ...converted];

  const formulas = fs.readdirSync(path.join(path.dirname(new URL(import.meta.url).pathname), 'templates', 'formulas'))
    .map((f) => f.replace(/\.toml$/, ''));
  const placeholders = gascityPlaceholders({ packName: args['pack-name'], packEnv: 'IMPECCABLE_PACK', formulas });
  const version = sourceVersion(source);

  const manifest = emitPack({
    out,
    packName: args['pack-name'],
    source,
    agents,
    sourceVersion: version,
    placeholders,
    installPath: args['install-path'],
    apiUrl: args['api-url'],
  });
  process.stdout.write(`wrote ${out}\n`);
  for (const a of manifest.agents) {
    process.stdout.write(`  agent ${a.name.padEnd(32)} tools=[${a.tools.join(',')}] disallowed=[${a.disallowedTools.join(',')}]\n`);
  }
  process.stdout.write(`  formulas: ${manifest.formulas.join(', ')}\n`);

  if (args['baseline-out']) {
    const baselineOut = path.resolve(args['baseline-out']);
    emitBaselinePack({
      out: baselineOut,
      packName: args['baseline-pack-name'],
      sourceVersion: version,
      installPath: args['baseline-install-path'],
      apiUrl: args['api-url'],
    });
    process.stdout.write(`wrote ${baselineOut} (baseline arm)\n`);
  }
}

main();
