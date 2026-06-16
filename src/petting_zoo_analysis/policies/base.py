from __future__ import annotations

import random
from abc import ABC, abstractmethod

from petting_zoo_analysis.engine.actions import TurnAction
from petting_zoo_analysis.engine.state import GameState


class Policy(ABC):
    @abstractmethod
    def choose_action(self, state: GameState, rng: random.Random) -> TurnAction:
        raise NotImplementedError

