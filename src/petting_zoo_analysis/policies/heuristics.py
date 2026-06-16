from __future__ import annotations

import random
from abc import ABC, abstractmethod

from petting_zoo_analysis.engine.actions import LegalBuy, LegalMove
from petting_zoo_analysis.engine.state import GameState, Position
from petting_zoo_analysis.policies.base import Policy
from petting_zoo_analysis.rules.cards import CARD_DEFS, VICTORY_CARD_IDS


class HeuristicPolicy(Policy, ABC):
    policy_name = "heuristic"

    def choose_move(self, state: GameState, roll: int, legal_moves: tuple[LegalMove, ...], rng: random.Random) -> LegalMove | None:
        _ = roll
        _ = rng
        if not legal_moves:
            return None
        return max(legal_moves, key=lambda move: (self.move_score(state, move), -abs(move.destination[0]) - abs(move.destination[1]), move.card_id))

    def choose_buy(self, state: GameState, legal_buys: tuple[LegalBuy, ...], rng: random.Random) -> LegalBuy | None:
        _ = rng
        if not legal_buys:
            return None
        best = max(legal_buys, key=lambda buy: (self.buy_score(state, buy), -CARD_DEFS[buy.card_id].cost, -_distance_from_origin(buy.position), buy.card_id))
        return best if self.buy_score(state, best) > 0 else None

    def move_score(self, state: GameState, move: LegalMove) -> float:
        card = CARD_DEFS[move.card_id]
        return card.victory_points * 50 + _ability_income_hint(move.card_id)

    @abstractmethod
    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        raise NotImplementedError


class GreedyVictoryPolicy(HeuristicPolicy):
    policy_name = "greedy_victory"

    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        card = CARD_DEFS[buy.card_id]
        needed_vp = buy.card_id in VICTORY_CARD_IDS and buy.card_id not in state.players[state.active_player].owned_victory_card_ids
        return (1000 if needed_vp else 0) + card.victory_points * 100 + _ability_income_hint(buy.card_id) - card.cost * 0.1


class GreedyIncomePolicy(HeuristicPolicy):
    policy_name = "greedy_income"

    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        card = CARD_DEFS[buy.card_id]
        return _ability_income_hint(buy.card_id) * 10 + card.victory_points * 25 - card.cost * 0.25


class CheapExpansionPolicy(HeuristicPolicy):
    policy_name = "cheap_expansion"

    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        card = CARD_DEFS[buy.card_id]
        return 20 - card.cost + card.victory_points * 20 + _roll_coverage_score(buy.card_id)


class HighCostSaverPolicy(HeuristicPolicy):
    policy_name = "high_cost_saver"

    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        card = CARD_DEFS[buy.card_id]
        player = state.players[state.active_player]
        if card.victory_points:
            return 500 + card.cost
        if player.coins < 15 and card.cost > 5:
            return 0
        return card.cost + _ability_income_hint(buy.card_id)


class RollCoveragePolicy(HeuristicPolicy):
    policy_name = "roll_coverage"

    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        player = state.players[state.active_player]
        existing = {_roll_signature(card_id) for card_id in player.owned_card_ids}
        novelty = 25 if _roll_signature(buy.card_id) not in existing else 0
        return novelty + _roll_coverage_score(buy.card_id) + CARD_DEFS[buy.card_id].victory_points * 100 - CARD_DEFS[buy.card_id].cost * 0.2


class InteractionPolicy(HeuristicPolicy):
    policy_name = "interaction"

    def buy_score(self, state: GameState, buy: LegalBuy) -> float:
        interaction_bonus = 100 if CARD_DEFS[buy.card_id].ability_id in {"take_7_from_others", "tax_vp_cards", "snow_cone"} else 0
        return interaction_bonus + CARD_DEFS[buy.card_id].victory_points * 100 + _ability_income_hint(buy.card_id)


def _ability_income_hint(card_id: str) -> float:
    hints = {
        "entrance": 2,
        "aviary": 1,
        "gift_shop": 3,
        "rooster": 5,
        "dolphin": 14,
        "kangaroo": 10,
        "llama_ride": 2,
        "sheep": 2,
        "burger_stand": 6,
        "garden": 8,
        "smoothie_shack": 8,
        "feed_dispenser": 5,
        "ice_cream_shop": 4,
        "snow_cone_stand": 5,
        "pony": 3,
        "picnic_table": 3,
        "cow": 2,
    }
    if CARD_DEFS[card_id].name == "Bunny":
        return 3
    if CARD_DEFS[card_id].name == "Apple Picking":
        return 3
    return hints.get(card_id, 1)


def _roll_signature(card_id: str) -> tuple[int, ...] | tuple[str, str]:
    roll = CARD_DEFS[card_id].roll
    if roll.values is not None:
        return tuple(sorted(roll.values))
    return (str(roll.low), str(roll.high))


def _roll_coverage_score(card_id: str) -> float:
    roll = CARD_DEFS[card_id].roll
    if roll.values is not None:
        return len(roll.values) * 5
    if roll.low is not None and roll.high is not None:
        return (roll.high - roll.low + 1) * 5
    return 8


def _distance_from_origin(position: Position) -> int:
    return abs(position[0]) + abs(position[1])

