# RobotRumble Strategy - Optimized Black Magic

We have built upon and refined the translated Python version (`robot.py`) of the `black-magic.js` heuristic search algorithm.

### Current Features & Performance:
1. **Robust Heuristics**: Preserves the extremely effective prioritized evaluation from Black Magic: Unit Differential, Hill Control (where relevant), Surround Advantage, Health, and Distance positioning.
2. **Validated & Stable**: Successfully achieves dominant wins over the `black-magic.js` baseline under multiple random seeds.
3. **No Overhead**: Keeps actions clean, efficient, and well within the allowed execution limit.
