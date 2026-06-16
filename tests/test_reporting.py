import json

from petting_zoo_analysis.experiments.reporting import write_tournament_outputs
from petting_zoo_analysis.experiments.tournament import run_policy_tournament, run_policy_tournament_games, summarize_tournament_games


def test_tournament_outputs_are_written(tmp_path) -> None:
    results = run_policy_tournament(game_count=3, player_count=3, max_turns=5)

    write_tournament_outputs(results, tmp_path)

    assert (tmp_path / "tournament-results.json").exists()
    assert (tmp_path / "tournament-results.csv").exists()
    assert (tmp_path / "tournament-summary.md").exists()
    loaded = json.loads((tmp_path / "tournament-results.json").read_text(encoding="utf-8"))
    assert loaded
    assert "policy_name" in loaded[0]


def test_tournament_outputs_can_include_game_replays(tmp_path) -> None:
    games = run_policy_tournament_games(game_count=2, player_count=3, max_turns=5)
    results = summarize_tournament_games(games)

    write_tournament_outputs(results, tmp_path, games=games, write_replays=True)

    index_path = tmp_path / "tournament-index.json"
    assert index_path.exists()
    loaded = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(loaded["games"]) == 2
    assert loaded["games"][0]["replay"] == "games/game-0000.json"
    assert (tmp_path / loaded["games"][0]["replay"]).exists()
