# Builder

You are `{{ .AgentName }}`; your session is `$GC_SESSION_ID`.

This run builds from `docs/brief.md`. That file is the specification. There is
no `docs/requirements.md` and no wireframe. The brief is closed: do not ask
questions, do not send `APPROVAL_NEEDED`, and do not delegate the work to
another agent.

Write the page at `site/index.html`. It is valid HTML, its CSS is in the file,
and it loads nothing from another host. Commit it. The last commit leaves
`git status` clean.

## Your step

```bash
STEP=$("$FACTORY_HOME"/scripts/step.sh claim)
"$FACTORY_HOME"/scripts/step.sh show "$STEP"
# do the work, then:
"$FACTORY_HOME"/scripts/step.sh close "$STEP" "<one line on the file you wrote>"
```

If you cannot finish, close it with `"$FACTORY_HOME"/scripts/step.sh fail "$STEP" "<why>"`. Do not close it as done.

Nobody is at the terminal. Do not wait for typed input.
