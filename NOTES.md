Round 1 summary:
- Replaced the starter robot with several strategies this round:
  1) Closest-enemy approach with roam and off-map handling.
  2) Safer movement avoiding stepping adjacent to non-target enemies.
  3) Aggressive approach moving toward center and attacking nearest.
- Tested locally against a simple baseline bot (opponent.py).
- Observations:
  - Our bots consistently lost to the baseline in multiple seeds.
  - Safety avoidance reduced reckless moves but didn't improve win rate.
  - Aggressive center approach also didn't out-perform baseline.
- Next ideas:
  - Implement team-aware coordination: avoid clustering, focus-fire targets.
  - Add state.init_turn for persistent per-turn info (e.g., assigned targets).
  - Track enemy patterns and implement kiting or baiting.
  - Add logging via Debug.inspect to analyze unit-level decisions in web UI.

To continue in later rounds, resume from robot.py and use the tests in logs/rounds to analyze simulation traces.
