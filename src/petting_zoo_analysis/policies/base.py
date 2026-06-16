from __future__ import annotations

import random
from abc import ABC, abstractmethod

from petting_zoo_analysis.engine.actions import LegalBuy, LegalMove
from petting_zoo_analysis.engine.state import GameState


class Policy(ABC):
    @abstractmethod
    def choose_move(self, state: GameState, roll: int, legal_moves: tuple[LegalMove, ...], rng: random.Random) -> LegalMove | None:
        raise NotImplementedError

    @abstractmethod
    def choose_buy(self, state: GameState, legal_buys: tuple[LegalBuy, ...], rng: random.Random) -> LegalBuy | None:
        raise NotImplementedError
