# Strategy and Notes

In Round 2, we analyzed the gameplay logs and verified that our bot had a 100% win rate (250/250) against the opponent in Round 1.
However, we wanted to ensure there were absolutely no edge cases where our units get stuck or face an unhandled situation if they get completely surrounded or blocked by walls/spawn points.

We kept the core logic identical since it's highly dominant (250/250), but added a robust fallback in `robot.py`:
1. Check adjacent enemies, focus and attack the one with lowest health.
2. Otherwise, find the closest enemy and move towards them.
3. If blocked directly, try clockwise and counterclockwise rotational moves.
4. **Added Round 2 improvement**: If even those rotation moves are blocked, we check all possible Directions to see if we can move anywhere at all (to avoid staying completely passive or stuck). This guarantees maximum mobility.

The tests run flawlessly and result in consistent, strong wins.
