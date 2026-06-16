from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from typing import TypeAlias

from petting_zoo_analysis.rules.cards import CARD_DEFS
from petting_zoo_analysis.rules.scoring import owned_victory_cards


Position: TypeAlias = tuple[int, int]


@dataclass(frozen=True, slots=True)
class PlacedCard:
    card_id: str
    position: Position
    tokens: int = 0


@dataclass(frozen=True, slots=True)
class PlayerState:
    player_id: int
    coins: int
    pawn: Position = (0, 0)
    zoo: tuple[PlacedCard, ...] = (PlacedCard("entrance", (0, 0)),)

    @property
    def victory_points(self) -> int:
        return sum(CARD_DEFS[card.card_id].victory_points for card in self.zoo)

    @property
    def owned_card_ids(self) -> tuple[str, ...]:
        return tuple(card.card_id for card in self.zoo)

    @property
    def owned_victory_card_ids(self) -> frozenset[str]:
        return owned_victory_cards(self.owned_card_ids)


@dataclass(frozen=True, slots=True)
class Event:
    turn: int
    player_id: int
    kind: str
    message: str
    snapshot: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class GameConfig:
    player_count: int = 3
    starting_coins: int = 4
    market_size: int = 6
    max_turns: int = 200


@dataclass(frozen=True, slots=True)
class GameState:
    players: tuple[PlayerState, ...]
    config: GameConfig = field(default_factory=GameConfig)
    active_player: int = 0
    turn_number: int = 1
    market: tuple[str, ...] = field(default_factory=tuple)
    deck: tuple[str, ...] = field(default_factory=tuple)
    discard: tuple[str, ...] = field(default_factory=tuple)
    events: tuple[Event, ...] = field(default_factory=tuple)
    winner: int | None = None

    @property
    def is_complete(self) -> bool:
        return self.winner is not None or self.turn_number > self.config.max_turns
