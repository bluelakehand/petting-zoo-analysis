from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from petting_zoo_analysis.engine.replay import replay_payload, write_replay
from petting_zoo_analysis.experiments.tournament import TournamentGame, TournamentResult


def write_tournament_outputs(
    results: list[TournamentResult],
    output_dir: str | Path,
    games: list[TournamentGame] | None = None,
    write_replays: bool = False,
) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    write_tournament_json(results, path / "tournament-results.json")
    write_tournament_csv(results, path / "tournament-results.csv")
    write_tournament_markdown(results, path / "tournament-summary.md")
    if games is not None:
        write_tournament_index(results, games, path / "tournament-index.json", replay_dir=path / "games" if write_replays else None)


def write_tournament_json(results: list[TournamentResult], path: str | Path) -> None:
    Path(path).write_text(json.dumps([asdict(result) for result in results], indent=2), encoding="utf-8")


def write_tournament_csv(results: list[TournamentResult], path: str | Path) -> None:
    fields = list(asdict(results[0]).keys()) if results else list(TournamentResult.__dataclass_fields__)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def write_tournament_markdown(results: list[TournamentResult], path: str | Path) -> None:
    lines = [
        "# Tournament Summary",
        "",
        "| Policy | Wins | Victory Wins | Fallback Wins | Games | Win Rate | 95% CI | Mean Place | Mean Turn | Mean VP Cards | Mean VP | Mean Coins | Mean Cards |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in sorted(results, key=lambda item: item.win_rate, reverse=True):
        lines.append(
            f"| {result.policy_name} | {result.wins} | {result.victory_wins} | {result.fallback_wins} | {result.games} | "
            f"{result.win_rate:.3f} | {result.ci95:.3f} | {result.mean_place:.2f} | {result.mean_turns:.1f} | "
            f"{result.mean_vp_cards:.2f} | {result.mean_vp_total:.2f} | "
            f"{result.mean_coins:.1f} | {result.mean_cards:.1f} |"
        )
    lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_tournament_index(
    results: list[TournamentResult],
    games: list[TournamentGame],
    path: str | Path,
    replay_dir: str | Path | None = None,
) -> None:
    index_path = Path(path)
    replay_path = Path(replay_dir) if replay_dir is not None else None
    if replay_path is not None:
        replay_path.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "schema_version": 1,
        "summary": [asdict(result) for result in results],
        "games": [],
    }
    for game in games:
        replay_file = f"game-{game.game_id:04d}.json"
        replay_url = f"games/{replay_file}"
        if replay_path is not None:
            write_replay(game.state, replay_path / replay_file, seed=game.seed, policies=game.policies)
        entry: dict[str, Any] = {
            "game_id": game.game_id,
            "seed": game.seed,
            "policies": list(game.policies),
            "winner_id": game.winner_id,
            "winner_policy": game.winner_policy,
            "ended_by_victory": game.ended_by_victory,
            "turn_number": game.state.turn_number,
            "placements": game.placements,
            "replay": replay_url if replay_path is not None else None,
        }
        if replay_path is None:
            entry["replay_payload"] = replay_payload(game.state, seed=game.seed, policies=game.policies)
        payload["games"].append(entry)

    index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
