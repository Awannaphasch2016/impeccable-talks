# Cost by formula step 2026-09-28

The same dollars, one row per arm and phase, are in `cost-map.md`.

Dollars are Claude Code's cost snapshot for the session that ran the step. A session that ran one step keeps that whole snapshot. A session that ran several steps is split by the output tokens of the assistant turns inside each step's start-to-close window. `workflow-finalize` is on every formula and never calls the model, so it is $0 and omitted from the tables.

The 29 closed sessions in `tokens.md` total $21.69. $20.87 of that falls on a formula step. The other $0.82 is a coder pool wake with no step ($0.20) and one manual conductor session ($0.62) opened while mol-scoped-work's synthesize step was unclaimed.

## critique

Six runs of `impeccable` `critique`: prepare, then assess-a and assess-b together, then synthesize.

| Step | Agent | Total | Mean | onepage | factory | mol-do-work | mol-scoped-work | mol-polecat-commit | impeccable-build |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| prepare | conductor | 1.112 | 0.185 | 0.172 | 0.156 | 0.141 | 0.136 | 0.255 | 0.252 |
| assess-a | design-reviewer | 4.875 | 0.813 | 0.898 | 0.806 | 0.730 | 0.838 | 0.844 | 0.759 |
| assess-b | evidence-collector | 2.346 | 0.391 | 0.568 | 0.575 | 0.261 | 0.280 | 0.242 | 0.420 |
| synthesize | conductor | 5.481 | 0.914 | 0.932 | 0.926 | 0.956 | 0.845 | 0.889 | 0.933 |
| **formula** | | **13.814** | **2.302** | **2.570** | **2.463** | **2.088** | **2.099** | **2.230** | **2.364** |

Synthesize is the expensive step on every page. assess-b is the cheap one. The row totals match the design-reviewer ($4.88) and evidence-collector ($2.35) role totals. Conductor is prepare plus synthesize ($6.593). The rest of the conductor role total is the manual session, which is not in this table.

## onepage

| Step | USD |
|---|---:|
| build | 0.253 |

## website-factory

The experiment formula is the implement step only.

| Step | USD |
|---|---:|
| implement | 0.220 |

## build-native

| Step | USD |
|---|---:|
| build | 2.193 |

That session includes its three Task subagents.

## mol-do-work

| Step | USD |
|---|---:|
| do-work | 0.232 |
| drain | 0.168 |
| **formula** | **0.400** |

## mol-polecat-commit

One coder session also started mol-scoped-work. The figures below are the share of that session inside each polecat step.

| Step | USD |
|---|---:|
| load-context | 0.583 |
| workspace-setup | 0.060 |
| preflight-tests | 0.000 |
| implement | 0.102 |
| self-review | 0.055 |
| commit-and-push | 0.058 |
| **formula** | **0.858** |

preflight-tests closed in a few seconds and has no assistant turn of its own. Those tokens sit in the neighboring steps.

## mol-scoped-work

preflight-tests, implement, self-review, and submit closed with no session of their own. The page was written in the load-context and workspace-setup turns. cleanup-worktree then ran again on later coder sessions; each of those sessions only claimed that step.

| Step | USD |
|---|---:|
| load-context | 0.248 |
| workspace-setup | 0.114 |
| preflight-tests | 0.000 |
| implement | 0.000 |
| self-review | 0.000 |
| submit | 0.000 |
| cleanup-worktree | 2.770 |
| **formula** | **3.132** |

The first cleanup session is $0.402. Later passes of the same step are $0.738, $0.468, and $1.162.
