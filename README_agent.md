# Strategy and Notes

In Round 1, our teammate implemented a simple but robust state-seeking bot (`robot.py`).
This bot logic does the following:
1. Attacks adjacent enemies first (focusing on the one with the lowest health).
2. Otherwise, moves towards the closest enemy using direction/CW/CCW pathing.

We analyzed the past rounds:
- **Round 0**: 250 Ties, 0 Wins, 0 Losses (The opponent did nothing/stayed passive, and our original bot likely stayed passive or couldn't reach, resulting in all ties).
- **Round 1**: 250 Wins (Red), 0 Losses (Blue). Since we won 100% of the matches with the new logic in Round 1, and the opponent has 0 wins, our bot is extremely dominant.

We kept the bot exactly the same since it's already perfectly defeating the opponent with 100% win rate (250/250).

If you want to optimize further or if the opponent changes, you can use `./rumblebot run term robot.py robot.py` to test.
