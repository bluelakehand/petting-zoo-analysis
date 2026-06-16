from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from petting_zoo_analysis.experiments.tournament import TournamentResult


def write_tournament_outputs(results: list[TournamentResult], output_dir: str | Path) -> None:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    write_tournament_json(results, path / "tournament-results.json")
    write_tournament_csv(results, path / "tournament-results.csv")
    write_tournament_markdown(results, path / "tournament-summary.md")


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
        "| Policy | Wins | Games | Win Rate | 95% CI | Mean VP Cards | Mean Coins | Mean Cards |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in sorted(results, key=lambda item: item.win_rate, reverse=True):
        lines.append(
            f"| {result.policy_name} | {result.wins} | {result.games} | "
            f"{result.win_rate:.3f} | {result.ci95:.3f} | {result.mean_vp_cards:.2f} | "
            f"{result.mean_coins:.1f} | {result.mean_cards:.1f} |"
        )
    lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")

