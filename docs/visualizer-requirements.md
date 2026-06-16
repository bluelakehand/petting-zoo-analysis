# Game Visualizer Requirements

The simulator must produce replayable game logs, and the project must include a
visualizer before large strategy experiments are trusted.

## Purpose

The visualizer exists so played games can be reviewed by a human and compared
against expected Petting Zoo behavior. It is an engine-validation tool first,
not a polished product dashboard.

## Required Views

- Turn timeline with previous/next/play controls.
- Current player's roll and chosen action.
- Each player's zoo grid with card names, icons, roll values, and pawn
  position.
- A visible pawn/customer marker on the card last visited by each player.
- Highlighted movement path, activated card, and purchased card.
- Player summary: coins, VP, cards owned, and current turn earnings.
- Supply stack counts and game end status.
- Event log showing rule-relevant state changes for the selected turn.

## Required Data

Each replay log must include:

- Game config, RNG seed, player policies, and card catalog version.
- Initial state.
- Per-turn snapshots before and after action resolution.
- Die rolls, legal actions considered where practical, selected actions, and
  ability events.
- Final scoring and winner.

## Recommended Tech

- Build the first version as a lightweight local HTML/JavaScript viewer served
  by Python or opened from a static file.
- Keep the replay format JSON so Python, Rust, and future ML tools can all emit
  and consume the same artifact.
- Do not block engine work on visual polish; prioritize correctness,
  inspectability, and deterministic replay.

## Approval Role

Gate 2 cannot be approved until sample games can be replayed visually and the
observed behavior matches expectations.
