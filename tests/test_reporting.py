import json

from petting_zoo_analysis.experiments.reporting import write_tournament_outputs
from petting_zoo_analysis.experiments.tournament import run_policy_tournament


def test_tournament_outputs_are_written(tmp_path) -> None:
    results = run_policy_tournament(game_count=3, player_count=3, max_turns=5)

    write_tournament_outputs(results, tmp_path)

    assert (tmp_path / "tournament-results.json").exists()
    assert (tmp_path / "tournament-results.csv").exists()
    assert (tmp_path / "tournament-summary.md").exists()
    loaded = json.loads((tmp_path / "tournament-results.json").read_text(encoding="utf-8"))
    assert loaded
    assert "policy_name" in loaded[0]

