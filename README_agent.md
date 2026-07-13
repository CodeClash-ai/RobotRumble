# Agent notes

## Round 1 (current matchup: navster8__maginot-line)
- Reviewed official `/logs/rounds/0/`: opponent `navster8__maginot-line` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250, avg final health/units: opponent Blue 3.1 health and 1.0 units vs our Red 143.8 health and 32.9 units; minimum our final health was 82.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score with a large safety margin; changing tactics would add regression risk with no possible upside in this matchup.
- Recommendation for next teammate: if still facing `navster8__maginot-line`, preserve `robot.py` and just re-check new logs.

## Current match-up status
- Current official logs in `/logs/rounds/0/` show opponent `aaoutkine__dark-knight`.
- We (`gpt-5-5`) were **Blue** and swept the round: `250/250` wins.
- `python3 tools/analyze_rounds.py` summary for round 0:
  - visual winners: Blue 250/250
  - average final health: us 126.1 vs opponent 4.1
  - average final units: us 27.1 vs opponent 1.2
- Recommendation while still facing `aaoutkine__dark-knight`: keep the current `robot.py`. It is a proven full sweep; risky tuning is unlikely to improve the official score and could introduce regressions.

## Current `robot.py` summary
- Fast coordinated one-ply tactical planner adapted from the strong public `black-magic.js` bot.
- `init_turn` builds tuple-coordinate maps of friendly/enemy units.
- Enemy model: adjacent enemies attack our lowest-health adjacent friend.
- For each friendly unit, tries pass/attack/legal moves and greedily keeps changes that improve a lexicographic score:
  1. unit advantage
  2. surround/contact pattern
  3. square-root health advantage
  4. pressure/distance field
  5. small center term
- `robot` returns the precomputed per-unit action.
- Optimized vs original JS `black-magic`: cached direction deltas/legal coords, tuple math, avoids repeated `Coords` allocation.
- The small center term encourages units to leave spawn/edges and meet enemies instead of camping.

## Tools
- `tools/analyze_rounds.py` summarizes `/logs/rounds/*/results.json` plus final health/unit stats parsed from `sim_*.txt`.
  Run from `/workspace` with:
  ```bash
  python3 tools/analyze_rounds.py
  ```
  Note: the CLI final-state line prints values as `Health <blue> <red> Units <blue> <red>`.
- `tools/local_eval.py` runs quick local multi-seed regression matches and parses final stats. Examples:
  ```bash
  python3 tools/local_eval.py --seeds 1-5 --opponent builtin-bots/black-magic.js --both-sides
  ./rumblebot run term --results-only --seed 1 robot.py builtin-bots/black-magic.js
  ./rumblebot run term --results-only --seed 1 builtin-bots/black-magic.js robot.py
  ```
  A 20-seed both-sides run can exceed the command timeout; use small batches.

## Round 1 action
- Reviewed official round 0 logs. Because the current bot swept `aaoutkine__dark-knight` 250/250 with large margins, I left `robot.py` unchanged.
- Updated this README only, replacing stale notes from a previous matchup.


## Round 2 action
- Re-ran `python3 tools/analyze_rounds.py` after round 1 logs were available. Round 1 was another perfect sweep over `aaoutkine__dark-knight`: 250/250 wins as Blue, avg final health 127.4 vs 3.7 and avg units 27.4 vs 1.1.
- I intentionally left `robot.py` unchanged. We are already achieving the maximum official score against the current opponent; tuning would add regression risk with no possible score improvement in this matchup.

## Potential future work
- If still facing `aaoutkine__dark-knight`, preserve the proven winner.
- If a stronger mirror/black-magic-like opponent appears, test both colors over multiple seeds and tune score weights/order, especially the center term and tie-breaking.

## Round 1 (current matchup: mountain__neuralbot1-1h)
- Official `/logs/rounds/0/` shows a perfect sweep: opponent `mountain__neuralbot1-1h` was Blue, our `gpt-5-5` was Red, and we won **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250, avg final health 122.0 vs 4.5, avg final units 28.7 vs 1.2. Minimum our final health was still 85, so the matchup is very safe.
- I left `robot.py` unchanged. The bot is already achieving the maximum official score against this opponent; changing tactics now has only downside/regression risk.
- Quick sanity check vs `builtin-bots/black-magic.js` over seeds 1-3 is mixed, but this is not the official opponent. Do not tune for black-magic unless the official opponent changes.

## Round 2 (current matchup: mountain__neuralbot1-1h)
- Reviewed `/logs/rounds/1/`: opponent `mountain__neuralbot1-1h` was Blue, our `gpt-5-5` was Red, and we again won **250/250**.
- `python3 tools/analyze_rounds.py` summary for round 1: visual winners Red 250/250, avg final health 121.6 vs 4.3, avg final units 28.6 vs 1.2; minimum our final health was 90.
- Left `robot.py` unchanged. Current strategy has swept both official rounds in this matchup with large margins, so changes would only risk regression.

## Round 1 (current matchup: sivecano__clouded-mind)
- Reviewed official `/logs/rounds/0/`: opponent `sivecano__clouded-mind` was Red, our `gpt-5-5` was Blue, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health 122.7 vs 6.2 and avg units 25.3 vs 1.7; minimum our final health was 76.
- Left `robot.py` unchanged. Current black-magic-style coordinated planner is already achieving the maximum score in this matchup, so code changes would add regression risk without possible official-score upside.
- Sanity note: quick local seed 1 versus builtin `black-magic.js` remains color-dependent/mixed; do not tune for that unless the official opponent changes.

## Round 2 (current matchup: sivecano__clouded-mind)
- Re-reviewed official logs after round 1: we swept again **250/250** while playing Red (`/logs/rounds/1/`). Combined current matchup record is 500/500 across both colors.
- `python3 tools/analyze_rounds.py` shows round 1 avg final health/units: opponent Blue 6.8 health, 1.8 units vs our Red 121.1 health, 25.0 units; minimum our final health was 78.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing the official score against `sivecano__clouded-mind`; tactical tuning would only risk regression.

## Round 1 (current matchup: mountain__neuralbot2-6h)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `mountain__neuralbot2-6h` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health 152.7 vs 5.6 and avg final units 31.7 vs 1.5; minimum our final health was 111.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum score with a large safety margin; changing it would add regression risk without possible official-score upside.

## Round 2 (current matchup: mountain__neuralbot2-6h)
- Reviewed `/logs/rounds/1/`: our `gpt-5-5` was Blue again and swept `mountain__neuralbot2-6h` **250/250** for the second official round in a row.
- `python3 tools/analyze_rounds.py` summary for round 1: avg final health 151.8 vs 5.4 and avg final units 31.5 vs 1.4; minimum our final health was 106.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing score with a very large margin, so tactical edits would mainly add regression risk.

## Round 1 (current matchup: kalkin__artemis)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `kalkin__artemis` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health 93.0 vs 7.5 and avg final units 25.5 vs 2.1; minimum our final health was 62.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score in this matchup; tactical edits would add only regression risk.

## Round 2 (current matchup: kalkin__artemis)
- Reviewed official `/logs/rounds/1/`: our `gpt-5-5` was Blue, opponent `kalkin__artemis` was Red, and we swept again **250/250**.
- `python3 tools/analyze_rounds.py` summary for round 1: visual winners Blue 250/250, avg final health 95.0 vs 7.6 and avg units 25.9 vs 2.1; minimum our final health was 56.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner has now swept both official rounds in this matchup, so tactical changes would risk regression with no possible score upside.

## Round 1 (current matchup: kalkin__artemis2)
- Reviewed `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `kalkin__artemis2` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health 70.2 vs 6.3 and avg final units 23.0 vs 1.9; minimum our final health was 35.
- Left `robot.py` unchanged. Margins are lower than some previous matchups but still a perfect official score; tactical changes would risk breaking a proven full sweep with no possible upside for this opponent/round.
- Sanity check: `./rumblebot run term --results-only --seed 1 robot.py builtin-bots/simple-bot.js` still wins (Blue, Health 165-10 Units 33-2). Current local black-magic mirror tests are mixed and should not drive tuning unless the official opponent changes.

## Round 2 (current matchup: kalkin__artemis2)
- Reviewed official `/logs/rounds/1/`: opponent `kalkin__artemis2` was Blue, our `gpt-5-5` was Red, and we swept again **250/250**.
- `python3 tools/analyze_rounds.py` summary for round 1: visual winners Red 250/250, avg final health/units: opponent Blue 6.2 health and 1.8 units vs our Red 69.5 health and 23.0 units; minimum our final health was 41.
- Left `robot.py` unchanged. The current black-magic-style coordinated planner has now swept this opponent from both colors; changing tactics would risk regression with no official-score upside.

## Round 2 action (current matchup: navster8__maginot-line)
- Re-reviewed official logs after round 1: opponent `navster8__maginot-line` was Blue, our `gpt-5-5` was Red, and we swept again **250/250**.
- `python3 tools/analyze_rounds.py` summary for round 1: visual winners Red 250/250, avg final health/units: opponent Blue 3.3 health and 1.1 units vs our Red 145.6 health and 33.1 units; minimum our final health was 73.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner has a perfect 500/500 record in this matchup with huge margins; changes would add regression risk with no possible official-score upside.

## Round 1 (current matchup: jiricodes__jiricodes-bot)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `jiricodes__jiricodes-bot` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health/units: us 177.0 health and 36.1 units vs opponent 0.3 health and 0.1 units. Minimum our final health was 128.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score with an extremely large safety margin, so tactical edits would only risk regression.
- Recommendation for next teammate: if still facing `jiricodes__jiricodes-bot`, preserve `robot.py` and just re-check new logs.

## Round 2 (current matchup: jiricodes__jiricodes-bot)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `jiricodes__jiricodes-bot` **500/500** across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: we were Blue and won 250/250, avg final health/units 177.0 and 36.1 vs opponent 0.3 and 0.1.
  - Round 1: we were Red and won 250/250, avg final health/units 176.8 and 36.1 vs opponent 0.3 and 0.1.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score with enormous margins; changing tactics would only add regression risk for this matchup.

## Round 1 (current matchup: sbasu3__meek-bot)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `sbasu3__meek-bot` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health/units: us 65.2 health and 22.4 units vs opponent 5.6 health and 1.8 units; minimum our final health was 38.
- Left `robot.py` unchanged. Margins are narrower than some earlier matchups but still a perfect official score; tactical edits would risk breaking a proven sweep with no possible score upside for this opponent/round.
- Recommendation for next teammate: if still facing `sbasu3__meek-bot`, re-check new logs but strongly consider preserving the current coordinated planner unless a loss appears.

## Round 2 (current matchup: sbasu3__meek-bot)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: our `gpt-5-5` was Blue both rounds and swept `sbasu3__meek-bot` **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Blue wins 250/250, avg final health/units 65.2 and 22.4 vs opponent 5.6 and 1.8; minimum our final health 38.
  - Round 1: Blue wins 250/250, avg final health/units 64.1 and 22.3 vs opponent 5.4 and 1.7; minimum our final health 32.
- Left `robot.py` unchanged. Margins are narrower than some previous matchups, but the bot has now swept 500 official games against this opponent; tactical changes would risk regression with no official-score upside.
- Recommendation for next teammate: if still facing `sbasu3__meek-bot`, preserve the current coordinated black-magic-style planner unless a future official log shows a loss.
