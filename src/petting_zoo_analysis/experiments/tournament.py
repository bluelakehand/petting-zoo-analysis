from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Callable

from petting_zoo_analysis.engine.simulate import play_game
from petting_zoo_analysis.engine.state import GameConfig
from petting_zoo_analysis.policies.base import Policy
from petting_zoo_analysis.policies.heuristics import (
    CheapExpansionPolicy,
    GreedyIncomePolicy,
    GreedyVictoryPolicy,
    HighCostSaverPolicy,
    InteractionPolicy,
    RollCoveragePolicy,
)
from petting_zoo_analysis.policies.random_policy import RandomPolicy


PolicyFactory = Callable[[], Policy]


POLICY_FACTORIES: dict[str, PolicyFactory] = {
    "random": RandomPolicy,
    "greedy_victory": GreedyVictoryPolicy,
    "greedy_income": GreedyIncomePolicy,
    "cheap_expansion": CheapExpansionPolicy,
    "high_cost_saver": HighCostSaverPolicy,
    "roll_coverage": RollCoveragePolicy,
    "interaction": InteractionPolicy,
}


@dataclass(frozen=True, slots=True)
class TournamentResult:
    policy_name: str
    games: int
    wins: int
    win_rate: float
    ci95: float
    mean_vp_cards: float
    mean_coins: float
    mean_cards: float


def run_policy_tournament(game_count: int = 100, player_count: int = 3, max_turns: int = 80) -> list[TournamentResult]:
    policy_names = tuple(POLICY_FACTORIES)
    records: dict[str, dict[str, float]] = defaultdict(lambda: {"games": 0, "wins": 0, "vp_cards": 0, "coins": 0, "cards": 0})
    config = GameConfig(player_count=player_count, max_turns=max_turns)

    for seed in range(game_count):
        rotated = tuple(policy_names[(seed + offset) % len(policy_names)] for offset in range(player_count))
        policies = tuple(POLICY_FACTORIES[name]() for name in rotated)
        state = play_game(policies, seed=seed, config=config)
        winner_id = state.winner
        if winner_id is None:
            winner_id = max(
                state.players,
                key=lambda player: (len(player.owned_victory_card_ids), player.coins, len(player.zoo)),
            ).player_id
        for seat, player in enumerate(state.players):
            name = rotated[seat]
            records[name]["games"] += 1
            records[name]["wins"] += 1 if seat == winner_id else 0
            records[name]["vp_cards"] += len(player.owned_victory_card_ids)
            records[name]["coins"] += player.coins
            records[name]["cards"] += len(player.zoo)

    return [_summarize(name, values) for name, values in sorted(records.items())]


def winner_counts(results: list[TournamentResult]) -> Counter[str]:
    return Counter({result.policy_name: result.wins for result in results})


def _summarize(policy_name: str, values: dict[str, float]) -> TournamentResult:
    games = int(values["games"])
    wins = int(values["wins"])
    win_rate = wins / games if games else 0.0
    ci95 = 1.96 * sqrt((win_rate * (1 - win_rate)) / games) if games else 0.0
    return TournamentResult(
        policy_name=policy_name,
        games=games,
        wins=wins,
        win_rate=win_rate,
        ci95=ci95,
        mean_vp_cards=values["vp_cards"] / games if games else 0.0,
        mean_coins=values["coins"] / games if games else 0.0,
        mean_cards=values["cards"] / games if games else 0.0,
    )

