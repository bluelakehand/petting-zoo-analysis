from petting_zoo_analysis.engine.simulate import legal_buys, new_game
from petting_zoo_analysis.engine.state import GameConfig
from petting_zoo_analysis.experiments.run_batch import run_smoke_batch
from petting_zoo_analysis.experiments.tournament import POLICY_FACTORIES, run_policy_tournament


def test_all_policy_factories_can_choose_from_initial_state() -> None:
    state = new_game(config=GameConfig(player_count=3), seed=3)
    buys = legal_buys(state)

    for factory in POLICY_FACTORIES.values():
        policy = factory()
        policy.choose_buy(state, buys, __import__("random").Random(1))


def test_tournament_returns_summary_for_policy_pool() -> None:
    results = run_policy_tournament(game_count=5, player_count=3, max_turns=10)

    assert results
    assert all(result.games > 0 for result in results)
    assert all(0 <= result.win_rate <= 1 for result in results)
    assert sum(result.wins for result in results) == 5


def test_smoke_batch_returns_winner_counts() -> None:
    winners = run_smoke_batch(game_count=5, player_count=3)

    assert sum(winners.values()) == 5

