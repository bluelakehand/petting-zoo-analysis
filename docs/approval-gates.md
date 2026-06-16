# Approval Gates

This project is intentionally staged. Work should pause at each gate until the
listed artifact is reviewed.

## Gate 1: Rules Catalog And Semantics

Status: ready for review.

Review artifacts:

- `docs/rule-transcription-notes.md`
- `src/petting_zoo_analysis/rules/cards.py`
- `tests/test_rules_cards.py`

Acceptance criteria:

- Card catalog includes every market, starting, scoring, Bunny, and Apple
  Picking variant.
- Copy counts match the game: normal cards 5, starting cards 3, scoring cards
  3, Bunny variants 1 each, Apple Picking variants 1 each.
- Victory condition is encoded as owning Gift Shop, Rooster, Dolphin, and
  Kangaroo.
- Spatial terms are encoded as adjacent, diagonal, and surrounding.
- Rules tests pass.

## Gate 2: Deterministic Python Engine

Status: in progress. Visualizer requirement accepted.

Acceptance criteria:

- Seeded games replay deterministically.
- Legal actions are generated separately from applying actions.
- Event logs make sample turns easy to inspect.
- Every card ability has focused tests.
- A visualizer can replay saved games turn by turn.
- The visualizer shows each player's zoo grid, pawn position, roll, activated
  card, ability outcome, coins, VP, market, deck/discard counts, and event log.
- Visualizer review is part of approving engine correctness before large
  simulations.

## Gate 3: Rust Core

Status: blocked on Gate 2 approval.

Acceptance criteria:

- Rust engine matches Python engine on parity tests.
- Rust provides a meaningful simulation speedup.

## Gate 4: Baseline Strategy Tournaments

Status: started with first policy pool and tournament runner.

Acceptance criteria:

- Baseline policy suite runs reproducible tournaments.
- Results include win rates, placements, confidence intervals, and key metrics.

## Gate 5: ML Self-Play

Status: blocked on Gates 3 and 4 approval.

Acceptance criteria:

- Long-run experiment config is reviewed before overnight jobs.
- Training jobs checkpoint and can resume.
- Learned policies are compared against scripted and search policies.

## Gate 6: Final Strategy Report

Status: blocked on Gate 5 approval.

Acceptance criteria:

- Report ranks strategies with evidence and reproducible commands.
- Results include sensitivity by player count and opponent mix.
