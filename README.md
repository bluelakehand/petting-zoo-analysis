# Petting Zoo Strategy Analysis

This project is for finding high-performing strategies in the card game
Petting Zoo through rules-accurate simulation, search, and machine learning.

The repository is intentionally structured in layers:

- `src/petting_zoo_analysis/rules`: authoritative game/card definitions.
- `src/petting_zoo_analysis/engine`: deterministic state transitions.
- `src/petting_zoo_analysis/policies`: bots and decision policies.
- `src/petting_zoo_analysis/experiments`: simulation batches and analysis.
- `docs`: research plan, rule assumptions, and validation notes.

## Current Status

The rules catalog, deterministic Python engine, replay visualizer, and first
baseline policy tournament runner are in place. The current engine uses full
shared supply stacks, optional buying, and the four-card victory condition.

Current review artifacts:

- `docs/rules-validation-report.md`
- `docs/baseline-tournament-notes.md`
- `visualizer/index.html`

## First Research Question

What strategy maximizes win rate across thousands of simulated Petting Zoo
games under realistic player counts and opponent mixes?

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Replay Visualizer

Generate a sample replay:

```powershell
$env:PYTHONPATH='src'
python -m petting_zoo_analysis.experiments.write_sample_replay
```

Serve the repo and open:

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Then visit:

```text
http://127.0.0.1:8765/visualizer/index.html?replay=../sample-replay.json
```

## Baseline Tournament

Run a baseline policy tournament and write JSON/CSV/Markdown outputs:

```powershell
$env:PYTHONPATH='src'
python -m petting_zoo_analysis.experiments.run_batch --games 300 --players 3 --max-turns 80 --output-dir results\baseline-300
```
