# Notebooks Overview (Student Guide)

This folder contains a template to help you build, test, and submit a Prisoner’s Dilemma Player for the class tournament.

## Quick intro: The Prisoner’s Dilemma Tournament
- Each round, two players simultaneously choose one of two actions:
  - Cooperate (`C`)
  - Defect (`D`)
- Payoffs per round follow the standard Prisoner’s Dilemma ordering: Temptation > Reward > Punishment > Sucker (T > R > P > S).
- In the `Axelrod` library we use in this project, the default scores are:
  - `C`/`C`: R, R = 3, 3 (mutual Reward for cooperation)
  - `D`/`D`: P, P = 1, 1 (mutual Punishment for defection)
  - `C`/`D`: S, T = 0 (Sucker for cooperator), 5 (Temptation for defector)

### How a match works
- A match is a sequence of many rounds (turns). The default for our tournament scripts is 200 turns.
- On each turn, your `strategy(self, opponent)` method chooses `Action.C` (cooperate) or `Action.D` (defect).
- After every turn, both players receive points based on the payoff rules above. Your total match score is the sum across all turns.

### How the class tournament works
- We run a round‑robin: every submitted Player plays one match against every other submitted Player.
- Each Player’s tournament score is the sum of their scores from all matches.
- Final standings are determined by total score (higher is better). Ties are possible.

Behind the scenes, our tournament tooling uses the `Axelrod` library and a small engine included in this repo:
- `tournament/engine/referee.py` runs a single match and produces the total scores for both players.
- `tournament/engine/tournament.py` runs a full round‑robin and aggregates totals and rankings.

## Using the Template notebook
Use `Template.ipynb` in this folder to develop and test your Player. The notebook includes:
1) A brief API reminder for `axelrod.Player`
2) A code cell with the required imports and a template for a `Player` class.
3) A script that plays a short match so you can sanity‑check your `Player` implementation.

Basic workflow:
1. Open `Template.ipynb` in your IDE (e.g., Colab, VS Code, Pycharm).
2. Edit the template class:
   - Implement `def strategy(self, opponent) -> Action` and return `Action.C` or `Action.D` each turn.
   - Give the class a unique Python class name and set a human‑friendly `name` attribute.
   - Include a docstring listing the student(s) who authored it.
3. Run the provided test cell to make sure the class runs without errors and behaves as expected.
4. Submit your Player to the tournament on GitHub - detailed instructions included in the Template notebook.

Tip: Keep your strategy clear and test iteratively in the notebook. When you change your design, rerun the test cell to confirm behavior.

Good luck and have fun!
