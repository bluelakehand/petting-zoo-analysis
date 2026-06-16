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

The starter GitHub repository was empty. The local rule PDF is image-based, so
the next milestone is to finish card/rule transcription from `PZRULES.pdf` and
lock it down with golden tests before trusting large simulation results.

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
