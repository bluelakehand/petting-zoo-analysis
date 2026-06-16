from __future__ import annotations

import random
from abc import ABC, abstractmethod

from petting_zoo_analysis.engine.actions import LegalBuy, LegalMove
from petting_zoo_analysis.engine.state import GameState, PlacedCard


class Policy(ABC):
    @abstractmethod
    def choose_move(self, state: GameState, roll: int, legal_moves: tuple[LegalMove, ...], rng: random.Random) -> LegalMove | None:
        raise NotImplementedError

    @abstractmethod
    def choose_buy(self, state: GameState, legal_buys: tuple[LegalBuy, ...], rng: random.Random) -> LegalBuy | None:
        raise NotImplementedError

    def choose_apple_picking_token(self, state: GameState, placed: PlacedCard, token_total: int, rng: random.Random) -> bool:
        _ = state
        _ = placed
        _ = rng
        return token_total < 3
