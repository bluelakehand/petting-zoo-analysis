# Baseline Tournament Notes

## 2026-06-16 Shared-Supply Baseline

Command:

```powershell
$env:PYTHONPATH='src'
python -m petting_zoo_analysis.experiments.run_batch --games 300 --players 3 --max-turns 80 --output-dir results\baseline-300
```

This is an early sanity-check tournament after replacing the random market model with full shared supply stacks. Treat these numbers as directional only; policies are still simple heuristics, not tuned strategies.

| Policy | Wins | Victory Wins | Fallback Wins | Games | Win Rate | 95% CI | Mean Place | Mean Turn | Mean VP Cards | Mean Coins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| high_cost_saver | 78 | 78 | 0 | 129 | 0.605 | 0.084 | 1.52 | 44.8 | 3.33 | 8.7 |
| greedy_victory | 63 | 63 | 0 | 128 | 0.492 | 0.087 | 1.71 | 47.8 | 3.19 | 12.3 |
| interaction | 52 | 52 | 0 | 128 | 0.406 | 0.085 | 1.92 | 47.3 | 2.79 | 10.2 |
| roll_coverage | 48 | 48 | 0 | 129 | 0.372 | 0.083 | 1.77 | 44.6 | 3.08 | 11.9 |
| greedy_income | 42 | 42 | 0 | 129 | 0.326 | 0.081 | 2.09 | 45.9 | 2.63 | 11.4 |
| random | 10 | 10 | 0 | 128 | 0.078 | 0.046 | 2.45 | 48.6 | 1.95 | 6.8 |
| cheap_expansion | 7 | 7 | 0 | 129 | 0.054 | 0.039 | 2.53 | 44.1 | 1.99 | 6.2 |

## Early Read

- High-cost saving is the current leader, mostly because it prioritizes the expensive victory-card path instead of spending early money on cheap engine cards.
- Greedy victory is also strong, but it finishes slightly later and with fewer average victory cards than high-cost saver in this batch.
- Roll coverage places well despite fewer wins than interaction, suggesting it may be a strong support idea once mixed with victory-card prioritization.
- Cheap expansion performs poorly in this simple form. Under shared stacks, buying lots of cheap cards does not appear to beat focused progress toward the four required victory cards.
- There were no fallback wins in this run; all winners completed the four-card victory set before the 80-turn cap.

## Next Experiments

- Add hybrid policies that combine high-cost saving with roll coverage and selective income engines.
- Track purchased card order and first victory-card timing.
- Run paired head-to-head tournaments between the top policy families.
- Add strategy parameters for save thresholds, cheap-card limits, and victory-card purchase priority.
