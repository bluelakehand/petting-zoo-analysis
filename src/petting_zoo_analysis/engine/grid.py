from __future__ import annotations

from petting_zoo_analysis.engine.state import Position


ORTHOGONAL_DELTAS: tuple[Position, ...] = ((0, 1), (1, 0), (0, -1), (-1, 0))
DIAGONAL_DELTAS: tuple[Position, ...] = ((1, 1), (1, -1), (-1, -1), (-1, 1))
SURROUNDING_DELTAS: tuple[Position, ...] = ORTHOGONAL_DELTAS + DIAGONAL_DELTAS


def adjacent_positions(position: Position) -> tuple[Position, ...]:
    x, y = position
    return tuple((x + dx, y + dy) for dx, dy in ORTHOGONAL_DELTAS)


def diagonal_positions(position: Position) -> tuple[Position, ...]:
    x, y = position
    return tuple((x + dx, y + dy) for dx, dy in DIAGONAL_DELTAS)


def surrounding_positions(position: Position) -> tuple[Position, ...]:
    x, y = position
    return tuple((x + dx, y + dy) for dx, dy in SURROUNDING_DELTAS)

