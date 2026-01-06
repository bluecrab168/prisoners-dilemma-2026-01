# Prisoner’s Dilemma Class Tournament

A lightweight toolkit for running a class tournament of Iterated Prisoner’s Dilemma strategies built on the `Axelrod` library.

## Students
See the student guide in `notebooks/README.md` for a quick intro to the game, how matches and tournaments are scored, 
and how to use the provided template notebook to build and test your `Player`. 
Submission is done by copy‑pasting your Player class into the GitHub Issue form in this repo.

## Instructors
This repository is designed as a (GitHub Template Repository)[https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository#about-template-repositories]
 for creating class tournaments.

### 1) Create a new course repo from this template
- On GitHub, click “Use this template” on this repo and create a new repository for your course.
- Ensure GitHub Issues are enabled (Settings → General → Features → Issues).
- Ensure GitHub Actions are enabled (Settings → Actions → General → Allow all actions). 
  The GH Actions workflow documented below processes student submissions posed in the Issues.

### 2) How student submissions are collected
- Students open a new Issue using the “Player Submission” Issue form (see `.github/ISSUE_TEMPLATE/player_submission.yml`).
- They paste their complete `axelrod.Player` subclass inside triple backticks in the form’s textarea.
- The GitHub Action `.github/workflows/handle_submission.yml` runs on issue open/edit when the `submission` label is present:
  - Extracts the first fenced code block from the issue body.
  - Writes it to `tournament/players/<github-username>.py`.
  - Imports the module, finds `axelrod.Player` subclasses, and validates them using the local validation utility.
  - Posts a pass/fail comment back to the issue with details.

### 3) Configure GitHub to allow PR automation
To let the workflow open pull requests that add student players, configure these settings on the copied repository:
- Repository Settings → Actions → General
  - Workflow permissions: set to “Read and write permissions”.
  - Allow GitHub Actions to create and approve pull requests: enable this checkbox.
- Ensure a `submission` label exists (used by the workflow and Issue Form):
- Optional fallback if org policy forbids PRs by `GITHUB_TOKEN`:
  - Create a fine‑grained PAT on a maintainer account with repo access and Pull Requests/Contents write permissions.
  - Save it as a repository secret (e.g., `PR_AUTOMATION_TOKEN`) and configure the PR step to use it.

After these settings, when a submission passes validation the workflow will open a PR that only includes files under `tournament/players/` (the new player module and the auto‑generated `_registry.py`). Merging the PR will auto‑close the originating Issue via the `Closes #<issue-number>` link in the PR description.

### 4) How the players registry is built
- The tournament uses a generated registry (`tournament/players/_registry.py`) that lists all Player classes to include by default.
- Build or refresh the registry any time Players change by running:
  ```bash
  # install (editable) and dependencies
  pip install -e .
  # rebuild the registry by scanning tournament.players
  python -m tournament.scripts.build_registry
  ```
- The script imports Python files from `tournament/players/` and writes `_registry.py` with explicit imports and a `REGISTERED_PLAYERS` list. 
    - Use `--dry-run` to preview and `--verbose` for discovery logs.


### 5) How to run the tournament
- After refreshing the registry, run a round‑robin among registered Players:
  ```bash
  python -m tournament.scripts.run_tournament --turns 200 --seed 123
  ```
- Output includes per‑player totals, ranking, and per‑match scores. Adjust `--turns` and `--seed` as desired.

Notes:
- You can locally validate either a specific class or all registered classes:
  ```bash
  # validate a specific class
  python -m tournament.scripts.validate_player tournament.players.cooperator:Cooperator
  # validate all registered players
  python -m tournament.scripts.validate_player
  ```
- A simple file watcher is available for classroom development convenience:
  ```bash
  python -m tournament.scripts.watch_players --interval 1.0
  ```

## Credits
- Built on the `Axelrod` library for the Iterated Prisoner’s Dilemma:
  - GitHub: https://github.com/Axelrod-Python/Axelrod
  - Documentation: https://axelrod.readthedocs.io/
- References for further reading:
  - Robert Axelrod (1984), “The Evolution of Cooperation.” Basic Books.
  - William Poundstone (1992), “Prisoner’s Dilemma.” Anchor Books.
- Code co‑authored by `powderflask` and Junie (JetBrains autonomous programmer's assistant).