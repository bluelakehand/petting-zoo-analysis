from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Callable

from petting_zoo_analysis.engine.simulate import play_game
from petting_zoo_analysis.engine.state import GameConfig, GameState
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
    victory_wins: int
    fallback_wins: int
    win_rate: float
    ci95: float
    mean_place: float
    mean_turns: float
    mean_vp_cards: float
    mean_vp_total: float
    mean_coins: float
    mean_cards: float


@dataclass(frozen=True, slots=True)
class TournamentGame:
    game_id: int
    seed: int
    policies: tuple[str, ...]
    state: GameState
    winner_id: int
    winner_policy: str
    ended_by_victory: bool
    placements: dict[int, int]


def run_policy_tournament(game_count: int = 100, player_count: int = 3, max_turns: int = 80) -> list[TournamentResult]:
    return summarize_tournament_games(run_policy_tournament_games(game_count=game_count, player_count=player_count, max_turns=max_turns))


def run_policy_tournament_games(game_count: int = 100, player_count: int = 3, max_turns: int = 80) -> list[TournamentGame]:
    policy_names = tuple(POLICY_FACTORIES)
    config = GameConfig(player_count=player_count, max_turns=max_turns)
    games: list[TournamentGame] = []

    for seed in range(game_count):
        rotated = tuple(policy_names[(seed + offset) % len(policy_names)] for offset in range(player_count))
        policies = tuple(POLICY_FACTORIES[name]() for name in rotated)
        state = play_game(policies, seed=seed, config=config)
        winner_id = state.winner
        ended_by_victory = winner_id is not None
        if winner_id is None:
            winner_id = max(
                state.players,
                key=lambda player: (len(player.owned_victory_card_ids), player.coins, len(player.zoo)),
            ).player_id
        places = _placements(state)
        games.append(
            TournamentGame(
                game_id=seed,
                seed=seed,
                policies=rotated,
                state=state,
                winner_id=winner_id,
                winner_policy=rotated[winner_id],
                ended_by_victory=ended_by_victory,
                placements=places,
            )
        )

    return games


def summarize_tournament_games(games: list[TournamentGame]) -> list[TournamentResult]:
    records: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "games": 0,
            "wins": 0,
            "victory_wins": 0,
            "fallback_wins": 0,
            "place": 0,
            "turns": 0,
            "vp_cards": 0,
            "vp_total": 0,
            "coins": 0,
            "cards": 0,
        }
    )

    for game in games:
        for seat, player in enumerate(game.state.players):
            name = game.policies[seat]
            records[name]["games"] += 1
            is_winner = seat == game.winner_id
            records[name]["wins"] += 1 if is_winner else 0
            records[name]["victory_wins"] += 1 if is_winner and game.ended_by_victory else 0
            records[name]["fallback_wins"] += 1 if is_winner and not game.ended_by_victory else 0
            records[name]["place"] += game.placements[seat]
            records[name]["turns"] += game.state.turn_number
            records[name]["vp_cards"] += len(player.owned_victory_card_ids)
            records[name]["vp_total"] += player.victory_points
            records[name]["coins"] += player.coins
            records[name]["cards"] += len(player.zoo)

    return [_summarize(name, values) for name, values in sorted(records.items())]


def winner_counts(results: list[TournamentResult]) -> Counter[str]:
    return Counter({result.policy_name: result.wins for result in results})


def _placements(state) -> dict[int, int]:
    ranked = sorted(
        state.players,
        key=lambda player: (
            len(player.owned_victory_card_ids),
            player.victory_points,
            player.coins,
            len(player.zoo),
        ),
        reverse=True,
    )
    return {player.player_id: place for place, player in enumerate(ranked, start=1)}


def _summarize(policy_name: str, values: dict[str, float]) -> TournamentResult:
    games = int(values["games"])
    wins = int(values["wins"])
    win_rate = wins / games if games else 0.0
    ci95 = 1.96 * sqrt((win_rate * (1 - win_rate)) / games) if games else 0.0
    return TournamentResult(
        policy_name=policy_name,
        games=games,
        wins=wins,
        victory_wins=int(values["victory_wins"]),
        fallback_wins=int(values["fallback_wins"]),
        win_rate=win_rate,
        ci95=ci95,
        mean_place=values["place"] / games if games else 0.0,
        mean_turns=values["turns"] / games if games else 0.0,
        mean_vp_cards=values["vp_cards"] / games if games else 0.0,
        mean_vp_total=values["vp_total"] / games if games else 0.0,
        mean_coins=values["coins"] / games if games else 0.0,
        mean_cards=values["cards"] / games if games else 0.0,
    )
