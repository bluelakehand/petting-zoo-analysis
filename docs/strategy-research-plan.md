# Petting Zoo Strategy Research Plan

## Goal

Determine which Petting Zoo strategies win most often by building a
rules-accurate simulator, validating it against the rule PDF, then running
large batches of policy-vs-policy games.

## Initial Observations From `PZRULES.pdf`

- Each player appears to start with an Entrance card, one pawn, a die, and
  starting coins.
- Cards have a roll range at the top, a kind/type icon, an ability text box,
  victory points, and a coin cost.
- A player's zoo is a grid of purchased cards. Adjacency and pawn movement are
  major mechanics.
- Many cards compound based on neighboring cards, card type counts, or current
  turn earnings.
- Some effects transfer coins between players, which means multiplayer opponent
  modeling matters.

## Rule Questions To Verify

- Exact starting coins and player-count setup.
- Market layout, refill order, and deck composition/counts.
- Turn sequence: roll, movement choice, card activation timing, buying timing,
  and whether purchases happen before/after movement.
- End condition and final scoring.
- Tie breakers.
- Whether players may voluntarily skip movement, activation, or purchase.
- Exact interpretation of `?`, `? - 6`, `1 - ?`, diagonal movement, and
  same-card movement effects.

## Architecture

1. **Rules Data Layer**
   - Store every card as structured data: id, name, type, roll expression,
     cost, victory points, ability id, and ability parameters.
   - Keep the raw transcription in a reviewable data file before embedding
     effects in code.

2. **Deterministic Engine**
   - Use immutable-ish dataclasses for game state snapshots.
   - All randomness flows through an injected RNG seed.
   - Legal action generation is separate from action application.
   - Each transition emits an event log for debugging and golden tests.
   - Game logs can be replayed in a visualizer so rules behavior is reviewable
     by board state, pawn movement, market changes, and coin/scoring changes.

3. **Policy Layer**
   - Start with random, greedy coins, greedy victory points, engine-builder,
     adjacency-builder, and denial/interference policies.
   - Add rollout-based policies such as Monte Carlo Tree Search after the
     rules engine is validated.

4. **Experiment Layer**
   - Run seeded tournaments with fixed opponent pools.
   - Track win rate, mean placement, final VP, coins generated, card mix,
     movement efficiency, and action/value correlations.
   - Use confidence intervals and paired seeds to avoid over-reading noise.

5. **ML Layer**
   - Begin with supervised imitation of strong heuristic/MCTS decisions.
   - Train value models to estimate win probability from state features.
   - Use self-play or population-based training only after fast simulation and
     rule tests are stable.

## Simulation Milestones

1. Transcribe cards and rules from the PDF.
2. Build engine with random-play smoke tests.
3. Add golden tests from the PDF examples.
4. Build a visualizer for replaying deterministic games and reviewing each
   turn.
5. Run 10,000 random/heuristic games to identify obvious dominant signals.
6. Add parameterized strategies and grid search.
7. Add MCTS rollouts for tactical move/buy decisions.
8. Train value/policy models from the resulting game logs.
9. Produce a ranked strategy report with sensitivity by player count.

## Strategy Families To Test

- Early cheap-card expansion versus saving for high-cost cards.
- Coin engine first versus victory-point rush.
- High-roll cards versus broad roll coverage.
- Adjacency cluster strategies around food/animal/building types.
- Pawn mobility strategies using diagonal and same-type movement cards.
- Player-interaction strategies that steal or tax opponents.
- Market denial: buying cards mostly to prevent opponents from using them.

## Success Criteria

- Simulations are reproducible by seed.
- Rule assumptions are explicit and tested.
- Strategy claims include sample size and confidence intervals.
- Best strategy is robust against at least random, greedy, and search-based
  opponents.
