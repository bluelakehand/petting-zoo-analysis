from collections import Counter

from petting_zoo_analysis.engine.grid import adjacent_positions, diagonal_positions, surrounding_positions
from petting_zoo_analysis.rules.cards import CARD_DEFS, VICTORY_CARD_IDS, DeckRole, build_deck
from petting_zoo_analysis.rules.scoring import has_winning_victory_set, owned_victory_cards


def test_unique_bunny_and_apple_picking_rolls() -> None:
    bunny_rolls = {card.roll.values for card in CARD_DEFS.values() if card.name == "Bunny"}
    apple_rolls = {card.roll.values for card in CARD_DEFS.values() if card.name == "Apple Picking"}

    assert bunny_rolls == {frozenset({value}) for value in range(1, 6)}
    assert apple_rolls == {frozenset({value, 6}) for value in range(1, 6)}


def test_deck_copy_counts() -> None:
    counts = Counter(build_deck())

    assert sum(counts.values()) == 85
    assert counts["entrance"] == 3
    assert counts["gift_shop"] == 3
    assert counts["rooster"] == 3
    assert counts["dolphin"] == 3
    assert counts["kangaroo"] == 3
    assert counts["llama_ride"] == 5
    assert counts["bunny_1"] == 1
    assert counts["bunny_5"] == 1
    assert counts["apple_picking_1_6"] == 1
    assert counts["apple_picking_5_6"] == 1


def test_deck_roles_match_copy_rules() -> None:
    for card_id, card in CARD_DEFS.items():
        if card.deck_role == DeckRole.STARTING:
            assert card.copies == 3, card_id
        elif card.deck_role == DeckRole.SCORING:
            assert card.victory_points > 0, card_id
            assert card.copies == 3, card_id
        elif card.deck_role == DeckRole.UNIQUE_SET:
            assert card.copies == 1, card_id
        else:
            assert card.deck_role == DeckRole.NORMAL
            assert card.victory_points == 0, card_id
            assert card.copies == 5, card_id


def test_victory_condition_requires_all_four_scoring_cards() -> None:
    assert VICTORY_CARD_IDS == frozenset({"gift_shop", "rooster", "dolphin", "kangaroo"})
    assert owned_victory_cards(["gift_shop", "rooster", "dolphin", "kangaroo", "sheep"]) == VICTORY_CARD_IDS
    assert has_winning_victory_set(["gift_shop", "rooster", "dolphin", "kangaroo"])
    assert not has_winning_victory_set(["gift_shop", "rooster", "dolphin"])
    assert not has_winning_victory_set(["gift_shop", "rooster", "dolphin", "dolphin"])


def test_catalog_has_expected_unique_card_entries() -> None:
    assert len(CARD_DEFS) == 27
    assert {card_id for card_id in CARD_DEFS if card_id.startswith("bunny_")} == {
        "bunny_1",
        "bunny_2",
        "bunny_3",
        "bunny_4",
        "bunny_5",
    }
    assert {card_id for card_id in CARD_DEFS if card_id.startswith("apple_picking_")} == {
        "apple_picking_1_6",
        "apple_picking_2_6",
        "apple_picking_3_6",
        "apple_picking_4_6",
        "apple_picking_5_6",
    }


def test_representative_card_text_is_locked() -> None:
    assert CARD_DEFS["feed_dispenser"].ability_text == (
        "+1 coin for every Paw or Utensils card surrounding this card."
    )
    assert CARD_DEFS["snow_cone_stand"].ability_text == (
        "+1 coin from all other players for every Utensils card adjacent to this card."
    )
    assert CARD_DEFS["picnic_table"].ability_text.endswith(
        "You can only move diagonally from Picnic Table."
    )


def test_spatial_terms_have_distinct_neighborhoods() -> None:
    position = (0, 0)

    assert set(adjacent_positions(position)) == {(0, 1), (1, 0), (0, -1), (-1, 0)}
    assert set(diagonal_positions(position)) == {(1, 1), (1, -1), (-1, -1), (-1, 1)}
    assert set(surrounding_positions(position)) == set(adjacent_positions(position)) | set(diagonal_positions(position))
