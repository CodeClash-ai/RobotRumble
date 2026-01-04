# Robot Rumble Agent Notes

## Current Status (Round 1)
- **Previous Performance**: Won 18-0 with 2 ties against anton_anton3000
- **Current Bot**: Improved chaser strategy

## Bot Strategy
The current bot uses a "chaser" strategy:
1. Finds the closest enemy to each unit
2. Moves toward that enemy
3. Attacks when adjacent (distance = 1)

This is a significant improvement over the previous "move west blindly" strategy.

## Testing Results
Tested new bot vs old bot (5 games):
- New bot won all 5 games decisively
- Average final health: ~120 vs ~6
- Average final units: ~25 vs ~2

## Files
- `robot.py` - Current bot implementation (chaser strategy)
- `old_robot.py` - Previous bot (move west strategy) - kept for reference
- `analyze_logs.py` - Script to analyze game logs (see below)

## Analysis Tools

### analyze_logs.py
Run with: `python /workspace/analyze_logs.py /logs/rounds/X`

This script analyzes game logs to show:
- Win/loss/tie statistics
- Final health and unit counts
- Performance trends

## Potential Improvements for Future Rounds
1. **Coordinated targeting**: Use init_turn() to have all units focus on the same enemy
2. **Health-based decisions**: Flee when low health, be aggressive when healthy
3. **Formation tactics**: Keep units grouped for mutual support
4. **Terrain awareness**: Use terrain strategically if present
5. **Advanced heuristics**: Consider enemy health, distance, and friendly unit proximity

## Game Mechanics (Quick Reference)
- Map size: 19x19 grid
- Units spawn at corners
- Each unit has health (starts at 5)
- Actions: Move, Attack, or Pass (None)
- Attack damage: 2 per hit
- Game ends at turn 100 or when one team is eliminated
- Winner determined by: units remaining, then total health

## Useful Commands
Test bot locally:
  ./rumblebot run term /workspace/robot.py /workspace/builtin-bots/chaser.js

Run multiple tests:
  for i in {1..10}; do ./rumblebot run term /workspace/robot.py opponent.py --results-only; done

Analyze logs:
  python /workspace/analyze_logs.py /logs/rounds/0
