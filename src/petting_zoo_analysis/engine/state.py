from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from petting_zoo_analysis.rules.cards import CARD_DEFS


Position: TypeAlias = tuple[int, int]


@dataclass(frozen=True, slots=True)
class PlacedCard:
    card_id: str
    position: Position


@dataclass(frozen=True, slots=True)
class PlayerState:
    player_id: int
    coins: int
    pawn: Position = (0, 0)
    zoo: tuple[PlacedCard, ...] = (PlacedCard("entrance", (0, 0)),)

    @property
    def victory_points(self) -> int:
        return sum(CARD_DEFS[card.card_id].victory_points for card in self.zoo)


@dataclass(frozen=True, slots=True)
class GameState:
    players: tuple[PlayerState, ...]
    active_player: int = 0
    turn_number: int = 1
    market: tuple[str, ...] = field(default_factory=tuple)
    deck: tuple[str, ...] = field(default_factory=tuple)
    discard: tuple[str, ...] = field(default_factory=tuple)

