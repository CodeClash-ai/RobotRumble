# RobotRumble Strategy - Black Magic Implementation

We migrated and implemented the highly optimized `black-magic.js` heuristic search algorithm into Python (`robot.py`).
This algorithm:
1. Simulates state-transitions (one-ply lookahead) for all possible joint moves and attacks.
2. Evaluates the resulting state using four criteria (unit differential, local surround advantage, health, and distance-based positioning).
3. Highly outperforms standard basic bots (e.g., `heuristic-bot.js`, `simple-bot.js`, and `needle-bot.js`).

Feel free to continue tweaking the scoring parameters in `robot.py` to gain further tactical advantage or customize the simulation model for deeper plies!
