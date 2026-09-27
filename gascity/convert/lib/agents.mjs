import { parseFrontmatter, slugify } from './text.mjs';

// Claude Code tools that change state or reach outside the repo. An
// Impeccable agent that does not list one of these in its `tools:` line is
// launched with it disallowed, which is how the advisory tool list in the
// frontmatter becomes an enforced one under Gas City.
const GATED_TOOLS = ['Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'WebFetch', 'WebSearch'];

// Never available to a pack agent. Fan-out belongs to the formula, not to a
// nested Task call, and no human sits at the tmux pane to answer a question.
const ALWAYS_DISALLOWED = ['Task', 'AskUserQuestion'];

const EFFORT_TIERS = new Set(['low', 'medium', 'high', 'xhigh', 'max']);

export function disallowedToolsFor(tools) {
  const allowed = new Set(tools.map((t) => t.trim()));
  const gated = GATED_TOOLS.filter((t) => !allowed.has(t));
  return [...new Set([...gated, ...ALWAYS_DISALLOWED])];
}

export function isReadOnly(tools) {
  const allowed = new Set(tools.map((t) => t.trim()));
  return !['Write', 'Edit', 'MultiEdit', 'NotebookEdit'].some((t) => allowed.has(t));
}

function splitTools(value) {
  if (Array.isArray(value)) return value;
  if (!value) return [];
  return String(value).split(',').map((t) => t.trim()).filter(Boolean);
}

// One `skill/agents/*.md` file -> the agent record the emitter needs.
export function agentFromImpeccable(markdown, fileName) {
  const { data, body } = parseFrontmatter(markdown);
  const name = data.name || fileName.replace(/\.md$/, '');
  const tools = splitTools(data.tools);
  return {
    dirName: slugify(name),
    sourceName: name,
    description: data.description || '',
    tools,
    readOnly: isReadOnly(tools),
    disallowedTools: disallowedToolsFor(tools),
    effort: EFFORT_TIERS.has(data.effort) ? data.effort : null,
    model: data.model && data.model !== 'inherit' ? data.model : null,
    maxTurns: data['max-turns'] ? Number(data['max-turns']) : null,
    body,
    origin: `skill/agents/${fileName}`,
  };
}

// Agents that exist in the Gas City pack but not as files upstream. In
// Impeccable these roles live inside the parent's turn (the critique command
// spawns two anonymous sub-agents and then synthesizes in its own context).
// Gas City has no parent context, so each role becomes an agent of its own.
export function syntheticAgents() {
  return [
    {
      dirName: 'conductor',
      sourceName: 'critique parent context',
      description: 'Prepares the critique packet for the assessors, then synthesizes both assessments into the report, persists the snapshot, and records the questions for the user.',
      tools: ['Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep'],
      effort: 'high',
      model: null,
      maxTurns: null,
      origin: 'skill/reference/critique.md (Setup, Generate Combined Critique Report, Persist the Snapshot, Ask the User)',
      template: 'conductor.md',
    },
    {
      dirName: 'design-reviewer',
      sourceName: 'critique Assessment A sub-agent',
      description: 'Assessment A: unanchored design review of one target. Never sees detector output or the other assessment.',
      tools: ['Read', 'Bash', 'Glob', 'Grep', 'WebFetch'],
      effort: 'high',
      model: null,
      maxTurns: null,
      origin: 'skill/reference/critique.md (Assessment A: Design Review, Reference Material)',
      template: 'design-reviewer.md',
    },
    {
      dirName: 'evidence-collector',
      sourceName: 'critique Assessment B sub-agent',
      description: 'Assessment B: deterministic detector scan and browser evidence for one target. Never sees the design review.',
      tools: ['Read', 'Bash', 'Glob', 'Grep', 'WebFetch'],
      effort: 'medium',
      model: null,
      maxTurns: null,
      origin: 'skill/reference/critique.md (Assessment B: Detector + Browser Evidence)',
      template: 'evidence-collector.md',
    },
  ].map((a) => ({
    ...a,
    readOnly: isReadOnly(a.tools),
    disallowedTools: disallowedToolsFor(a.tools),
  }));
}
