from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CardKind(StrEnum):
    PAW = "paw"
    UTENSILS = "utensils"
    HOUSE = "house"
    FLOWER = "flower"
    FEATHER = "feather"
    WATER = "water"
    ENTRANCE = "entrance"


class DeckRole(StrEnum):
    NORMAL = "normal"
    STARTING = "starting"
    SCORING = "scoring"
    UNIQUE_SET = "unique_set"


@dataclass(frozen=True, slots=True)
class RollSpec:
    values: frozenset[int] | None = None
    low: int | None = None
    high: int | None = None

    def contains(self, roll: int, dynamic_low: int | None = None, dynamic_high: int | None = None) -> bool:
        if self.values is not None:
            return roll in self.values
        low = self.low if self.low is not None else dynamic_low
        high = self.high if self.high is not None else dynamic_high
        if low is None or high is None:
            raise ValueError("Dynamic roll range was not resolved.")
        return low <= roll <= high


@dataclass(frozen=True, slots=True)
class CardDef:
    card_id: str
    name: str
    kind: CardKind
    roll: RollSpec
    cost: int
    victory_points: int
    ability_id: str
    copies: int
    deck_role: DeckRole
    ability_text: str


def exact(*values: int) -> RollSpec:
    return RollSpec(values=frozenset(values))


def span(low: int | None, high: int | None) -> RollSpec:
    return RollSpec(low=low, high=high)


CARD_DEFS: dict[str, CardDef] = {
    "entrance": CardDef("entrance", "Entrance", CardKind.ENTRANCE, span(1, 4), 0, 0, "entrance", 3, DeckRole.STARTING, "+2 coins. You can only land on this card on your first roll."),
    "aviary": CardDef("aviary", "Aviary", CardKind.FEATHER, exact(6), 5, 0, "aviary", 5, DeckRole.NORMAL, "+1 coin. On your first roll you can enter your Petting Zoo through Aviary if you roll a 6."),
    "apple_picking_1_6": CardDef("apple_picking_1_6", "Apple Picking", CardKind.FLOWER, exact(1, 6), 3, 0, "apple_picking", 1, DeckRole.UNIQUE_SET, "You may place 1 of your coins on this card or +? coins. The ? is equal to the total number of coins on all your Apple Picking cards."),
    "apple_picking_2_6": CardDef("apple_picking_2_6", "Apple Picking", CardKind.FLOWER, exact(2, 6), 3, 0, "apple_picking", 1, DeckRole.UNIQUE_SET, "You may place 1 of your coins on this card or +? coins. The ? is equal to the total number of coins on all your Apple Picking cards."),
    "apple_picking_3_6": CardDef("apple_picking_3_6", "Apple Picking", CardKind.FLOWER, exact(3, 6), 3, 0, "apple_picking", 1, DeckRole.UNIQUE_SET, "You may place 1 of your coins on this card or +? coins. The ? is equal to the total number of coins on all your Apple Picking cards."),
    "apple_picking_4_6": CardDef("apple_picking_4_6", "Apple Picking", CardKind.FLOWER, exact(4, 6), 3, 0, "apple_picking", 1, DeckRole.UNIQUE_SET, "You may place 1 of your coins on this card or +? coins. The ? is equal to the total number of coins on all your Apple Picking cards."),
    "apple_picking_5_6": CardDef("apple_picking_5_6", "Apple Picking", CardKind.FLOWER, exact(5, 6), 3, 0, "apple_picking", 1, DeckRole.UNIQUE_SET, "You may place 1 of your coins on this card or +? coins. The ? is equal to the total number of coins on all your Apple Picking cards."),
    "bunny_1": CardDef("bunny_1", "Bunny", CardKind.PAW, exact(1), 1, 0, "bunny_count", 1, DeckRole.UNIQUE_SET, "+1 coin for every Bunny card in your Petting Zoo."),
    "bunny_2": CardDef("bunny_2", "Bunny", CardKind.PAW, exact(2), 1, 0, "bunny_count", 1, DeckRole.UNIQUE_SET, "+1 coin for every Bunny card in your Petting Zoo."),
    "bunny_3": CardDef("bunny_3", "Bunny", CardKind.PAW, exact(3), 1, 0, "bunny_count", 1, DeckRole.UNIQUE_SET, "+1 coin for every Bunny card in your Petting Zoo."),
    "bunny_4": CardDef("bunny_4", "Bunny", CardKind.PAW, exact(4), 1, 0, "bunny_count", 1, DeckRole.UNIQUE_SET, "+1 coin for every Bunny card in your Petting Zoo."),
    "bunny_5": CardDef("bunny_5", "Bunny", CardKind.PAW, exact(5), 1, 0, "bunny_count", 1, DeckRole.UNIQUE_SET, "+1 coin for every Bunny card in your Petting Zoo."),
    "burger_stand": CardDef("burger_stand", "Burger Stand", CardKind.UTENSILS, span(3, 4), 5, 0, "tax_vp_cards", 5, DeckRole.NORMAL, "Each player gives you +2 coins for each of their victory point cards."),
    "cow": CardDef("cow", "Cow", CardKind.PAW, exact(6), 2, 0, "cow_diagonal_animals", 5, DeckRole.NORMAL, "+2 coins. All Paw cards diagonal to this card give you +1 coin."),
    "dolphin": CardDef("dolphin", "Dolphin", CardKind.WATER, span(2, 3), 25, 1, "take_7_from_others", 3, DeckRole.SCORING, "+7 coins from all other players."),
    "feed_dispenser": CardDef("feed_dispenser", "Feed Dispenser", CardKind.HOUSE, span(4, 5), 4, 0, "feed_dispenser", 5, DeckRole.NORMAL, "+1 coin for every Paw or Utensils card surrounding this card."),
    "garden": CardDef("garden", "Garden", CardKind.FLOWER, span(2, 3), 10, 0, "double_turn_coins", 5, DeckRole.NORMAL, "Double the coins you have earned this turn."),
    "gift_shop": CardDef("gift_shop", "Gift Shop", CardKind.HOUSE, span(5, 6), 10, 1, "gift_shop", 3, DeckRole.SCORING, "+3 coins. You now get in the Entrance on a 1-5."),
    "ice_cream_shop": CardDef("ice_cream_shop", "Ice Cream Shop", CardKind.UTENSILS, span(5, 6), 6, 0, "ice_cream_shop", 5, DeckRole.NORMAL, "+2 coins for every Cow card surrounding this card."),
    "kangaroo": CardDef("kangaroo", "Kangaroo", CardKind.PAW, span(3, 4), 40, 1, "flat_10", 3, DeckRole.SCORING, "+10 coins."),
    "llama_ride": CardDef("llama_ride", "Llama Ride", CardKind.PAW, span(1, 2), 5, 0, "llama_ride", 5, DeckRole.NORMAL, "+2 coins. When your pawn is on a Llama Ride card and you roll a 1-2 you may move to any other Llama Ride card in your Petting Zoo."),
    "picnic_table": CardDef("picnic_table", "Picnic Table", CardKind.UTENSILS, span(None, 6), 4, 0, "picnic_table", 5, DeckRole.NORMAL, "+1 coin for each Flower diagonal to this card. The ? is equal to 7 minus the amount of Utensils adjacent to this card. You can only move diagonally from Picnic Table."),
    "pony": CardDef("pony", "Pony", CardKind.PAW, span(1, None), 5, 0, "pony", 5, DeckRole.NORMAL, "+3 coins. The ? is equal to the amount of Paw cards adjacent to this card. You can only move diagonally from Pony."),
    "rooster": CardDef("rooster", "Rooster", CardKind.FEATHER, span(1, 2), 15, 1, "flat_5", 3, DeckRole.SCORING, "+5 coins."),
    "sheep": CardDef("sheep", "Sheep", CardKind.PAW, exact(4), 1, 0, "sheep_diagonal", 5, DeckRole.NORMAL, "+2 coins. You can move diagonally to Sheep."),
    "smoothie_shack": CardDef("smoothie_shack", "Smoothie Shack", CardKind.UTENSILS, span(3, 4), 6, 0, "distance_from_entrance", 5, DeckRole.NORMAL, "+2 coins for every move that this card is away from the Entrance."),
    "snow_cone_stand": CardDef("snow_cone_stand", "Snow Cone Stand", CardKind.UTENSILS, span(1, 2), 2, 0, "snow_cone", 5, DeckRole.NORMAL, "+1 coin from all other players for every Utensils card adjacent to this card."),
}


def build_deck() -> tuple[str, ...]:
    return tuple(card_id for card_id, card in CARD_DEFS.items() for _ in range(card.copies))


VICTORY_CARD_IDS: frozenset[str] = frozenset(
    card_id for card_id, card in CARD_DEFS.items() if card.deck_role == DeckRole.SCORING
)
