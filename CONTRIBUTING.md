# Contributing to Thunder Link

## Branches

- `main` is protected. Nobody pushes to it directly; everything goes through a pull request.
- Make one short-lived branch per task, cut from the latest `main`:

| Type | Name | Example |
|---|---|---|
| Feature | `feature/us-XX-short-name` | `feature/us-05-results-map` |
| Bug fix | `fix/short-name` | `fix/search-empty-query` |
| Docs | `docs/short-name` | `docs/testing-plan` |

- Delete the branch after it's merged. The old personal branches (`Azad-branch`, etc.) are no longer used.

```bash
git checkout main
git pull
git checkout -b feature/us-02-categories-api
```

## Commits

- Start the message with the story ID when there is one: `US-02: return only categories with services`
- Keep each commit to one logical change. Small commits are easier to review.
- Commit your own work from your own GitHub account. The TA grades contributions from the commit history.

## Pull requests

1. Pull `main` into your branch before opening the PR so it's up to date:
   ```bash
   git fetch origin
   git merge origin/main
   ```
2. Run the tests locally (see the README).
3. Push and open a PR into `main`. Fill in the template.
4. Ask a teammate to review. **At least one approval is needed**, and CI must pass.
5. The author merges after approval (use "Squash and merge" if the branch has a lot of small fix-up commits).

### Reviewing

- Check that the code matches the story's acceptance criteria in P1.
- Run it locally if it changes something visible.
- Ask questions in PR comments rather than in chat, so the discussion is in the repo history.

## Tests

- Every new endpoint gets pytest tests in `backend/tests/`. Use the `client` and `make_service` fixtures in `conftest.py`.
- Every new page or component gets a Vitest test in `frontend/tests/`.
- Name tests after the behaviour, e.g. `test_search_with_no_matches_returns_empty_list`.
- Target from P1 (NFR-05): at least 70% backend coverage by the final release.

## Project board

Every user story is a card on the GitHub Projects board. Move your card to **In progress** when you start and **Done** when the PR is merged. The board is what we update the backlog from.

## API changes

If you change an endpoint's URL, parameters or response shape, update [`docs/api.md`](docs/api.md) in the same PR and tell whoever uses it.
