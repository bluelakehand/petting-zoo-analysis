from __future__ import annotations

from collections.abc import Iterable

from petting_zoo_analysis.rules.cards import VICTORY_CARD_IDS


def owned_victory_cards(card_ids: Iterable[str]) -> frozenset[str]:
    return frozenset(card_id for card_id in card_ids if card_id in VICTORY_CARD_IDS)


def has_winning_victory_set(card_ids: Iterable[str]) -> bool:
    return owned_victory_cards(card_ids) == VICTORY_CARD_IDS

