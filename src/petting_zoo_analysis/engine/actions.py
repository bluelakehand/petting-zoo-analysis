from __future__ import annotations

from dataclasses import dataclass

from petting_zoo_analysis.engine.state import Position


@dataclass(frozen=True, slots=True)
class MoveAction:
    destination: Position


@dataclass(frozen=True, slots=True)
class BuyAction:
    card_id: str
    position: Position


@dataclass(frozen=True, slots=True)
class TurnAction:
    move: MoveAction | None
    buy: BuyAction | None


@dataclass(frozen=True, slots=True)
class LegalMove:
    destination: Position
    card_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class LegalBuy:
    card_id: str
    position: Position

