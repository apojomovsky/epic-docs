# AGENTS.md

`epic-docs` is the documentation hub for the epic8 family. It holds only
the site configuration (`mkdocs.yml`), the home and getting-started
pages, the shared includes and the style guide. Every repository keeps
owning its pages in its own `docs/`, next to the code; the hub
assembles them at build time with MkDocs Material plus
`mkdocs-monorepo-plugin`. No content writing happens here outside the
hub-owned pages: the coordinator writes the style guide and templates,
writers come later.

## Picking up work

Work is coordinated by
[epic-tasks](https://github.com/apojomovsky/epic-tasks). **Do not
choose a ticket by reading the issue list.** Every issue filed in this
repo must be on the epic8 board from the moment it is created (the
canonical rule lives in `epic-tasks`' `AGENTS.md`, "Board tracking"
section).

For every ticket:

1. `epic-tasks next` to see what you may take, `epic-tasks claim
   <repo>#<n>` to take it.
2. Create a worktree under `.worktrees/` and branch as
   `<type>/<issue>-<slug>`, never work on `master`.
3. Develop, then dispatch a separate reviewer for the code and address
   its findings (the Review gate, canonical in epic-tasks'
   `AGENTS.md`). Only then run the takeoff ritual (`make
   pre-pr-check`).
4. Open the pull request with `Closes #N`, then `epic-tasks review
   <repo>#<n> --pr <url>`. The body must use real newlines:
   `gh pr create --body-file - <<'EOF'`, never
   `--body "a\nb"` (epic-cc#129).

Set `EPIC_AGENT_ID` (`<runtime>@<host>`) and `EPIC_TASKS_PROJECT` once
per runtime and machine.

## Build and test

```bash
make build         # strict MkDocs build into site/
make serve         # local preview with live reload
make pre-pr-check  # sibling layout check plus strict build
```

Python requirements are pinned in `requirements.txt` and install into
`.venv`. The sibling checkouts (`epic-cc`, `epic-hal`,
`epic-platformio`, `epic-tools`) sit next to this clone; CI checks
them out the same way.

## Commit hygiene

- **Conventional Commits, single line.**
  `feat(scope): summary`, `fix(...)`, `chore(...)`, `docs(...)`.
- **Never `Co-Authored-By:` or any other trailer, and no em-dashes.**
  The commit-msg hook from epic-tasks rejects both; use a comma, a
  colon, or a period and a new sentence.
- **PR bodies use real newlines** (`--body-file` or a heredoc).

## Expression conventions (comments and docs)

1. **Why, not what.** A comment that restates the line below it is
   deleted.
2. **A comment must earn its lines.** Over 8 lines is a hard failure.
3. **No decoration.** No separators, no `@file`/`@brief` boilerplate.
4. **No narrative.** No iteration or session prose in the tree.
5. **No em-dashes in prose.** Not in comments, docs, or commit
   messages.

## CI

`.github/workflows/docs.yml` builds the site strict on every push and
PR, link-checks the built site, and deploys to GitHub Pages from
`master` only.

## Ground rules

- **Never post to a third-party repository.** No write outside the
  `apojomovsky/epic-*` repositories unless the human asks for that
  specific post directly, in your own session (canonical: epic-tasks'
  `AGENTS.md`, "Third-party repositories").
- **No force pushes.** The pre-push hook refuses them; rebase onto
  master instead.
