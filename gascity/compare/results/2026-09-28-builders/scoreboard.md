# Builder experiment 2026-09-28

Brief: experiments/brief.md. Rig: experiment. Model pin: claude-sonnet-5. Started: 2026-09-28T08:42:24Z.
Each variant ran in its own worktree under experiment-worktrees/, and the critiques ran together. The factory arm was the implement-only step: it read `docs/brief.md` and wrote `site/index.html`, and it did not wait on Telegram.

## Build status

| Arm | Build | Workflow | Score workflow | Note |
|---|---|---|---|---|
| onepage | closed | xpr-g3x | xpr-4ax | /opt/gascity/projects/experiment-worktrees/onepage; score closed |
| factory | closed | xpr-4mf | xpr-obu | /opt/gascity/projects/experiment-worktrees/factory; score closed |
| mol-do-work | closed | xpr-fv0 | xpr-02y | /opt/gascity/projects/experiment-worktrees/mol-do-work; score closed |
| mol-scoped-work | closed | xpr-eir | xpr-1k0 | /opt/gascity/projects/experiment-worktrees/mol-scoped-work; score closed |
| mol-polecat-commit | closed | xpr-t77 | xpr-4nv | /opt/gascity/projects/experiment-worktrees/mol-polecat-commit; score closed |
| impeccable-build | closed | xpr-eld | xpr-4gd | /opt/gascity/projects/experiment-worktrees/impeccable-build; score closed |

# Builder scoreboard

Each row is one Impeccable critique of a page a builder produced. The score is the conductor's report. A difference of one heuristic is within the swing already seen on a single unchanged page.

| Arm | Score | Percent | P0 | P1 | P2 | P3 | Detector findings | Agent time |
|---|---|---|---|---|---|---|---|---|
| onepage | 20/32 | 62% | 0 | 3 | 2 | 0 | 1 | 243s |
| factory | 20/28 | 71% | 0 | 2 | 3 | 0 | 1 | 334s |
| mol-do-work | 23/32 | 72% | 0 | 2 | 2 | 1 | 1 | 251s |
| mol-scoped-work | 23/28 | 82% | 0 | 2 | 2 | 1 | 1 | 238s |
| mol-polecat-commit | 22/32 | 69% | 0 | 3 | 1 | 0 | 1 | 284s |
| impeccable-build | 23/32 | 72% | 0 | 2 | 2 | 0 | 4 | 290s |

The critiques shared one Claude project directory (18 conversations). Transcript span 3505s, output tokens 359,698. Those figures are the pool, not a per-arm measurement. Agent time is the sum of that workflow's closed step durations.
Orchestration gap of 600s or more, counted outside agent time: mol-scoped-work 2613s.

Three pages scored 23 points (mol-do-work, mol-scoped-work, impeccable-build). mol-polecat-commit scored 22. onepage and factory scored 20. No arm has a P0. The higher percents on mol-scoped-work (23/28) and factory (20/28) come from a smaller applicable maximum: those reports marked three heuristics n/a, and the others marked two. impeccable-build is the only page with more than one detector finding (4, all `cramped-padding` at line 0).

mol-scoped-work's synthesize step was still open when the matrix hit its critique deadline. The shared conductor session had already been suspended, so the step was not claimed. After that session was replaced, the conductor wrote `mol-scoped-work-report.md` and closed the workflow. The 2613s gap is that wait. The four steps themselves took 238s.

Compared with `compare/results/2026-09-27-builders/scoreboard.md` (separate rigs, the full factory formula): factory now has a page and a score, where that run stayed blocked on an approval that never became pending. mol-scoped-work now has a page, where that run had none. onepage moved from 21/32 to 20/32. mol-do-work moved from 22/32 to 23/32. mol-polecat-commit moved from 19/28 (one P0) to 22/32 (no P0). impeccable-build stayed 23/32. These are new pages from this checkout, not a rescore of the 2026-09-27 files.
