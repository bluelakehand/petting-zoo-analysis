from __future__ import annotations

import random

from petting_zoo_analysis.engine.actions import TurnAction
from petting_zoo_analysis.engine.state import GameState
from petting_zoo_analysis.policies.base import Policy


class RandomPolicy(Policy):
    def choose_action(self, state: GameState, rng: random.Random) -> TurnAction:
        _ = state
        _ = rng
        return TurnAction(move=None, buy=None)

