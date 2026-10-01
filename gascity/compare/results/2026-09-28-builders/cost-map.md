# Cost map 2026-09-28

Each row is one formula step on one arm. Phase is `build` or `critique`. Dollars are the Claude Code cost snapshot for the session that ran the step. A session that ran several steps is split by the output tokens inside each step window. `workflow-finalize` is on every formula, never calls the model, and is $0, so it is left off.

Mapped steps total $20.870. The closed-session total in `tokens.md` is $21.69. The other $0.823 has no formula step.

## Map

| USD | Formula | Step | Arm | Phase |
|---:|---|---|---|---|
| 0.253 | onepage | build | onepage | build |
| 0.172 | critique | prepare | onepage | critique |
| 0.898 | critique | assess-a | onepage | critique |
| 0.568 | critique | assess-b | onepage | critique |
| 0.932 | critique | synthesize | onepage | critique |
| 0.220 | website-factory | implement | factory | build |
| 0.156 | critique | prepare | factory | critique |
| 0.806 | critique | assess-a | factory | critique |
| 0.575 | critique | assess-b | factory | critique |
| 0.926 | critique | synthesize | factory | critique |
| 0.232 | mol-do-work | do-work | mol-do-work | build |
| 0.168 | mol-do-work | drain | mol-do-work | build |
| 0.141 | critique | prepare | mol-do-work | critique |
| 0.730 | critique | assess-a | mol-do-work | critique |
| 0.261 | critique | assess-b | mol-do-work | critique |
| 0.956 | critique | synthesize | mol-do-work | critique |
| 0.248 | mol-scoped-work | load-context | mol-scoped-work | build |
| 0.114 | mol-scoped-work | workspace-setup | mol-scoped-work | build |
| 0.000 | mol-scoped-work | preflight-tests | mol-scoped-work | build |
| 0.000 | mol-scoped-work | implement | mol-scoped-work | build |
| 0.000 | mol-scoped-work | self-review | mol-scoped-work | build |
| 0.000 | mol-scoped-work | submit | mol-scoped-work | build |
| 2.770 | mol-scoped-work | cleanup-worktree | mol-scoped-work | build |
| 0.136 | critique | prepare | mol-scoped-work | critique |
| 0.838 | critique | assess-a | mol-scoped-work | critique |
| 0.280 | critique | assess-b | mol-scoped-work | critique |
| 0.845 | critique | synthesize | mol-scoped-work | critique |
| 0.583 | mol-polecat-commit | load-context | mol-polecat-commit | build |
| 0.060 | mol-polecat-commit | workspace-setup | mol-polecat-commit | build |
| 0.000 | mol-polecat-commit | preflight-tests | mol-polecat-commit | build |
| 0.102 | mol-polecat-commit | implement | mol-polecat-commit | build |
| 0.055 | mol-polecat-commit | self-review | mol-polecat-commit | build |
| 0.058 | mol-polecat-commit | commit-and-push | mol-polecat-commit | build |
| 0.255 | critique | prepare | mol-polecat-commit | critique |
| 0.844 | critique | assess-a | mol-polecat-commit | critique |
| 0.242 | critique | assess-b | mol-polecat-commit | critique |
| 0.889 | critique | synthesize | mol-polecat-commit | critique |
| 2.193 | build-native | build | impeccable-build | build |
| 0.252 | critique | prepare | impeccable-build | critique |
| 0.759 | critique | assess-a | impeccable-build | critique |
| 0.420 | critique | assess-b | impeccable-build | critique |
| 0.933 | critique | synthesize | impeccable-build | critique |

`build-native` is the Impeccable builder (`impeccable-native.runner`). `mol-polecat-commit` is the polecat molecule on the shared `coder.coder`. `critique` is the Impeccable scorer, run once per arm.

## Arm totals

| Arm | Build formula | Build | Critique | Arm total |
|---|---|---:|---:|---:|
| onepage | onepage | 0.253 | 2.570 | 2.823 |
| factory | website-factory | 0.220 | 2.463 | 2.683 |
| mol-do-work | mol-do-work | 0.400 | 2.088 | 2.488 |
| mol-polecat-commit | mol-polecat-commit | 0.858 | 2.230 | 3.088 |
| impeccable-build | build-native | 2.193 | 2.364 | 4.557 |
| mol-scoped-work | mol-scoped-work | 3.132 | 2.099 | 5.231 |
| **Mapped** | | **7.056** | **13.814** | **20.870** |

## Not a formula step

| USD | What | Arm | Phase |
|---:|---|---|---|
| 0.203 | coder pool wake, no step claimed | — | — |
| 0.620 | manual conductor session while mol-scoped-work synthesize was unclaimed | mol-scoped-work | critique |
| **0.823** | | | |
