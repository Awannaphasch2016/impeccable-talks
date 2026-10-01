// Text transforms shared by the converter. Mirrors the subset of Impeccable's
// scripts/lib/utils.js that the Gas City target needs, plus the Go-template
// escaping that `gc prime` requires (it renders prompt.template.md with
// text/template, so any literal `{{` left in Impeccable prose would either be
// evaluated or fail the parse).

// Every provider tag Impeccable's compileProviderBlocks recognizes. A block
// whose tag is not in this set is ordinary markup and passes through.
export const PROVIDER_BLOCK_TAGS = new Set([
  'agents', 'antigravity', 'claude', 'claude-code', 'codex', 'cursor',
  'gemini', 'copilot', 'github-copilot', 'windsurf', 'kilo', 'kiro',
  'amp', 'opencode', 'roo', 'cline', 'trae', 'zed', 'junie', 'augment',
  'goose', 'kimi', 'droid', 'pi', 'grok', 'gascity',
]);

// The underlying harness inside a Gas City session is Claude Code, so
// `<claude>` blocks apply. `<gascity>` is reserved for blocks written for
// this target specifically (none exist upstream yet).
export const GASCITY_ACTIVE_TAGS = ['claude', 'claude-code', 'gascity'];

export function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: markdown };
  const data = {};
  let listKey = null;
  for (const rawLine of match[1].split(/\r?\n/)) {
    const line = rawLine.replace(/\s+$/, '');
    if (!line.trim()) continue;
    const item = line.match(/^\s+-\s+(.*)$/);
    if (item && listKey) {
      data[listKey].push(stripQuotes(item[1]));
      continue;
    }
    const kv = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!kv) continue;
    const [, key, value] = kv;
    if (value === '') {
      data[key] = [];
      listKey = key;
    } else {
      data[key] = stripQuotes(value);
      listKey = null;
    }
  }
  return { data, body: match[2] };
}

function stripQuotes(value) {
  const v = value.trim();
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1);
  }
  return v;
}

// Keep the body of active provider blocks, drop the others, leave unknown
// tags alone. Same regex as upstream so both compilers agree on block shape.
export function compileProviderBlocks(content, activeTags = GASCITY_ACTIVE_TAGS) {
  const active = new Set(activeTags);
  const pattern = /(^|\r?\n)[ \t]*<([a-z][a-z0-9-]*)>[ \t]*\r?\n([\s\S]*?)\r?\n[ \t]*<\/\2>[ \t]*(?=\r?\n|$)/g;
  let touched = false;
  const out = content.replace(pattern, (match, prefix, tag, body) => {
    if (!PROVIDER_BLOCK_TAGS.has(tag)) return match;
    touched = true;
    return active.has(tag) ? `${prefix}${body}` : prefix;
  });
  return touched ? out.replace(/(?:\r?\n){3,}/g, '\n\n') : out;
}

// `<!-- rule:name -->` markers are build-time bookkeeping for Impeccable's
// detector tests. They carry nothing an agent should read.
export function stripRuleMarkers(content) {
  return content.replace(/[ \t]*<!--\s*rule:[a-z0-9-]+\s*-->/g, '');
}

export const IMPECCABLE_SUB_COMMANDS = [
  'adapt', 'animate', 'audit', 'bolder', 'clarify', 'colorize',
  'critique', 'delight', 'distill', 'document', 'harden', 'layout',
  'onboard', 'optimize', 'overdrive', 'polish', 'quieter', 'shape', 'typeset',
];

// Placeholder values for the Gas City target. Impeccable's own table keys
// these by provider; Gas City is a harness around Claude Code with nobody at
// the terminal, which is what changes ask_instruction and command_prefix.
export function gascityPlaceholders({ packName, packEnv, formulas }) {
  const sling = `gc sling $GC_RIG/${packName}.conductor`;
  return {
    model: 'inherit',
    config_file: 'CLAUDE.md',
    scripts_path: `$${packEnv}/skill/scripts`,
    ask_instruction:
      'Nobody is at your terminal. Do not call an interactive question tool ' +
      'and do not wait for typed input. Write the questions, each with 2-3 ' +
      'concrete options, under a `## Questions for the user` heading at the ' +
      'end of the report file your step names, then close the step.',
    command_prefix: `${sling} `,
    sling,
    available_commands: formulas.map((f) => `\`${sling} ${f} --formula\``).join(', '),
  };
}

export function replacePlaceholders(content, values) {
  return content
    // `{{command_prefix}}impeccable polish` reads as a slash command upstream;
    // the Gas City equivalent is slinging the formula of the same name.
    .replace(/\{\{command_prefix\}\}impeccable ([a-z]+)/g, (_, cmd) => `${values.sling} ${cmd} --formula`)
    .replace(/\{\{model\}\}/g, values.model)
    .replace(/\{\{config_file\}\}/g, values.config_file)
    .replace(/\{\{ask_instruction\}\}/g, values.ask_instruction)
    .replace(/\{\{command_prefix\}\}/g, values.command_prefix)
    .replace(/\{\{available_commands\}\}/g, values.available_commands)
    .replace(/\{\{scripts_path\}\}/g, values.scripts_path)
    .replace(/\{\{command_hint\}\}/g, IMPECCABLE_SUB_COMMANDS.join('|'));
}

// Go text/template treats `{{` as an action. Any that survive placeholder
// replacement are Impeccable prose (or a genuine template example) and must be
// emitted literally. `{{"{{"}}` is the canonical way to print a literal brace pair.
export function escapeGoTemplate(content) {
  return content.replace(/\{\{/g, '\u0000OPEN\u0000').replace(/\}\}/g, '\u0000CLOSE\u0000')
    .replace(/\u0000OPEN\u0000/g, '{{"{{"}}')
    .replace(/\u0000CLOSE\u0000/g, '{{"}}"}}');
}

// Returns the markdown between a heading line and the next heading of equal
// or higher level (or an explicit stop heading). Used to lift Assessment A,
// Assessment B and the synthesis instructions out of critique.md verbatim so
// the Gas City agents stay in sync with upstream text.
export function sliceSection(markdown, startHeading, stopHeading = null) {
  const lines = markdown.split(/\r?\n/);
  const startIdx = lines.findIndex((l) => l.trim() === startHeading.trim());
  if (startIdx === -1) throw new Error(`heading not found: ${startHeading}`);
  const level = startHeading.match(/^#+/)[0].length;
  let endIdx = lines.length;
  for (let i = startIdx + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (stopHeading && line.trim() === stopHeading.trim()) { endIdx = i; break; }
    if (!stopHeading) {
      const m = line.match(/^(#+)\s/);
      if (m && m[1].length <= level) { endIdx = i; break; }
    }
  }
  return lines.slice(startIdx, endIdx).join('\n').trimEnd() + '\n';
}

export function tomlString(value) {
  return JSON.stringify(String(value));
}

// TOML multi-line literal for step descriptions and similar prose.
export function tomlMultiline(value) {
  const safe = String(value).replace(/"""/g, '""\\"');
  return `"""\n${safe.replace(/\s+$/, '')}\n"""`;
}

export function slugify(name) {
  return name.toLowerCase().replace(/^impeccable-/, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}
