from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from petting_zoo_analysis.engine.state import GameState
from petting_zoo_analysis.rules.cards import CARD_DEFS


REPLAY_SCHEMA_VERSION = 1


def replay_payload(state: GameState, seed: int, policies: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "seed": seed,
        "policies": list(policies),
        "config": asdict(state.config),
        "winner": state.winner,
        "turn_number": state.turn_number,
        "card_catalog": {
            card_id: {
                "name": card.name,
                "kind": card.kind.value,
                "cost": card.cost,
                "victory_points": card.victory_points,
                "ability_text": card.ability_text,
                "image": f"assets/cards/{card_id}.jpg",
            }
            for card_id, card in CARD_DEFS.items()
        },
        "players": [
            {
                "player_id": player.player_id,
                "coins": player.coins,
                "victory_points": player.victory_points,
                "pawn": list(player.pawn),
                "zoo": [
                    {
                        "card_id": placed.card_id,
                        "position": list(placed.position),
                        "tokens": placed.tokens,
                    }
                    for placed in player.zoo
                ],
            }
            for player in state.players
        ],
        "market": supply_snapshot(state),
        "supply": supply_snapshot(state),
        "deck_count": len(state.deck),
        "discard_count": len(state.discard),
        "events": [asdict(event) for event in state.events],
    }


def write_replay(state: GameState, path: str | Path, seed: int, policies: tuple[str, ...] = ()) -> None:
    payload = replay_payload(state, seed=seed, policies=policies)
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def supply_snapshot(state: GameState) -> list[dict[str, Any]]:
    return [
        {"card_id": card_id, "count": state.supply.count(card_id)}
        for card_id in CARD_DEFS
        if card_id != "entrance" and state.supply.count(card_id) > 0
    ]
