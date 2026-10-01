# Token spend 2026-09-28

Harbor Ledger builder matrix on the `experiment` rig. Model pin `claude-sonnet-5`. Started 2026-09-28T08:42:24Z.

Dollars and token counts are the last `cost-state` snapshot in each Claude Code session. That snapshot is what Claude Code billed for the session, including thinking tokens and the small Haiku title call. A session that spawned Task subagents includes those subagents in the parent snapshot.

The 359,698 critique output-token figure on the first scoreboard pass counted the same assistant message more than once. Claude Code writes several transcript rows per message id. The figures below count each message once, through the cost snapshot.

One coder session (`b266b870`, cwd `/opt/gascity/projects/experiment`) was still running at 10:30 UTC and had no cost snapshot. It is listed after the total and is not in the $21.69.

## Closed sessions

| Phase | Sessions | USD | Input | Output | Thinking | Cache write | Cache read |
|---|---:|---:|---:|---:|---:|---:|---:|
| onepage build | 1 | 0.25 | 12,264 | 4,772 | 655 | 29,043 | 331,535 |
| factory build | 1 | 0.22 | 1,965 | 4,608 | 229 | 26,462 | 328,283 |
| impeccable-build | 1 | 2.19 | 42,122 | 47,848 | 12,783 | 213,608 | 4,575,970 |
| mol coder pool | 8 | 4.59 | 36,278 | 72,645 | 10,695 | 336,189 | 12,306,706 |
| critique | 18 | 14.44 | 230,803 | 179,006 | 37,094 | 910,827 | 14,853,102 |
| **Total** | **29** | **21.69** | **323,432** | **308,879** | **61,456** | **1,516,129** | **32,395,596** |

Of the $21.69, $21.57 is Sonnet 5 and $0.13 is Haiku 4.5 (session titles). Uncached input is 323,432 tokens. Cache reads are 32.4 million tokens, which is most of the context that was billed.

The three mol formulas share two `coder.coder` sessions, and their cwd is the rig checkout, so their build spend is one pool. onepage, factory, and impeccable-build each had their own worktree cwd. impeccable-build's $2.19 includes three Task subagents.

## Critique by role

| Role | Sessions | USD | Output | Thinking | Cache read |
|---|---:|---:|---:|---:|---:|
| conductor | 8 | 7.21 | 83,911 | 11,827 | 8,903,340 |
| design-reviewer | 6 | 4.88 | 71,672 | 22,802 | 3,419,260 |
| evidence-collector | 4 | 2.35 | 23,423 | 2,465 | 2,530,502 |
| **Critique total** | **18** | **14.44** | **179,006** | **37,094** | **14,853,102** |

## Critique sessions that named one workflow

A session whose transcript names a single score workflow is charged to that arm. Six sessions named more than one workflow, because the critique agents are a shared pool; that $4.42 is not split.

| Arm | Sessions | USD |
|---|---:|---:|
| onepage | 3 | 2.57 |
| factory | 3 | 2.46 |
| mol-polecat-commit | 2 | 1.73 |
| impeccable-build | 2 | 1.69 |
| mol-scoped-work | 1 | 0.84 |
| mol-do-work | 1 | 0.73 |
| shared across arms | 6 | 4.42 |
| **Critique total** | **18** | **14.44** |

## Still open, not in the total

Coder session `b266b870` had no cost snapshot at 10:30 UTC. Deduped message usage at that moment: 74 input, 14,203 output, 48,280 cache write, 2,195,038 cache read. Thinking tokens are not separated until a cost snapshot is written.
