# Petting Zoo Rules Validation Report

This report describes the rules as the simulator currently understands them. It also calls out known gaps and rule questions for validation before the engine becomes authoritative.

## Recently Validated Corrections

- Entrance cannot be moved back to during a turn. It is only a legal first-roll entry point, even if Gift Shop has expanded its entry range.
- There is no random market row. The game uses full shared stacks of all available buyable cards.
- Buying is optional. A player can refuse to buy on a turn to save money for a later turn.
- Market refill is not a rule because all non-empty stacks are available all the time.
- Cows get +1 from other diagonal Cows when the activating card is Cow, but a Cow's own ability text normally buffs other Paw cards rather than itself.

## Players And Setup

- The simulator defaults to 3 players.
- Each player starts with:
  - 4 coins.
  - 1 Entrance card at grid position `(0, 0)`.
  - Pawn/customer marker at the Entrance.
- There is no random market. All buyable cards are available as shared stacks from the start.
- Entrance cards are starting cards only and are removed from the shuffled deck.

## Deck Composition

- Entrance: 3 copies, one starting card per player.
- Normal cards: 5 copies each, except unique sets.
- Victory/scoring cards: 3 copies each, one available per player.
- Bunny is a unique set:
  - 1 copy each of Bunny 1, Bunny 2, Bunny 3, Bunny 4, and Bunny 5.
- Apple Picking is a unique set:
  - 1 copy each of Apple Picking 1 or 6, 2 or 6, 3 or 6, 4 or 6, and 5 or 6.
- Buying a card removes 1 copy from that card's shared stack.
- A card cannot be bought once its stack is empty.

## Victory Condition

- The game is won by owning each of the 4 victory cards:
  - Gift Shop
  - Dolphin
  - Kangaroo
  - Rooster
- Players may not buy a duplicate of a victory card they already own.
- The simulator currently checks for a winner after the active player's buy step at turn end.
- If no player wins before `max_turns`, the simulator stops by turn cap for experiments.

## Spatial Terms

- Adjacent means the 4 orthogonal spaces sharing sides.
- Diagonal means the 4 corner-touching spaces.
- Surrounding means all 8 spaces: adjacent plus diagonal.
- New cards may only be bought into empty orthogonally adjacent spaces.

## Turn Structure

- Active player starts a turn.
- The player repeatedly rolls one six-sided die.
- On each roll, the player must choose a legal destination if one exists under its policy.
- After moving, the destination card activates immediately.
- If the player has no chosen legal move, the movement sequence ends.
- The player may then buy one legal card from any non-empty shared stack, paying its cost and placing it adjacent to their zoo.
- The player may also decline to buy.
- Bought cards are removed from their stack. There is no refill step.
- The turn ends and play passes to the next player.

## Movement Rules

- On the first roll of a turn:
  - Entrance is a legal entry point if its roll condition matches.
  - Aviary is also a legal entry point on a 6.
- After the first movement of a turn:
  - Standard movement is to orthogonally adjacent cards.
  - Sheep may be entered diagonally.
  - If the pawn is on Llama Ride and the roll is 1 or 2, the pawn may move to any other Llama Ride in that player's zoo.
  - From Pony, movement is restricted to diagonal cards.
  - From Picnic Table, movement is restricted to diagonal cards.
  - Entrance is not a valid destination after the first roll.

## Card Catalog And Abilities

| Card | Roll | Type | Cost | VP | Copies | Ability as understood |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Entrance | 1-4 | Entrance | 0 | 0 | 3 | +2 coins. First-roll entry only. Gift Shop changes entry range to 1-5. |
| Aviary | 6 | Feather | 5 | 0 | 5 | +1 coin. On first roll, can enter through Aviary on 6. |
| Apple Picking 1 or 6 | 1 or 6 | Flower | 3 | 0 | 1 | May place 1 own coin on this card, or gain coins equal to total coins on all own Apple Picking cards. |
| Apple Picking 2 or 6 | 2 or 6 | Flower | 3 | 0 | 1 | Same Apple Picking ability. |
| Apple Picking 3 or 6 | 3 or 6 | Flower | 3 | 0 | 1 | Same Apple Picking ability. |
| Apple Picking 4 or 6 | 4 or 6 | Flower | 3 | 0 | 1 | Same Apple Picking ability. |
| Apple Picking 5 or 6 | 5 or 6 | Flower | 3 | 0 | 1 | Same Apple Picking ability. |
| Bunny 1 | 1 | Paw | 1 | 0 | 1 | +1 coin for every Bunny in your zoo. |
| Bunny 2 | 2 | Paw | 1 | 0 | 1 | Same Bunny ability. |
| Bunny 3 | 3 | Paw | 1 | 0 | 1 | Same Bunny ability. |
| Bunny 4 | 4 | Paw | 1 | 0 | 1 | Same Bunny ability. |
| Bunny 5 | 5 | Paw | 1 | 0 | 1 | Same Bunny ability. |
| Burger Stand | 3-4 | Utensils | 5 | 0 | 5 | Each other player gives +2 coins for each victory card they own, capped by their available coins. |
| Cow | 6 | Paw | 2 | 0 | 5 | +2 coins. Also gives +1 when a Paw card diagonal to Cow activates, including Cow cards diagonal to other Cows. |
| Dolphin | 2-3 | Water | 25 | 1 | 3 | +7 coins from each other player, capped by their available coins. Victory card. |
| Feed Dispenser | 4-5 | House | 4 | 0 | 5 | +1 coin for every Paw or Utensils card surrounding it. |
| Garden | 2-3 | Flower | 10 | 0 | 5 | Gain coins equal to coins already earned this turn, effectively doubling turn earnings so far. |
| Gift Shop | 5-6 | House | 10 | 1 | 3 | +3 coins. Entrance can be entered on 1-5 on the first roll. Victory card. |
| Ice Cream Shop | 5-6 | Utensils | 6 | 0 | 5 | +2 coins for every Cow surrounding it. |
| Kangaroo | 3-4 | Paw | 40 | 1 | 3 | +10 coins. Victory card. |
| Llama Ride | 1-2 | Paw | 5 | 0 | 5 | +2 coins. From Llama Ride on 1-2, may move to any other Llama Ride. |
| Picnic Table | ?-6 | Utensils | 4 | 0 | 5 | +1 coin for each diagonal Flower. `? = 7 - adjacent Utensils`. Movement from Picnic Table is diagonal only. |
| Pony | 1-? | Paw | 5 | 0 | 5 | +3 coins. `? = adjacent Paw count`. Movement from Pony is diagonal only. |
| Rooster | 1-2 | Feather | 15 | 1 | 3 | +5 coins. Victory card. |
| Sheep | 4 | Paw | 1 | 0 | 5 | +2 coins. Can be entered diagonally. |
| Smoothie Shack | 3-4 | Utensils | 6 | 0 | 5 | +2 coins per orthogonal grid step from Entrance, currently Manhattan distance from `(0, 0)`. |
| Snow Cone Stand | 1-2 | Utensils | 2 | 0 | 5 | +1 coin from each other player for every adjacent Utensils card, capped by their available coins. |

## Validated Assumptions

- A player keeps rolling and moving until no legal move is selected or no legal move exists.
- If legal moves exist, a player may still voluntarily stop movement. Current policy interface permits choosing no move.
- A player may buy at most one card after movement ends.
- Buying is optional.
- Buying always places the card orthogonally adjacent to any existing card in that player's zoo.
- Bought cards do not activate immediately.
- There is no market refill step.
- Payments taken from opponents are capped by the coins they actually have.
- Apple Picking tokens are player coins moved onto the card and reduce the player's coin total by 1.
- Apple Picking can bank a coin only if the player has at least 1 coin.
- Cow's diagonal bonus applies when Paw cards diagonal to Cow activate. A Cow can receive +1 from other diagonal Cows, but not from itself.
- Smoothie Shack distance is currently Manhattan distance from Entrance, not shortest traversable path through cards.
- Garden doubles coins earned earlier in the current turn, but does not double later earnings.
- Dynamic roll ranges can become impossible if the computed range is outside 1-6; the simulator simply checks whether the die roll falls in the computed range.
- Unique Apple Picking and Bunny cards are one copy each in the shared supply, not one copy per player.

## Current Implementation Gaps Or Review Items

- Confirm whether `move away from Entrance` on Smoothie Shack means Manhattan grid distance or shortest legal path distance through placed cards.
- Confirm exact timing for Garden if a later card in the same turn earns coins after Garden.
- Confirm whether Apple Picking tokens persist forever and count across all Apple Picking cards owned by that player.
