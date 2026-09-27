// Reproduces Impeccable's own Claude Code build (scripts/lib/transformers,
// provider 'claude-code') from the skill source. The baseline arm of the
// comparison needs the skill installed the way a developer would have it;
// `npx impeccable install` downloads a prebuilt bundle, and when that download
// is unavailable this produces the same layout from the checkout:
//
//   .claude/skills/impeccable/SKILL.md
//   .claude/skills/impeccable/reference/*.md
//   .claude/skills/impeccable/scripts/**
//   .claude/agents/impeccable-*.md
import fs from 'node:fs';
import path from 'node:path';
import {
  parseFrontmatter, compileProviderBlocks, stripRuleMarkers, IMPECCABLE_SUB_COMMANDS,
} from './text.mjs';

const CLAUDE_TAGS = ['claude-code', 'claude'];
const CONFIG_DIR = '.claude';
const SKILL_NAME = 'impeccable';
const SCRIPTS_PATH = `${CONFIG_DIR}/skills/${SKILL_NAME}/scripts`;

// PROVIDER_PLACEHOLDERS['claude-code'] upstream.
const PLACEHOLDERS = {
  model: 'Claude',
  config_file: 'CLAUDE.md',
  ask_instruction: 'STOP and call the AskUserQuestion tool to clarify.',
  command_prefix: '/',
};

function replaceClaudePlaceholders(content) {
  const commands = IMPECCABLE_SUB_COMMANDS.map((n) => `/impeccable ${n}`).join(', ');
  return content
    .replace(/\{\{model\}\}/g, PLACEHOLDERS.model)
    .replace(/\{\{config_file\}\}/g, PLACEHOLDERS.config_file)
    .replace(/\{\{ask_instruction\}\}/g, PLACEHOLDERS.ask_instruction)
    .replace(/\{\{command_prefix\}\}/g, PLACEHOLDERS.command_prefix)
    .replace(/\{\{available_commands\}\}/g, commands)
    .replace(/\{\{scripts_path\}\}/g, SCRIPTS_PATH)
    .replace(/\{\{command_hint\}\}/g, IMPECCABLE_SUB_COMMANDS.join('|'));
}

function compile(markdown) {
  return replaceClaudePlaceholders(stripRuleMarkers(compileProviderBlocks(markdown, CLAUDE_TAGS)));
}

function yamlScalar(value) {
  const v = String(value);
  // Frontmatter numbers and booleans (maxTurns, user-invocable) are meant to
  // be typed, so they stay bare; everything else that YAML would misread is quoted.
  if (/^(\d+|true|false)$/.test(v)) return v;
  if (v === '' || /^\s|\s$|: |\s#|:$|^[\[\]{},&*!|>'"%@`#]|^[?:-](\s|$)|^(null|yes|no|on|off|~)$|^-?\d/i.test(v)) {
    return JSON.stringify(v);
  }
  return v;
}

function frontmatter(data) {
  const lines = ['---'];
  for (const [key, value] of Object.entries(data)) {
    if (value === undefined || value === null) continue;
    if (Array.isArray(value)) {
      lines.push(`${key}:`);
      for (const item of value) lines.push(`  - ${yamlScalar(item)}`);
    } else {
      lines.push(`${key}: ${yamlScalar(value)}`);
    }
  }
  lines.push('---');
  return lines.join('\n');
}

function write(file, content) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content);
}

function copyTree(src, dst) {
  fs.mkdirSync(dst, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dst, entry.name);
    if (entry.isDirectory()) copyTree(s, d);
    else { fs.copyFileSync(s, d); fs.chmodSync(d, fs.statSync(s).mode); }
  }
}

export function emitClaudeBuild({ source, out }) {
  const skillSrc = path.join(source, 'skill');
  const skillDir = path.join(out, CONFIG_DIR, 'skills', SKILL_NAME);
  fs.rmSync(path.join(out, CONFIG_DIR, 'skills', SKILL_NAME), { recursive: true, force: true });
  fs.rmSync(path.join(out, CONFIG_DIR, 'agents'), { recursive: true, force: true });

  const { data, body } = parseFrontmatter(fs.readFileSync(path.join(skillSrc, 'SKILL.src.md'), 'utf8'));
  // Upstream's claude-code provider keeps these fields and drops allowed-tools,
  // which blocks skill activation in non-interactive sessions (issue #736).
  const fm = {
    name: data.name,
    description: data.description,
    'argument-hint': (data['argument-hint'] || '').replace('{{command_hint}}', IMPECCABLE_SUB_COMMANDS.join('|')),
    'user-invocable': data['user-invocable'],
    license: data.license,
  };
  write(path.join(skillDir, 'SKILL.md'), `${frontmatter(fm)}\n\n${compile(body)}`);

  let refs = 0;
  for (const f of fs.readdirSync(path.join(skillSrc, 'reference'))) {
    write(path.join(skillDir, 'reference', f), compile(fs.readFileSync(path.join(skillSrc, 'reference', f), 'utf8')));
    refs += 1;
  }
  copyTree(path.join(skillSrc, 'scripts'), path.join(skillDir, 'scripts'));

  const agents = [];
  for (const f of fs.readdirSync(path.join(skillSrc, 'agents')).filter((n) => n.endsWith('.md'))) {
    const parsed = parseFrontmatter(fs.readFileSync(path.join(skillSrc, 'agents', f), 'utf8'));
    const a = parsed.data;
    const fmAgent = {
      name: a.name,
      description: a.description,
      tools: a.tools,
      model: a.model,
      effort: a.effort,
      maxTurns: a['max-turns'],
    };
    write(path.join(out, CONFIG_DIR, 'agents', `${a.name}.md`), `${frontmatter(fmAgent)}\n${compile(parsed.body).trim()}\n`);
    agents.push(a.name);
  }
  return { skillDir, refs, agents };
}
