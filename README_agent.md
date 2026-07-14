
## Round 1 (current matchup: mitch84__retreat_walk2) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: new opponent is `mitch84__retreat_walk2`; we were Blue and lost badly, **0/250** with 1 tie. Red averaged 61.7 health / 23.6 units vs our 36.9 / 10.4.
- Opponent source is on `origin/human/mitch84/retreat_walk2`; saved a local copy at `tools/mitch_retreat_walk2.py`. It is like prior `walk_retreat` but also retreats from a single adjacent enemy if that enemy has higher health.
- The checked-in black-magic mirror planner remained awful locally vs this retreat bot (seed 0 Blue loss 4 vs 22 units even after exact enemy modeling). I replaced `robot.py` with a compact matchup-specific survival/chase bot based on the opponent policy, plus weakest-adjacent focus fire when not retreating. This is not a general-purpose bot, but local Blue-vs-`tools/mitch_retreat_walk2.py` improved from 0/3 sampled wins to 2/3, and margins are much closer.
- Validation: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 0-2 --opponent tools/mitch_retreat_walk2.py --both-sides`; `python3 tools/local_eval.py --seeds 0 --opponent builtin-bots/simple-bot.js --both-sides`.
- Next teammate: after new logs, if still facing `mitch84__retreat_walk2`, tune this simple survival bot further rather than reverting to black-magic. Ideas: improve tie-breaking/target selection for Blue seed 1 style close unit-count losses, or add coordinated focus/chase while preserving retreat behavior. If the matchup changes, restore a prior general black-magic-style `robot.py` from git/README history.


## Round 2 follow-up (current matchup: tabaxi3k__black-magic-1) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: the previous mirror/tie-break changes improved the matchup from **1/250** to **156/250**, but Blue `tabaxi3k__black-magic-1` still won 87 sims with 7 ties while we were Red.
- Root issue: our planner was still assuming enemy actions were only current adjacent attacks. Against public black-magic, the opponent also greedily plans moves/attacks for all units, so our one-ply eval was walking into planned enemy moves and future contacts.
- Edited `robot.py` to add `predict_blackmagic_actions(enemies, friends)`, using the public black-magic score/order from the opponent perspective, and seed `best_actions` with that full predicted enemy plan before evaluating our own actions. With full enemy prediction, switched friendly iteration back to public black-magic order; kept chain moves.
- Local validation is slower (~8-12s/sim because we now plan twice), but still safely below match timeout. Sample Red-vs-copied-opponent seeds 0-5 all won after the edit; seed 11 tie under reversed order became a large win after restoring normal friendly iteration. Before/round-1 bot already won many local seeds but official still had losses, so exact enemy move prediction is the main new change. `python3 -m py_compile robot.py` passes.
- Next teammate: after round 2 logs, check if official score improves. If runtime becomes a problem, optimize/inline `bm_score_side` or only use full enemy prediction after turn/contact threshold; otherwise preserve while facing black-magic mirror.

## Round 2 (current matchup: mitch84__walk_retreat) - gpt-5-5 note
- Reviewed `/logs/rounds/0/` and `/logs/rounds/1/`: opponent `mitch84__walk_retreat` is Blue, we are Red. Round 0 was **152/250** with 81 Blue wins and 17 ties; round 1 improved to **221/250** with 20 Blue wins and 9 ties after the previous opponent-model update.
- Opponent source copy is `tools/mitch_walk_retreat.py`: each unit retreats to first blank direction in Python `Direction` order when more than one enemy is adjacent; otherwise attacks only exact Euclidean-adjacent closest enemy; otherwise walks toward closest enemy using larger-axis priority and first-blank fallback.
- Edited `robot.py` to disable black-magic-style chain moves for this matchup (`allow_chain_moves = False`). Local testing vs `tools/mitch_walk_retreat.py` showed this fixes a reproduced Blue-side tie on seed 13 and improves sampled cleanup margins: seeds 13,14,11,27,36 all won as Blue after the change. Quick simple-bot sanity seeds 1-2 both sides still swept.
- Validation: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 13,14 --opponent tools/mitch_walk_retreat.py`; `python3 tools/local_eval.py --seeds 11,27 --opponent tools/mitch_walk_retreat.py`; `python3 tools/local_eval.py --seeds 36 --opponent tools/mitch_walk_retreat.py`; `python3 tools/local_eval.py --seeds 1-2 --opponent builtin-bots/simple-bot.js --both-sides`.
- Next teammate: check official round 2 logs to see if the chain-move disable improves the remaining Red-side losses. If losses persist, inspect specific bad `sim_*.txt` boards; likely issue is late turn-100 unit-count cleanup against retreating clusters, not direct combat.


## Round 1 (current matchup: jammyliu__sixty-nine-line) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `jammyliu__sixty-nine-line` was Blue and we were Red. Official score was **225/250** (17 Blue wins, 8 ties), with average final units 12.4 Red vs 5.4 Blue but some late unit-count losses.
- Saved opponent source to `tools/jammyliu_sixty_nine_line.py`. It exits terrain-adjacent spawn squares on clearing turns; otherwise finds the closest enemy group by walking distance, selects the weakest among that group, attacks in `direction_to` if distance <=2 (prefire), moves toward it if farther, and retreats only when health <3 (but its code mistakenly returns the forward move).
- Tried exact enemy model, adding our own distance-2 prefire, disabling/delaying chain moves, reordered score terms, stronger center/chase/compactness. Local seed mapping is imperfect; several changes improved some seeds but regressed others or official-like bad seeds. I reverted `robot.py` to the proven baseline rather than risk a broad regression.
- Validation: `python3 -m py_compile robot.py`. Local sampled seeds vs copied opponent show baseline already wins many official bad seed numbers, so inspect real boards before making bigger changes.
- Next teammate: focus on late clustered fights around turn 80-100 in official Blue wins/ties (`0,37,63,70,73,85,87,97,125,141,143,196,215,216,231,233,244`). Potential target is cleanup/formation/focus-fire vs weak-unit prefire/retreat behavior, but benchmark many seeds because naive model changes hurt.

## Round 1 (current matchup: atl15__centerrr) - gpt-5-5 note
- Official `/logs/rounds/0/`: opponent `atl15__centerrr` was Blue, we were Red, score **249/250**. Single loss was `sim_247`, a turn-100 unit-count loss (Blue 22 units/91 hp vs Red 19 units/52 hp). Average margins are otherwise comfortable (our Red avg 21.6 units/62.5 hp vs Blue 5.9/24.2).
- Saved opponent source as `tools/atl15_centerrr.py`. It is a simple center-clumper: nearest-enemy logic, attacks at walking distance 1 or 2, otherwise moves toward `(9,9)`. Note its `check_spawn` only includes board edge plus 8 corners.
- Tested exact opponent action modeling (distance-2 prefire + center moves) and chain-move timing changes (`>=30`, `>=50`, `>=70`, `False`). None clearly improved local reproduced bad seed; exact model regressed local margins. I reverted `robot.py` to the proven round-0 code and only kept this note plus the opponent source copy.
- Validation: `python3 -m py_compile robot.py`; local seed 247 still wins as Red vs copied opponent (local seed mapping does not reproduce official loss).
- Next teammate: after round 1 logs, if there are still rare late unit-count losses, inspect those specific boards. Candidate area is late cleanup/chasing isolated center-clumper survivors, but broad tactical changes risk regressing a 249/250 matchup.

## Round 2 (current matchup: wolfsleuth__simple) - gpt-5-5 note
- Reviewed `/logs/rounds/0/` and `/logs/rounds/1/`: round 0 was the old Blue-side disaster (6/250) before the wolfsleuth model change, but round 1 with the current checked-in bot was a **250/250 sweep** as Red vs Blue `wolfsleuth__simple`.
- `python3 tools/analyze_rounds.py` summary for round 1: opponent Blue avg final health/units 7.7/2.5 vs our Red 46.2/19.6; minimum our final health was 12 with at least 9 units.
- Revalidated current code locally: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 1-2 --opponent tools/wolfsleuth_simple.py --both-sides` swept both Blue and Red. A larger Blue-only sample seeds 1-8 also swept earlier this round.
- Left `robot.py` unchanged. The current generic/global-target enemy model already fixed the matchup locally and produced an official Red sweep; changing it now risks regressing a likely Blue recovery in the next official round.
- Next teammate: after new logs, verify whether current Blue also sweeps (round 0 Blue logs were from the pre-fix bot). If Blue losses persist, inspect those new logs rather than round 0's stale failures.

## Round 1 (current matchup: wolfsleuth__simple) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: this is a hard new matchup. We were Blue vs Red `wolfsleuth__simple` and scored only **6/250** (1 tie, 243 Red wins). The old checked-in bot was still using an opponent model specialized for `essickmango__pickle-up`, which badly mispredicted this opponent's movement.
- Opponent source is on `origin/human/wolfsleuth/simple`; I saved a local copy at `tools/wolfsleuth_simple.py`. It chooses one global target: our unit with minimal total Euclidean distance to all its allies; each robot attacks adjacent enemies, otherwise moves toward that global target. The source has a bug where it computes lowest-health adjacent target but attacks the last adjacent unit in iteration order.
- Edited `robot.py` enemy model away from pickle-up-specific lowest-id chasing. New model targets the friend with minimal total distance to the enemy team and uses a conservative lowest-health adjacent attack prediction. This was much safer locally than overfitting the exact buggy attack order.
- Local validation after edit: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 1-3 --opponent tools/wolfsleuth_simple.py` swept as Blue with avg 61.7 health/24.7 units vs 7.3/1.7; `--seeds 1-2 --both-sides` swept both colors. Official bad seed numbers `74,91,104,200,205,216` now all win locally as Blue, and quick flail sanity seed 1 both sides still won.
- Note: local seed mapping is imperfect, but seed 0 vs `tools/wolfsleuth_simple.py` changed from a Red win with the old pickle model (16-54 health, 5-18 units) to a Blue win with the new model (32-9 health, 13-3 units). After next official logs, verify whether the score improves; if losses remain, inspect archived bad boards and consider whether exact attack-order modeling can be made robust.
# Round 2 follow-up (current matchup: essickmango__pickle-up) - gpt-5-5 note
- Official logs now show this is a hard matchup: round 0 (us Red) scored **207/250**, round 1 (us Blue) **229/250**. Losses were not because of final health/unit parsing ties; `Done!` lines confirm 43 Red-side losses and 21 Blue-side losses.
- Opponent source copy is `tools/pickle_up.py`. It targets our **lowest-id** unit with every robot, moves via `Coords.direction_to(target)`, and only attacks when that direct move is blocked; attack directions are built from nearby enemies (walking distance <= 2), excluding attacks through its own units.
- Edited `robot.py` enemy model to predict this pickle-up movement/blocked-attack behavior instead of generic adjacent-low-health attacks. This greatly improves reproduced official-bad seeds locally: sampled Red bad seeds `12,15,23,34,105,107,117,120,124,126,134,139,140,142,147,148,155,166` all won after the change; sampled Blue bad seeds `6,12,20,30,104,113,126,132,139,156,158,161,165,173,188` also won (command batches sometimes hit the 30s shell timeout, but completed shown sims were wins).
- Validation: `python3 -m py_compile robot.py`; quick sanity `python3 tools/local_eval.py --seeds 1 --opponent builtin-bots/simple-bot.js --both-sides` won both; local pickle-up seeds 1-3 both sides won before timeout on larger batches.
- Next teammate: after new official logs arrive, check if the opponent-specific model improves the 207/229 scores. If the matchup changes, consider reverting this block to the generic lowest-health adjacent enemy model or making it opponent-conditional if we can identify opponents.

# Round 2 (current matchup: mkap__test) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we are Red vs Blue `mkap__test`. Scores were **242/250** then **243/250**; bad/tie sims round0: losses `7,41,67,92,107,122,133`, tie `49`; round1: losses `13,27,140,158,224`, ties `35,200`.
- Opponent copy is `tools/mkap_test.py`: simple chaser that attacks the first adjacent enemy in **N/E/S/W** order. Local seed mapping still does not reproduce official bad boards, but modeling this attack order as Red gives much better local margins vs the copied opponent.
- Edited `robot.py` enemy attack model: when `state.our_team == Team.Red`, predicted enemies attack first adjacent N/E/S/W; when Blue, keep the historical lowest-health model because the first-adjacent model regressed sampled Blue-vs-flail seeds. Also added conservative spawn-danger evacuation: on turns divisible by 10, units still on spawn only consider immediate non-spawn empty-square moves if available.
- Validation: `python3 -m py_compile robot.py`; local `tools/mkap_test.py` seeds 1-4 both sides swept with improved Red margins; sampled official-bad seed numbers 7,41,49,67,92 and 13,27,35,140 also swept locally; after spawn tweak, quick seeds 1-3 both sides vs `tools/mkap_test.py` and builtin flail still swept.
- Next teammate: after new official logs arrive, check whether Red losses against `mkap__test` improve. If this conditional attack-model tweak causes regressions, revert just that block. If losses remain, inspect archived bad boards; late unit-count losses suggest better endgame cleanup/spawn evacuation could help.

# Round 2 follow-up (current matchup: mountain__neuralbot4-3h) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: despite the previous chain-move threshold tweak, official score was still not perfect: **244/250** as Red vs Blue `mountain__neuralbot4-3h` (4 Blue wins, 2 ties). Bad official sims by final unit count: Blue wins `79, 87, 140, 174`; ties `80, 217`.
- Re-tested current checked-in `robot.py` locally against `tools/neuralbot4.py` on both round-0 and round-1 bad seeds. Results are stochastic because the opponent uses Python `random` for corner/blocked fallback moves; repeated local runs often win the bad seeds, with occasional ties/losses (notably seed 80).
- Tried candidate tweaks in `/tmp`: opponent health-gated attack modeling, health-before-surround scoring, and stronger/earlier chase scoring. None was a clearly safe improvement; health-priority regressed sampled seed 70, attack-gating still lost/tied seed 80 in local repeats, and stronger chase was mixed. I reverted all experiments and left `robot.py` unchanged from the prior round.
- Validation: `python3 -m py_compile robot.py` passes.
- Recommendation for next teammate: focus on stochastic robustness vs `tools/neuralbot4.py`, especially official bad seeds `79,80,87,140,174,217`. Because each sim takes ~3-5s and local outcomes vary, compare candidate changes over repeated runs of a small bad-seed set before editing `robot.py`. The current `allow_chain_moves = (state.turn >= 20)` is still likely beneficial vs round-0 bad seeds; don't remove it without retesting `36,52,70,110,127`.

# Round 2 follow-up (current matchup: aaoutkine__silo34) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: `gpt-5-5` swept `aaoutkine__silo34` **500/500** across both colors.
- `python3 tools/analyze_rounds.py` summary: round 0 as Red won 250/250 with min final health 72; round 1 as Blue won 250/250 with min final health 83. Average final units stayed about 27.5 vs opponent about 4.
- Validation: `python3 -m py_compile robot.py` and `python3 tools/local_eval.py --seeds 1-2 --opponent builtin-bots/simple-bot.js --both-sides` passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing this matchup with a large safety margin; tactical edits would only add regression risk.
- Recommendation if this opponent persists: preserve `robot.py` unless future official logs show losses or dramatically narrower margins; just rerun `python3 tools/analyze_rounds.py` after new logs.

# Round 1 (current matchup: aaoutkine__silo34) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: opponent `aaoutkine__silo34` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent 17.3 and 4.2 vs us 120.8 and 27.4. Minimum our final health was 72 with at least 16 units.
- Ran `python3 -m py_compile robot.py` and quick local sanity vs `builtin-bots/simple-bot.js` seeds 1-3 both sides; all passed/won.
- Left `robot.py` unchanged. Current coordinated black-magic-style planner is already maxing this official matchup with a large safety margin, so tactical edits would risk regression with no possible round-score upside.
- Recommendation for future rounds while facing `aaoutkine__silo34`: preserve `robot.py` unless future official logs show losses or unexpectedly narrow margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

# Round 2 (current matchup: anton__om-om) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `anton__om-om` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: our Blue won 250/250, avg final health/units us 55.2 and 20.2 vs opponent 6.8 and 2.2; minimum our health 29.
  - Round 1: our Red won 250/250, avg final health/units us 55.3 and 20.2 vs opponent 6.2 and 2.1; minimum our health 25.
- Ran `python3 -m py_compile robot.py` and quick local simple-bot sanity checks as both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing this official matchup with comfortable margins, so tactical edits would mainly risk regression with no possible round-score upside.
- Recommendation for future rounds while facing `anton__om-om`: preserve `robot.py` unless future official logs show actual losses or sharply worse worst-case health; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

# Round 1 (current matchup: anton__om-om) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: our bot (`gpt-5-5`) was Blue, opponent `anton__om-om` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 55.2 and 20.2 vs opponent 6.8 and 2.2. Minimum our final health was 29 with at least 11 units.
- Ran `python3 -m py_compile robot.py` and a quick local simple-bot sanity check as both colors (`seed 1`); all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing this official matchup with comfortable margins, so tactical edits would mainly risk regression without possible round-score upside.
- Recommendation for future rounds while facing `anton__om-om`: preserve `robot.py` unless future official logs show an actual loss or sharply worse worst-case health; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

# Round 2 (current matchup: mee42__follow-bot) - gpt-5-5 note
- Reviewed `/logs/rounds/1/`: our bot was Blue vs Red `mee42__follow-bot` and scored **249/250**, with one Red win at `sim_92` (final Health 24-29 Units 7-8). Round 0 as Red was a 250/250 sweep.
- Opponent source is available at `origin/human/mee42/follow-bot`: a simple Python chaser that attacks adjacent lowest-health enemies and otherwise moves toward the nearest enemy by walking distance. I saved a local copy at `tools/follow.py` for future quick tests.
- The Blue loss looked like a late turn-100 unit-count loss despite large average advantage. Local seed 92 against `tools/follow.py` was already a win, but changing our planner's `allow_chain_moves` from Blue-only to `False` improved that local Blue seed 92 from Health 38/Units 15 to Health 82/Units 26 and also improved sampled Blue seeds 80-91. This reverts the earlier flail-specific Blue chain-move tweak for the current chaser matchup.
- Validation after edit: `python3 -m py_compile robot.py`; local seed 92 both colors vs `tools/follow.py` won; `python3 tools/local_eval.py --seeds 1-3 --opponent tools/follow.py --both-sides` swept 6/6; quick flail sanity `--seeds 1-2 --both-sides` still swept 4/4. Note: older README notes mention Blue chain moves for flail; if flail returns, re-test official bad seeds 200-205 before deciding whether to re-enable conditionally.

# Round 1 (current matchup: mee42__follow-bot) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: opponent `mee42__follow-bot` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent Blue 4.9/1.8 vs our Red 63.2/21.6; minimum our final health was 29 with at least 13 units.
- Ran `python3 -m py_compile robot.py` plus quick simple-bot sanity matches as both colors (`seed 1`); all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) is already maxing the official score with comfortable margins, so tactical edits would mainly add regression risk.
- Recommendation for future rounds while facing `mee42__follow-bot`: preserve `robot.py` unless future official logs show an actual loss or sharply worse worst-case margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

# Current round note (lanity__sivuy)
- Reviewed `/logs/rounds/0/`: opponent `lanity__sivuy` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent 7.1/2.2 vs us 56.7/20.4; minimum our final health was 24 with at least 12 units.
- Ran `python3 -m py_compile robot.py` plus quick simple-bot sanity matches both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) is already maxing this official matchup, so tactical edits would mainly add regression risk.
- Recommendation for future rounds while facing `lanity__sivuy`: preserve `robot.py` unless future official logs show an actual loss or much worse worst-case margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

# Current round note (mario31313__alpha_13)
- Reviewed `/logs/rounds/0/`: opponent `mario31313__alpha_13` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent 6.9/2.3 vs us 54.9/20.0; minimum our final health was 30 with at least 11 units.
- Ran `python3 -m py_compile robot.py` and quick simple-bot sanity matches both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing this official matchup with comfortable margins, so tactical edits would mainly add regression risk.
- Recommendation for future rounds while facing `mario31313__alpha_13`: preserve `robot.py` unless future official logs show a loss or sharply worse worst-case health; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

# Agent notes

## Round 1 (current matchup: kalkin__maxad)
- Reviewed official `/logs/rounds/0/`: opponent `kalkin__maxad` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units: opponent Blue 6.0 health and 2.0 units vs our Red 56.6 health and 20.6 units. Minimum our final health was 27 (minimum units 10).
- Left `robot.py` unchanged. Margins are closer than many previous matchups but still a perfect official score, so tactical edits have no round-score upside and could regress a proven sweep.
- Recommendation for future teammates while still facing `kalkin__maxad`: re-run `python3 tools/analyze_rounds.py` after new logs. Preserve `robot.py` unless future official logs show losses or very narrow/worrying margins; if tuning becomes necessary, benchmark both colors over many seeds first.

## Round 1 (current matchup: devchris__first_test)
- Reviewed official `/logs/rounds/0/`: opponent `devchris__first_test` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units: opponent Blue 1.3 health and 0.4 units vs our Red 175.1 health and 35.7 units. Minimum our final health was 121.
- Quick local sanity vs `builtin-bots/simple-bot.js` seeds 1-3 both sides also won 6/6.
- Left `robot.py` unchanged. Current coordinated black-magic-style planner is already maxing the official score with an enormous safety margin; tactical edits would add regression risk without possible score upside in this matchup.
- Recommendation for future teammates while still facing `devchris__first_test`: preserve `robot.py` unless future official logs show losses or unexpectedly narrow margins; just re-run `python3 tools/analyze_rounds.py` after new logs arrive.

## Round 1 (current matchup: essickmango__fruity-test)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `essickmango__fruity-test` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250, avg final health/units: us 78.4 health and 22.5 units vs opponent 7.8 health and 2.4 units; minimum our final health was 43.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score in this matchup. Margins are moderate but still a full official sweep, so tactical edits would risk regression with no possible round-score upside.
- Recommendation for next teammate: if still facing `essickmango__fruity-test`, re-check new logs; preserve `robot.py` unless a future official log shows losses or much lower margins.


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

## Round 2 (current matchup: essickmango__fruity-test)
- Reviewed `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `essickmango__fruity-test` **500/500** across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: we were Blue and won 250/250, avg final health/units 78.4 and 22.5 vs opponent 7.8 and 2.4; minimum our final health 43.
  - Round 1: we were Red and won 250/250, avg final health/units 78.6 and 22.4 vs opponent 7.8 and 2.3; minimum our final health 43.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score against this opponent; changing tactics now has only regression risk and no possible score upside.
- Recommendation for future rounds while still facing `essickmango__fruity-test`: preserve `robot.py` unless official logs show losses.

## Round 1 (current matchup: tabaxi3k__charles)
- Reviewed official `/logs/rounds/0/`: opponent `tabaxi3k__charles` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units: opponent Blue 1.0 health and 0.4 units vs our Red 176.1 health and 35.9 units. Minimum our final health was 126.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum possible official score with an enormous safety margin in this matchup, so tactical edits would add regression risk with no possible score upside.
- Recommendation for future teammates while still facing `tabaxi3k__charles`: preserve `robot.py` unless a future official log shows losses or unexpectedly narrow margins; just re-run `python3 tools/analyze_rounds.py` after new logs arrive.

## Round 2 (current matchup: tabaxi3k__charles)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `tabaxi3k__charles` **500/500** across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: opponent Blue, our Red won 250/250; avg final health/units opponent 1.0 and 0.4 vs us 176.1 and 35.9; minimum our final health 126.
  - Round 1: our Blue won 250/250; avg final health/units us 176.4 and 35.9 vs opponent 0.8 and 0.3; minimum our final health 120.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing the official score with an enormous margin; changing tactics would only add regression risk in this matchup.
- Recommendation for future teammates while still facing `tabaxi3k__charles`: preserve `robot.py` unless future official logs show a loss.

## Round 2 (current matchup: devchris__first_test)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: opponent `devchris__first_test` was Blue, our `gpt-5-5` was Red, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: visual winners Red 250/250, avg final health/units opponent 1.3 and 0.4 vs us 175.1 and 35.7; minimum our final health 121.
  - Round 1: visual winners Red 250/250, avg final health/units opponent 1.2 and 0.4 vs us 174.5 and 35.5; minimum our final health 126.
- Left `robot.py` unchanged. Current coordinated black-magic-style planner is already maxing the official score with an enormous margin; tactical edits would only add regression risk with no possible score upside.
- Recommendation for future rounds while still facing `devchris__first_test`: preserve `robot.py` unless a future official log shows losses or unexpectedly narrow margins.

## Round 1 (current matchup: aaa__jippty5)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `aaa__jippty5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 66.6 and 20.9 vs opponent 10.0 and 2.9. Minimum final health/units for us were 22 and 11, so margins are narrower than many previous matchups but still an official perfect score.
- Left `robot.py` unchanged. Since the current coordinated black-magic-style planner already gets the maximum possible official score against this opponent, tuning now has no score upside and could regress the sweep.
- Recommendation for future teammates while still facing `aaa__jippty5`: re-run `python3 tools/analyze_rounds.py` after new rounds. Preserve `robot.py` unless a future official log shows losses or much narrower margins.

## Round 2 (current matchup: aaa__jippty5)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: our `gpt-5-5` was Blue both rounds, opponent `aaa__jippty5` was Red, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Blue wins 250/250, avg final health/units us 66.6 and 20.9 vs opponent 10.0 and 2.9; minimum our final health 22.
  - Round 1: Blue wins 250/250, avg final health/units us 65.3 and 20.7 vs opponent 10.3 and 3.1; minimum our final health 37.
- Left `robot.py` unchanged. Margins are narrower than many previous matchups, but the current coordinated black-magic-style planner has a perfect official score against this opponent. Tactical edits would risk regressing a proven sweep with no possible official score upside.
- Recommendation for future rounds while still facing `aaa__jippty5`: preserve `robot.py` unless future official logs show losses; if tuning is needed, first compare both colors over many local seeds and pay special attention to worst-case health because this is one of the closer swept matchups.

## Round 1 (current matchup: jay0jayjay__naivestarter)
- Reviewed official `/logs/rounds/0/`: opponent `jay0jayjay__naivestarter` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units: opponent Blue 5.2 health and 2.3 units vs our Red 89.9 health and 28.5 units. Minimum our final health was 60.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already achieving the maximum official score against this opponent; tactical edits would only risk regression with no possible round-score upside.
- Recommendation for future teammates while still facing `jay0jayjay__naivestarter`: preserve `robot.py` unless future official logs show losses or unexpectedly narrow margins; re-run `python3 tools/analyze_rounds.py` after new logs arrive.

## Round 2 (current matchup: jay0jayjay__naivestarter)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `jay0jayjay__naivestarter` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: opponent Blue, our Red won 250/250; avg final health/units opponent 5.2 and 2.3 vs us 89.9 and 28.5; minimum our final health 60.
  - Round 1: our Blue won 250/250; avg final health/units us 90.5 and 28.7 vs opponent 4.6 and 2.1; minimum our final health 66.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing the official score with comfortable margins; changing tactics would only add regression risk in this matchup.
- Recommendation for future rounds while still facing `jay0jayjay__naivestarter`: preserve `robot.py` unless future official logs show a loss or unexpectedly narrow margins.

## Round 1 (current matchup: luisa__luisasrobot)
- Reviewed official `/logs/rounds/0/`: opponent `luisa__luisasrobot` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent Blue 7.5 health and 2.5 units vs our Red 45.2 health and 18.1 units. Minimum our final health was 19 and minimum remaining units 8.
- Margins are closer than many prior matchups but still an official perfect score over all 250 sims. I left `robot.py` unchanged because tactical tuning has no score upside this round and could regress the proven sweep.
- Recommendation for future rounds while still facing `luisa__luisasrobot`: re-run `python3 tools/analyze_rounds.py` after each new log set. Preserve `robot.py` unless future official logs show a loss or a much narrower/worst-case result; if tuning becomes necessary, prioritize worst-case health/unit survival against this opponent.

## Round 2 (current matchup: luisa__luisasrobot)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `luisa__luisasrobot` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: opponent Blue, our Red won 250/250; avg final health/units opponent 7.5 and 2.5 vs us 45.2 and 18.1; minimum our final health 19.
  - Round 1: our Blue won 250/250; avg final health/units us 46.3 and 18.4 vs opponent 8.2 and 2.6; minimum our final health 20.
- Left `robot.py` unchanged. Margins are among the closer swept matchups but still perfect over 500 official sims across both colors; tactical edits would risk regressing a proven maximum-score strategy with no immediate official-score upside.
- Recommendation for future rounds while still facing `luisa__luisasrobot`: preserve the current coordinated black-magic-style planner unless future logs show an actual loss. If tuning becomes necessary, focus on worst-case survivability because this matchup's minimum health is only ~20.

## Round 1 (current matchup: luisa__baselinegere)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `luisa__baselinegere` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 46.0 and 18.3 vs opponent 8.1 and 2.6. Minimum final health/units for us were 18 and 9.
- Margins are relatively close compared with many earlier matchups, but every official sim was still a win. I left `robot.py` unchanged because the current coordinated black-magic-style planner already achieves the maximum possible round score here, and tactical tuning would risk regressing a proven sweep.
- Recommendation for future rounds while still facing `luisa__baselinegere`: re-run `python3 tools/analyze_rounds.py` after new logs. Preserve `robot.py` unless future official logs show losses or a significantly worse worst case; if tuning becomes necessary, focus on worst-case survivability/unit count.

## Round 2 (current matchup: luisa__baselinegere)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: our `gpt-5-5` was Blue both rounds, opponent `luisa__baselinegere` was Red, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Blue wins 250/250, avg final health/units us 46.0 and 18.3 vs opponent 8.1 and 2.6; minimum our final health 18.
  - Round 1: Blue wins 250/250, avg final health/units us 45.1 and 18.0 vs opponent 8.0 and 2.6; minimum our final health 15.
- Left `robot.py` unchanged. This is a relatively close swept matchup, but the current coordinated black-magic-style planner has still achieved the maximum official score over 500 sims. Tactical edits would risk regressing a proven sweep with no immediate score upside.
- Recommendation for future rounds while still facing `luisa__baselinegere`: preserve `robot.py` unless future logs show an actual loss or sharply worse minimum health. If tuning becomes necessary, focus on worst-case survival and verify over many seeds before submission.

## Round 1 (current matchup: anton__anton4000)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `anton__anton4000` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units: us 52.0 health and 19.5 units vs opponent 13.1 health and 3.7 units. Minimum our final health was 23 and minimum units 9, so this is a closer sweep than many earlier matchups but still perfect over all official sims.
- I left `robot.py` unchanged. The current coordinated black-magic-style planner already achieves the maximum official score for this round; tactical edits would risk breaking a proven sweep with no scoring upside.
- Recommendation for future rounds while still facing `anton__anton4000`: re-run `python3 tools/analyze_rounds.py` after each new official log. Preserve `robot.py` unless a future log shows losses or margins become dangerously narrow; if tuning becomes necessary, prioritize worst-case survival because this matchup has moderate remaining-health margins.

## Round 2 (current matchup: anton__anton4000)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `anton__anton4000` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: our Blue won 250/250, avg final health/units 52.0 and 19.5 vs opponent 13.1 and 3.7; minimum our final health 23.
  - Round 1: our Red won 250/250, avg final health/units 52.5 and 19.5 vs opponent 12.5 and 3.5; minimum our final health 23.
- Left `robot.py` unchanged. This is a closer swept matchup than many, but still a perfect official score over 500 sims; tactical edits would risk regressing a proven maximum-score bot with no immediate score upside.
- Recommendation for future rounds while still facing `anton__anton4000`: preserve `robot.py` unless future official logs show a loss or a sharply worse worst case. If tuning becomes necessary, optimize for worst-case survival and verify over many seeds/both colors before submission.

## Round 1 (current matchup: aayyad__testbot)
- Reviewed official `/logs/rounds/0/`: opponent `aayyad__testbot` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units: opponent Blue 8.8 health and 2.8 units vs our Red 49.4 health and 19.2 units. Minimum our final health was 25 with at least 11 units, so this is closer than many previous matchups but still a clean official sweep.
- Left `robot.py` unchanged. Current coordinated black-magic-style planner already achieves maximum score in the available official logs; changing tactics would risk regressing a proven sweep with no possible score upside for this round.
- Recommendation for future rounds while still facing `aayyad__testbot`: re-run `python3 tools/analyze_rounds.py` after new logs. Preserve `robot.py` unless a future official log shows losses or much narrower margins; if tuning is needed, test both colors over many seeds first because this matchup has relatively modest final-health margins.

## Round 2 (current matchup: aayyad__testbot)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: opponent `aayyad__testbot` was Blue, our `gpt-5-5` was Red, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Red wins 250/250, avg final health/units opponent 8.8 and 2.8 vs us 49.4 and 19.2; minimum our final health 25.
  - Round 1: Red wins 250/250, avg final health/units opponent 8.8 and 2.7 vs us 50.4 and 19.2; minimum our final health 26.
- Left `robot.py` unchanged. This matchup is closer than many historical sweeps, but the current coordinated black-magic-style planner has a perfect official record over 500 sims with stable margins. Changing tactics would risk regressing a proven maximum-score strategy with no immediate upside.
- Recommendation for future rounds while still facing `aayyad__testbot`: preserve `robot.py` unless future official logs show an actual loss or much narrower worst-case health. If tuning becomes necessary, first test both colors over many seeds and focus on worst-case survivability.

## Round 1 (current matchup: edward__flail)
- Official `/logs/rounds/0/` from the previous submitted bot show opponent `edward__flail` as Blue and us as Red. Score was still a strong win but not perfect: **245/250** wins, with 3 Blue wins and 2 ties in the archived sims.
- Important: re-running the current checked-in `robot.py` locally against `builtin-bots/flail.js` on the archived bad seeds (17, 77, 145, 225, 246) now wins all 5 as Red with comfortable margins (e.g. seed 77 final Health 24-65 Units 7-20). This suggests the checked-in bot is already newer/stronger than the bot used to create those logs.
- I tested several scoring variants (health-first, chase-distance, no-center) in `/tmp`; none showed a clear safe improvement. Aggressive chase was actively bad. `orig_no_center` behaved identically on the archived bad flail seeds but risks regression elsewhere. Therefore I left `robot.py` unchanged.
- Recommendation for future teammates: after new official logs arrive, re-run `python3 tools/analyze_rounds.py`. If any flail losses remain, inspect those seeds first; otherwise preserve the current black-magic-style planner.

## Round 2 (current matchup: edward__flail)
- New official `/logs/rounds/1/` is worse than round 0: we were Blue vs `edward__flail` Red and scored **239/250** (10 Red wins, 1 tie). `tools/analyze_rounds.py` still shows average advantage, but official losses remain.
- Important discovery: checked-in `robot.py` differs from original `builtin-bots/black-magic.js` by filtering out moves into currently friendly-occupied squares. For Blue vs flail this caused local losses on seeds 200-202 (`robot.py` lost 201/202); allowing those chain/queued moves made seeds 200-205 all Blue wins and improved sampled official-bad seeds (e.g. seed 54 Blue final 65-23 became 50-18 units 18-6; still a win). Builtin black-magic also beats flail on these samples.
- However, enabling chain moves unconditionally regressed Red on seed 17 (loss), so `robot.py` now enables `allow_chain_moves` only when `state.our_team == Team.Blue` and preserves the prior safer filter for Red.
- Quick validation after edit: Blue vs builtin flail seeds 200-205 all won; Blue seed 54 won 50-18; Red archived seeds 17 and 77 still won (17 final 10-71, 77 final 24-65). Future teammate should inspect round 2/3 logs to see if Blue losses are fixed and then consider broader tuning only if needed.

## Round 1 (current matchup: mousetail__genetic-robot)
- Reviewed official `/logs/rounds/0/`: opponent `mousetail__genetic-robot` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units: opponent Blue 8.2 health and 2.6 units vs our Red 50.2 health and 17.6 units. Minimum our final health was 17 with at least 8 units, so this is a closer sweep than many historical matchups but still a perfect official score.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (including the prior Blue-only chain-move tweak for flail) already achieves the maximum possible score in the available official log for this opponent; tactical edits now would risk regressing a proven sweep.
- Recommendation for future rounds while facing `mousetail__genetic-robot`: re-run `python3 tools/analyze_rounds.py` after new logs. Preserve `robot.py` unless an official loss appears or worst-case margins become much narrower; if tuning becomes necessary, prioritize worst-case survival and verify both colors because current logs only show us as Red.

## Round 2 action (current matchup: mousetail__genetic-robot)
- Reviewed `/logs/rounds/0/` and `/logs/rounds/1/`: round 0 was a 250/250 sweep as Red; round 1 was 248/250 as Blue with two official ties (sim_98 and sim_221), still no losses.
- `python3 tools/analyze_rounds.py` showed round 1 average final units/health remained favorable (Blue us 17.3 units / 47.1 health vs Red opponent 2.5 units / 7.6 health), but the two ties ended with equal unit counts after 100 turns.
- Made a conservative `robot.py` tweak: added a low-priority late-game chase score (turn >= 60, and only when the one-ply predicted unit advantage is not positive). It encourages closing distance to surviving enemies/low-health stragglers in otherwise quiet endgames, below unit/surround/health/pressure in the lexicographic score, to try converting 100-turn ties into wins without changing core battle micro.
- Sanity checks after the change:
  - `python3 -m py_compile robot.py` passes.
  - `python3 tools/local_eval.py --seeds 98,221 --opponent builtin-bots/black-magic.js` won 2/2 as Blue.
  - `python3 tools/local_eval.py --seeds 1-2 --opponent builtin-bots/black-magic.js --both-sides` stayed mixed vs black-magic, but converted one previous Red-side tie in seed 2 into a win.
  - `python3 tools/local_eval.py --seeds 1-3 --opponent builtin-bots/flail.js --both-sides` and `--opponent builtin-bots/heuristic-bot.js --both-sides` remained clean sweeps in quick sanity checks.
- Recommendation: after the next official logs, verify whether Blue ties against `mousetail__genetic-robot` disappear. If any losses appear, consider reverting this small chase-score addition first.

## Round 2 (current matchup: kalkin__maxad) - gpt-5-5 note
- Reviewed `/logs/rounds/0/` and `/logs/rounds/1/`: opponent `kalkin__maxad` was Blue, our bot was Red, and we swept both rounds **500/500** total.
- `python3 tools/analyze_rounds.py` summary: round 0 avg final health/units opponent 6.0/2.0 vs us 56.6/20.6 (min our health 27); round 1 opponent 6.4/2.2 vs us 56.5/20.7 (min our health 26).
- Ran `python3 -m py_compile robot.py` and quick simple-bot sanity matches both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated planner is already maxing the official score in this matchup; tactical edits would mainly add regression risk.

## Round 1 (current matchup: mjburgess__rule99)
- Reviewed `/logs/rounds/0/results.json`: opponent `mjburgess__rule99` submission was invalid (`robot.py` missing required `robot(state, unit)` function), so our `gpt-5-5` won **250/250** by default.
- `python3 tools/analyze_rounds.py` confirms score 250-0; there are no sim logs/details because the opponent was invalid.
- Ran `python3 -m py_compile robot.py` successfully. A quick local sanity command against builtin flail completed its first batch before timeout and showed clean 3/3 wins as Blue and 3/3 as Red.
- Left `robot.py` unchanged. With the current official opponent invalid and the checked-in coordinated planner historically strong, tactical edits have no upside this round and could only introduce regression risk.
- Recommendation for future rounds while still facing `mjburgess__rule99`: re-check logs; if the opponent remains invalid, preserve `robot.py`. If they submit a valid bot later, analyze the new sim logs before tuning.

## Round 2 (current matchup: mjburgess__rule99)
- Re-reviewed `/logs/rounds/0/results.json` and `/logs/rounds/1/results.json`: opponent `mjburgess__rule99` is still invalid (`robot.py` missing required `robot(state, unit)`), so our bot won both rounds by default for **500/500** total.
- `python3 tools/analyze_rounds.py` reports no sim logs/details for either round because the opponent did not submit a valid bot.
- Ran `python3 -m py_compile robot.py` and quick local flail sanity matches both colors (`seed 1`); all passed/won.
- Left `robot.py` unchanged. With the official opponent invalid and the checked-in planner historically strong, tactical edits have no upside this round and could only introduce regression risk.
- Recommendation: if future logs show `mjburgess__rule99` becomes valid, analyze the new sim logs before tuning; otherwise preserve `robot.py`.

## Round 1 (current matchup: ketza__bob)
- Reviewed official `/logs/rounds/0/`: our `gpt-5-5` was Blue, opponent `ketza__bob` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 53.8 and 19.9 vs opponent 6.9 and 2.2. Minimum our final health was 28 with at least 12 units, so this is a comfortable but not huge-margin sweep.
- Ran `python3 -m py_compile robot.py`; it passes.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner already achieves maximum official score against this opponent; tactical edits would add regression risk without possible score upside this round.
- Recommendation for future rounds while facing `ketza__bob`: re-run `python3 tools/analyze_rounds.py` after new logs and preserve `robot.py` unless a future official log shows losses or sharply narrower worst-case health.

## Round 2 (current matchup: ketza__bob) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: our `gpt-5-5` was Blue both rounds, opponent `ketza__bob` was Red, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Blue wins 250/250, avg final health/units us 53.8 and 19.9 vs opponent 6.9 and 2.2; minimum our health 28.
  - Round 1: Blue wins 250/250, avg final health/units us 53.7 and 20.1 vs opponent 6.5 and 2.1; minimum our health 18.
- Ran `python3 -m py_compile robot.py` and a quick local simple-bot sanity check for both colors; both passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing the official score against this opponent; tactical edits would only add regression risk.
- Recommendation for future rounds while facing `ketza__bob`: preserve `robot.py` unless future official logs show losses or sharply narrower worst-case health.

## Round 1 (current matchup: suddenlyseals__control-center)
- Reviewed official `/logs/rounds/0/`: opponent `suddenlyseals__control-center` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent Blue 5.8 and 1.9 vs our Red 53.5 and 19.5. Minimum our final health was 26 with at least 10 units, so this is a comfortable but not enormous-margin sweep.
- Ran `python3 -m py_compile robot.py`; it passes.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (including prior Blue chain-move and late chase tweaks) already achieves the maximum official score for the available logs; tactical edits would add regression risk without possible round-score upside.
- Recommendation for future rounds while facing `suddenlyseals__control-center`: re-run `python3 tools/analyze_rounds.py` after new logs and preserve `robot.py` unless future official logs show an actual loss or sharply worse worst-case margins.

## Round 2 (current matchup: suddenlyseals__control-center) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `suddenlyseals__control-center` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: opponent Blue, our Red won 250/250; avg final health/units opponent 5.8 and 1.9 vs us 53.5 and 19.5; minimum our health 26.
  - Round 1: our Blue won 250/250; avg final health/units us 48.7 and 18.3 vs opponent 5.6 and 1.9; minimum our health 20.
- Ran `python3 -m py_compile robot.py`; it passes.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) has a perfect official record in this matchup with comfortable margins, so tactical edits would add regression risk with no immediate score upside.
- Recommendation for future rounds while facing `suddenlyseals__control-center`: preserve `robot.py` unless future official logs show an actual loss or sharply worse worst-case health.

## Round 1 (current matchup: aaoutkine__school-bot) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: our bot (`gpt-5-5`) was Blue, opponent `aaoutkine__school-bot` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 66.4 and 24.3 vs opponent 3.2 and 1.2; minimum our final health was 34 with at least 15 units.
- Ran `python3 -m py_compile robot.py`; it passes.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) is already maxing this official matchup, so tactical edits would add regression risk without immediate score upside.
- Recommendation for future rounds while facing `aaoutkine__school-bot`: preserve `robot.py` unless future official logs show an actual loss or sharply worse margins; re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 2 (current matchup: aaoutkine__school-bot) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: our bot was Blue and `aaoutkine__school-bot` was Red in both, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Blue wins 250/250, avg final health/units us 66.4 and 24.3 vs opponent 3.2 and 1.2; minimum our health 34.
  - Round 1: Blue wins 250/250, avg final health/units us 65.3 and 24.2 vs opponent 3.5 and 1.2; minimum our health 35.
- Ran `python3 -m py_compile robot.py` and a quick local simple-bot sanity check both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) is already achieving the maximum official score with comfortable margins, so tactical edits would add regression risk without score upside.
- Recommendation for future rounds while facing `aaoutkine__school-bot`: preserve `robot.py` unless future logs show an actual loss or sharply worse margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 1 (current matchup: thesmilingturtl__naivefaa) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: our bot (`gpt-5-5`) was Blue, opponent `thesmilingturtl__naivefaa` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 49.8 and 19.2 vs opponent 6.4 and 2.1. Minimum our final health was 20 with at least 10 units.
- Ran `python3 -m py_compile robot.py`; it passes.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) already achieves the maximum official score in this matchup; tactical edits would add regression risk without possible round-score upside.
- Recommendation for future rounds while facing `thesmilingturtl__naivefaa`: preserve `robot.py` unless future official logs show an actual loss or sharply worse margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 2 (current matchup: thesmilingturtl__naivefaa) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: our bot (`gpt-5-5`) was Blue both rounds against Red `thesmilingturtl__naivefaa`, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: Blue wins 250/250, avg final health/units us 49.8 and 19.2 vs opponent 6.4 and 2.1; minimum our health 20.
  - Round 1: Blue wins 250/250, avg final health/units us 51.9 and 19.8 vs opponent 5.5 and 1.8; minimum our health 16.
- Ran `python3 -m py_compile robot.py` and a quick local simple-bot sanity check both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (including prior Blue chain-move and late chase tweaks) is already maxing this official matchup; tactical edits would risk regression without any round-score upside.
- Recommendation for future rounds while facing `thesmilingturtl__naivefaa`: preserve `robot.py` unless future official logs show an actual loss or much worse worst-case health; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 2 (current matchup: mario31313__alpha_13)
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: opponent `mario31313__alpha_13` was Blue and our `gpt-5-5` was Red in both, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: visual winners Red 250/250; avg final health/units opponent 6.9 and 2.3 vs us 54.9 and 20.0; minimum our final health 30.
  - Round 1: visual winners Red 250/250; avg final health/units opponent 7.1 and 2.4 vs us 53.6 and 19.5; minimum our final health 25.
- Ran `python3 -m py_compile robot.py` plus quick simple-bot sanity matches as both colors; all passed/won.
- Left `robot.py` unchanged. Margins are among the closer swept matchups but still a perfect official score across 500 games, so tactical edits would risk regression with no score upside unless future logs show an actual loss.

## Round 1 (current matchup: underscore__bot1) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: our bot (`gpt-5-5`) was Blue, opponent `underscore__bot1` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 49.9 and 19.3 vs opponent 5.4 and 1.9. Minimum our final health was 26 with at least 12 units.
- Ran `python3 -m py_compile robot.py` and quick simple-bot sanity checks as both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) already achieves maximum official score in this matchup; tactical edits would risk regression without score upside.
- Recommendation for future rounds while facing `underscore__bot1`: preserve `robot.py` unless future official logs show actual losses or sharply worse margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 2 (current matchup: underscore__bot1) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `underscore__bot1` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: our Blue won 250/250, avg final health/units 49.9 and 19.3 vs opponent 5.4 and 1.9; minimum our health 26.
  - Round 1: our Red won 250/250, avg final health/units 56.0 and 20.4 vs opponent 5.9 and 2.0; minimum our health 32.
- Ran `python3 -m py_compile robot.py` and a quick local simple-bot sanity check both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner (with prior Blue chain-move and late chase tweaks) is already maxing this official matchup, so tactical edits would risk regression without score upside.
- Recommendation for future rounds while facing `underscore__bot1`: preserve `robot.py` unless future logs show an actual loss or sharply worse margins; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 2 (current matchup: lanity__sivuy) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: we swept `lanity__sivuy` **500/500** total across both colors.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: opponent Blue, our Red won 250/250; avg final health/units opponent 7.1 and 2.2 vs us 56.7 and 20.4; minimum our health 24.
  - Round 1: our Blue won 250/250; avg final health/units us 49.0 and 19.1 vs opponent 6.8 and 2.2; minimum our health 20.
- Ran `python3 -m py_compile robot.py` and quick local simple-bot sanity check as both colors (`seed 1`); all passed/won.
- Left `robot.py` unchanged. Current planner is already achieving the maximum official score with comfortable margins; tactical edits would mainly risk regression.
- Recommendation for future rounds while facing `lanity__sivuy`: preserve `robot.py` unless future official logs show actual losses or sharply worse worst-case health; otherwise just re-run `python3 tools/analyze_rounds.py` after new logs.

## Round 1 (current matchup: mountain__neuralbot4-3h) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: opponent `mountain__neuralbot4-3h` was Blue and our bot was Red. We won the round but not perfectly: **245/250**, with 4 Blue wins and 1 tie.
- Bad official seeds from log parsing: tie `sim_36`; Blue wins `sim_52`, `sim_70`, `sim_110`, `sim_127`.
- Opponent source is available at `origin/human/mountain/neuralbot4-3h`; I saved a local copy at `tools/neuralbot4.py` for quick tests.
- Key tweak in `robot.py`: changed `allow_chain_moves` from always `False` to `state.turn >= 20`. This permits black-magic-style queued moves into friendly squares after the opening, but avoids the turn-0/early behavior that previously regressed Red-vs-flail seed 17 when chain moves were enabled unconditionally.
- Validation after edit:
  - `python3 -m py_compile robot.py` passes.
  - As Red vs `tools/neuralbot4.py`, all official bad seeds now win locally: 36, 52, 70, 110, 127.
  - As Blue vs `tools/neuralbot4.py`, `python3 tools/local_eval.py --seeds 36,52,70,110,127 --opponent tools/neuralbot4.py` wins 5/5.
  - Red flail archived bad seeds 17,77,145,225,246 still win; simple-bot sanity seeds 1-2 both sides still win.
- Recommendation: after round 1 logs arrive, re-run `python3 tools/analyze_rounds.py`. If losses remain, inspect exact seeds first. The chain threshold is a tuning knob; unconditional chain fixed neuralbot seed 127 too but lost flail seed 17, while threshold 20 fixed both sampled cases.

## Round 1 (current matchup: ketza__arthur) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: our bot (`gpt-5-5`) was Blue and `ketza__arthur` was Red. We swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Blue 250/250; avg final health/units us 60.4 and 21.8 vs opponent 4.7 and 1.6; minimum our final health 19 with at least 10 units.
- Opponent source is simple tutorial-style focused chasing/adjacent attacking; I saved a local copy as `tools/ketza_arthur.py` for quick tests.
- Sanity checks: `python3 -m py_compile robot.py` passes; `python3 tools/local_eval.py --seeds 1 --opponent builtin-bots/simple-bot.js --both-sides` wins both colors; `python3 tools/local_eval.py --seeds 1-5 --opponent tools/ketza_arthur.py --both-sides` wins 5/5 as Blue and 5/5 as Red.
- Left `robot.py` unchanged. Current coordinated black-magic-style planner (with prior chain-move and late-chase tweaks) already achieves maximum official score with comfortable margins; tactical edits would mostly risk regression.
- Recommendation for future rounds while facing `ketza__arthur`: preserve `robot.py` unless future official logs show losses or sharply worse worst-case health; otherwise re-run `python3 tools/analyze_rounds.py` after logs arrive.

## Round 1 (current matchup: mkap__test) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: opponent `mkap__test` was Blue, our `gpt-5-5` was Red. Score was **242/250** with 7 Blue wins and 1 tie. Bad/tie sims by final state: losses `7,41,67,92,107,122,133`; tie `49`.
- Opponent source is available on branch `origin/human/mkap/test`; I saved a local copy at `tools/mkap_test.py`. It is a simple chaser: leaves spawn on turns divisible by 10, attacks first adjacent enemy in N/E/S/W order, otherwise moves toward nearest enemy.
- Important: local replays with `tools/mkap_test.py` do **not** reproduce official bad seeds because spawn RNG/start layouts differ from archived logs, but current `robot.py` sweeps local sampled seeds 1-20 as Blue and the official bad seed numbers as both colors.
- Tried an enemy attack model matching mkap's first-adjacent attack order. It greatly improved local mkap margins, but regressed sampled Blue-vs-flail seeds 3 and 4, so I did **not** apply it. Current low-health enemy model is safer historically.
- Left `robot.py` unchanged; only added `tools/mkap_test.py` and this note. Recommendation: after round 1 logs arrive, re-run `python3 tools/analyze_rounds.py`. If mkap losses persist, inspect archived bad boards directly; possible targeted idea is better modeling of first-adjacent enemy attacks, but benchmark against flail/neuralbot before submitting.

## Round 1 (current matchup: essickmango__pickle-up) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `essickmango__pickle-up` was Blue and our bot was Red. We won but not perfectly: **207/250**. Official Blue-win sims by final unit/health parsing: `12,15,23,34,40,54,57,66,79,82,86,87,91,93,97,105,107,117,120,124,126,129,134,139,140,142,147,148,155,166,170,171,172,183,190,192,194,214,223,228,238,241,242`.
- Opponent source is available on branch `origin/human/essickmango/pickle-up`; I saved a local copy as `tools/pickle_up.py`. It is a simple chaser that targets `min(enemies)` for movement and, when blocked, attacks/moves toward nearby targets using direction order from relative position.
- Made a conservative `robot.py` change: removed the prior Red-only N/E/S/W enemy attack model that was introduced for `mkap__test`, and restored the lowest-health adjacent enemy attack model for both colors. Local tests against `tools/pickle_up.py` on sampled official-bad seeds `12,15,23,34,40` improved Red from 3/5 (one tie, one loss) to 5/5 wins with much larger margins, while Blue results on those seeds were unchanged (4/5, seed 40 still locally bad as Blue only; official round currently has us Red).
- Validation: `python3 -m py_compile robot.py`; local `tools/pickle_up.py` sampled official-bad seeds `12,15,23,34,40` both sides; seeds `54,57,66` both sides; quick flail/simple-bot seed 1 both sides all ran and won except the noted Blue-vs-pickle seed 40.
- Next teammate: after new official logs arrive, verify whether Red losses drop. If still many losses, inspect the archived bad boards; local seed mapping is only approximate. Potential next ideas: tune against `tools/pickle_up.py` Red side over the listed official-bad seed numbers, but beware regressions in historical flail/neuralbot matchups.

## Round 1 (current matchup: gerenuk__gere-ape) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: our bot was Blue vs Red `gerenuk__gere-ape`; official score was only **193/250** with 45 Red wins and 12 ties. Average still favored us (Blue 56.6 health / 17.7 units vs Red 33.9 / 12.3), but many games ended with Red having more units.
- Opponent source is on `origin/human/gerenuk/gere-ape`; saved a local copy as `tools/gere_ape.py`. It attacks weakest adjacent enemy unless outnumbered or facing a stronger single adjacent enemy, in which case it tries to run to an empty neighbor; otherwise it moves to center/chases weaker enemies with random tie-breaking.
- Edited `robot.py` score tuple to prioritize `health_score` ahead of `surround_score` after unit advantage. This avoids overvaluing contact/surround positions against the opponent's evasive/runaway logic and improved local Blue-vs-`tools/gere_ape.py` from losses/ties on seeds 4-5 to wins; seeds 1-3 also remain wins with better margins.
- Validation: `python3 -m py_compile robot.py`; local `python3 tools/local_eval.py --seeds 1-3 --opponent tools/gere_ape.py` swept as Blue (the 1-5 batch times out, but split tests showed 4-5 wins before applying the same patch); quick simple-bot and flail seed-1 both-sides sanity checks on the candidate also swept.
- Next teammate: after new logs arrive, check whether Blue losses/ties drop. If still bad, inspect official bad seeds (`4,7,10,15,20,26,...`) and consider more exact modeling of the opponent's flee rule, but my first exact-ish enemy model attempt regressed local seeds 1-2 badly, so benchmark carefully.

## Round 2 follow-up (current matchup: gerenuk__gere-ape) - gpt-5-5 note
- New official `/logs/rounds/1/` after the health-before-surround tweak improved but did not solve the matchup: score rose from **193/250** to **209/250** as Blue vs Red `gerenuk__gere-ape`; Red still won 33 sims. `tools/analyze_rounds.py` now shows avg Blue health/units 74.8/21.0 vs Red 41.9/14.0.
- Bad round-1 Red-win sim ids include `6,10,13,14,19,21,22,24,28,66,69,74,91,101,102,116,126,...` (parse `Done! Red won`). The opponent remains evasive/runaway; local seed mapping is imperfect and stochastic because `tools/gere_ape.py` shuffles/random-chooses plans.
- Edited `robot.py` chase term conservatively: late cleanup pressure now starts at turn >=45 (was >=60 and only when unit_score <= 0) and scales up when behind/even late. It is still below unit count and health in the score tuple, so core trade/survival logic remains dominant. This was aimed at not letting the evasive opponent preserve unit-count leads to turn 100.
- Validation: `python3 -m py_compile robot.py`; local Blue vs `tools/gere_ape.py` seeds 1-5 and sampled official-bad numbers 10,101,126 all won after the edit (split batches due 30s timeout). Quick sanity `builtin-bots/flail.js` and `builtin-bots/simple-bot.js` seed 1 both sides also won.
- Tried but did **not** keep: a more exact gere-ape flee/attack enemy model (`/tmp/cand_gere.py`) and a friendly-contact surround penalty (`/tmp/cand_surround.py`). Both had local regressions/ties on sampled gere seeds despite some margin gains.
- Next teammate: after new official logs, check if Red wins drop. If still many, focus on official bad boards and maybe improve endgame/unit-count preservation; beware that local results vs `tools/gere_ape.py` vary between runs.

## Round 1 (current matchup: clay__diag-lattice) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/`: opponent `clay__diag-lattice` was Blue, our `gpt-5-5` was Red, and we swept **250/250**.
- `python3 tools/analyze_rounds.py` summary: visual winners Red 250/250; avg final health/units opponent Blue 31.7/7.3 vs our Red 102.6/31.1. Minimum our final health was 70 with at least 23 units, so the sweep has a large safety margin.
- Ran `python3 -m py_compile robot.py` and quick local simple-bot sanity as both colors; all passed/won.
- Left `robot.py` unchanged. The current coordinated black-magic-style planner is already maxing this official matchup; tactical edits would risk regression with no possible score upside this round.
- Recommendation for future rounds while facing `clay__diag-lattice`: preserve `robot.py` unless future official logs show losses or sharply worse margins; otherwise just rerun `python3 tools/analyze_rounds.py` after new logs.

## Round 2 (current matchup: clay__diag-lattice) - gpt-5-5 note
- Reviewed official `/logs/rounds/0/` and `/logs/rounds/1/`: opponent `clay__diag-lattice` was Blue and our bot was Red in both, and we swept **500/500** total.
- `python3 tools/analyze_rounds.py` summary:
  - Round 0: visual winners Red 250/250; avg final health/units opponent Blue 31.7/7.3 vs our Red 102.6/31.1; minimum our health 70.
  - Round 1: visual winners Red 250/250; avg final health/units opponent Blue 32.5/7.4 vs our Red 102.1/30.9; minimum our health 75.
- Ran `python3 -m py_compile robot.py`; it passes.
- Left `robot.py` unchanged. Current coordinated planner is already maxing this official matchup with very large margins, so tactical edits would add regression risk without possible score upside.
- Recommendation for future rounds while facing `clay__diag-lattice`: preserve `robot.py` unless official logs show actual losses or a sharp margin collapse; otherwise just rerun `python3 tools/analyze_rounds.py` after logs arrive.

## Round 2 follow-up (current matchup: atl15__centerrr) - gpt-5-5 note
- New `/logs/rounds/1/` still has rare Red-side losses vs Blue `atl15__centerrr`: score **248/250**, Blue wins `sim_191` and `sim_228` (round 0 had `sim_247`). All are late unit-count losses despite a midgame health/production advantage.
- Opponent is a center-clumper (`tools/atl15_centerrr.py`) that attacks when walking distance is 1 or 2, otherwise moves toward `(9,9)`. The checked-in enemy model only accounted for adjacent attacks, so it could walk into distance-2 prefire.
- Edited `robot.py` enemy model to include conservative distance-2 prefire prediction: if an enemy has any friend at Manhattan/walking distance 2, model an attack in that direction before movement. Kept the prior global-target movement otherwise; a broader center-move model was not safely tested.
- Validation: `python3 -m py_compile robot.py`; local vs `tools/atl15_centerrr.py` with candidate won sampled seeds `191,228,247` as both colors (notably Blue seed 228 flipped from a local loss to a win), and won Blue seeds `1-3`.
- Next teammate: after new official logs, verify whether the rare `atl15__centerrr` late unit-count losses disappear. If not, inspect the new bad boards; possible next ideas are opponent-specific center-move modeling or stronger late cleanup, but these risk regressions and should be benchmarked.

## Round 2 follow-up (current matchup: jammyliu__sixty-nine-line) - gpt-5-5 note
- Reviewed `/logs/rounds/0/` and `/logs/rounds/1/`: after round 1 we are still winning but not perfectly. Round 0 as Red scored **225/250** (Blue wins listed in prior note), round 1 as Blue scored **216/250** with Red wins `4,13,14,22,75,77,82,84,90,92,101,109,121,130,140,148,176,186,193,196,197,217,219,222,224,241` and 8 ties.
- Opponent copy remains `tools/jammyliu_sixty_nine_line.py`. I replaced the generic/global-target enemy model in `robot.py` with a more exact Jammy model: terrain-adjacent spawn evacuation on clear turns, target the closest walking-distance group, choose the weakest target in that group, prefire at walking distance <=2, otherwise move directly toward the target (including its bug where low-health “retreat” still returns the forward move).
- Local seed mapping still does not reproduce official bad boards, but the exact model improved sampled local Blue bad seed numbers strongly (e.g. seed 13 improved from Health 25-25 Units 8-5 to a much safer win) and kept sampled Red seeds winning. Quick flail sanity seeds 0-1 both sides also swept.
- Validation: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 0-2 --opponent tools/jammyliu_sixty_nine_line.py --both-sides` swept both colors.
- Next teammate: after round 2 logs arrive, check if the exact model improved the official loss/tie count. If it regresses, revert the block in `init_turn` back to the prior generic enemy model (see git diff/README older notes). If losses remain, inspect late unit-count endings; many official bad boards are close endgames with scattered clusters.

## Round 1 (current matchup: mitch84__walk_retreat) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `mitch84__walk_retreat` was Blue and we were Red. Official score was only **152/250** with 81 Blue wins and 17 ties; average final units still favored us (Red 14.8 vs Blue 12.1), but many games were close unit-count endings.
- Saved opponent source from `origin/human/mitch84/walk_retreat` to `tools/mitch_walk_retreat.py`. It retreats to the first blank Direction when more than one enemy is adjacent; otherwise it attacks only adjacent closest enemy, or walks toward closest enemy using larger-axis movement with first-blank fallback.
- Edited `robot.py` enemy model from the previous Jammy-specific range-2 prefire model to this mitch walk/retreat model. Key detail: matching Python `min` tie preservation (no coordinate tie-break) mattered; coordinate tie-break caused local Red ties/losses.
- Validation: `python3 -m py_compile robot.py`; local vs `tools/mitch_walk_retreat.py` seeds 0-2 won as Blue and Red (split commands due timeouts). Sample official-bad seed 10 also now wins locally as both colors. Local seed mapping is imperfect, so inspect new official logs after submission.
- Next teammate: if losses remain, focus on unit-count endgames and the retreat behavior. This opponent only attacks adjacent units, so avoid reintroducing Jammy/atl-style distance-2 prefire unless the matchup changes.

## Round 1 (current matchup: tabaxi3k__black-magic-1) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `tabaxi3k__black-magic-1` was Blue, our bot was Red, and the previous matchup-specific bot was crushed: **1/250 wins, 2 ties**, Blue avg 62.1 health/20.4 units vs Red avg 15.9/6.0.
- Opponent source is `origin/human/tabaxi3k/black-magic-1`; saved a copy as `tools/tabaxi_black_magic_1.js`. It is exactly the public `black-magic.js` one-ply coordinated planner.
- Edited `robot.py` away from the prior mitch walk/retreat-specific model: restored generic adjacent lowest-health enemy attacks, enabled black-magic-style queued/chain moves, restored surround-before-health score order, disabled the late chase term for this mirror, and reversed our greedy friendly iteration order. Reversing unit order is a mirror tie-break that locally turns the black-magic matchup strongly in our favor.
- Validation: `python3 -m py_compile robot.py`; local vs builtin `black-magic.js` seeds 0-2 swept both colors, seeds 3-5 won 2/3 as Blue and 3/3 as Red; local vs copied `tools/tabaxi_black_magic_1.js` seeds 0-2 as Blue swept; simple-bot seed 1 both sides swept.
- Next teammate: after new logs, check whether this recovers the black-magic matchup. If still losing, inspect specific boards; potential knobs are direction order and greedy unit ordering, which have large mirror/tie-break effects. Avoid reintroducing previous opponent-specific chaser models while facing this mirror.

## Round 1 (current matchup: devchris__black_magic) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `devchris__black_magic` was Blue (public black-magic JS) and we were Red. Current score **200/250** with 37 Blue wins and 13 ties per results; parsed sim logs showed 37 Blue wins, many late unit-count losses despite Red average advantage.
- Saved opponent source as `tools/devchris_black_magic.js` (identical to public `builtin-bots/black-magic.js`).
- Edited `robot.py` to plan our friendly actions in both normal public unit order and reversed unit order, then choose whichever full one-ply score is better. Unit order is a major mirror tie-break; this is more adaptive than the previous fixed order and improved local Red-vs-devchris seed 0 from Health 22-61 Units 15-24 to Health 13-43 Units 12-18 (still Red win), while Blue seed 0 also remained a win.
- Validation: `python3 -m py_compile robot.py`; local seed 0 both sides vs `tools/devchris_black_magic.js` won. Runtime is slower (often 11-16s/game locally) but still below match timeout; avoid adding much more expensive search.
- Next teammate: after round 1 logs, check if mirror losses improve. If still many losses, inspect bad boards. Potential knobs: direction ordering and center/chase tie-breaks, but benchmark both colors because mirror tweaks can flip results.

## Round 2 follow-up (current matchup: devchris__black_magic) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: we were Blue vs Red public black-magic and improved from round 0's 200/250 as Red to **214/250**, but still had 22 Red wins and 14 ties. Bad Red-win sims include `15,31,52,78,80,90,97,101,116,122,129,...`.
- Current `robot.py` from round 1 tried both normal and reversed friendly greedy unit order and picked the higher one-ply score. Local tests showed this dual-order selection can choose a bad reversed-order plan on official-bad mirror seeds: seed 101 Blue-vs-black-magic lost 14-16 units with dual-order, while normal public order alone won 20-16.
- Edited `robot.py` to remove the reverse-order second planning pass and use normal public order only. This also reduces runtime materially (~6-8s per local sim instead of sometimes 12-16s). Kept full predicted enemy black-magic action modeling and chain moves.
- Validation: `python3 -m py_compile robot.py`; local Blue vs builtin black-magic official-bad seeds 101,116,122 now all win; seed 0 also wins. Red-side local seed 101 (`builtin-bots/black-magic.js robot.py`) still loses, but round 2 official side should be Blue if sides continue alternating/round 1 was Blue. If next logs are Red-side, reassess order/tie-breaks for Red separately.
- Next teammate: after round 2 logs, compare Blue loss/tie count. If still many losses, inspect specific bad boards; possible next knobs are color-specific iteration order or score tie-breakers, but avoid reintroducing the dual-order selector without proving it helps official-bad seeds.

## Round 2 follow-up (current matchup: mitch84__retreat_walk2) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: the prior survival/chase bot improved from round 0's 0/250 to **110/250**, but still had 114 Red wins and 26 ties while we were Blue.
- Current opponent remains `mitch84__retreat_walk2` (`tools/mitch_retreat_walk2.py`): it only attacks truly adjacent enemies (Euclidean distance 1) and otherwise moves/retreats. This makes it vulnerable to RobotRumble's range-2 directional attacks.
- Edited `robot.py` so that after retreat checks, our units attack the weakest enemy at walking distance <= 2 (prefire/kite) instead of only adjacent enemies. Because attacks are directional and hit after movement, this punishes the opponent's deterministic step-in movement while still preserving the earlier retreat logic.
- Local validation: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 0-9 --opponent tools/mitch_retreat_walk2.py --both-sides` swept 20/20 with much larger margins (Blue avg 56.0/14.9 units vs 8.3/3.4; Red avg 50.7/14.0 vs 9.2/2.9). Blue seeds 10-29 also swept 20/20 before the broader both-sides batch timed out.
- Next teammate: after new official logs, verify whether distance-2 prefire converts the matchup. If official losses remain, inspect those boards; possible issue would be over-prefiring empty squares after enemy retreats, but local results were dramatically better.

## Round 3 follow-up (current matchup: mitch84__retreat_walk2) - gpt-5-5 note
- Reviewed new `/logs/rounds/2/`: the distance-2 prefire change was a huge improvement, raising us to **246/250** as Blue vs Red `mitch84__retreat_walk2`. Remaining non-wins were ties `sim_96`, `sim_179`, `sim_196` and a Red win `sim_219`, all late turn-100 unit-count endings.
- Edited `robot.py` again to make the prefire more precise: for each enemy, predict its next square using the opponent's retreat/walk policy, and prefer attacking that predicted adjacent destination. If no predicted destination is attackable, fall back to the prior current-position range-2 attack. This is intended to catch the opponent as it steps into our attack lane rather than sometimes firing at its old square.
- Local validation: `python3 -m py_compile robot.py`; local Blue vs `tools/mitch_retreat_walk2.py` seeds `0-2` swept with much larger margins than before (avg 94.3 health / 23 units vs 2.7 / 1); official remaining bad seed numbers `96,179,196,219` also swept locally with avg 85 health / 21.5 units vs 1.8 / 0.8. Small both-sides seeds `0-1` swept before the command timeout, and simple-bot seed 1 as Blue still won.
- Next teammate: after new logs, check if this converts the final 4 non-wins. If regressions appear, revert only the `predicted_enemy_coords`/predicted-prefire block to the simpler walking-distance <=2 attack from the previous README note.

## Round 1 (current matchup: mitch84__crw_preempt) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `mitch84__crw_preempt` was Blue, our prior mitch84__retreat_walk2-specific bot was Red, and we only scored **80/250** with 120 Blue wins and 50 ties. Average final state was almost equal (Blue 79.4 health / 16.5 units vs Red 77.2 / 16.0), so many losses are late unit-count/tie-break issues.
- Saved opponent source as `tools/mitch_crw_preempt.py`. It is similar to retreat_walk2 but chooses closest enemy by `(walking_distance, health)` and does range-2 preemptive attacks when the adjacent square is not occupied by its own unit.
- Replaced the pure retreat_walk2 counter with a hybrid based on the prior strong black-magic planner from commit `106a8f8`, plus a wrapper that takes a safe predicted range-1 prefire shot when a crw_preempt-style enemy is about to step adjacent and no enemy is already adjacent. This restores coordinated black-magic movement/trading while still exploiting the opponent's preemptive-walk behavior.
- Local validation is slow but promising: `python3 -m py_compile robot.py`; as Blue vs copied opponent, seed 0 changed from a tie to a win (20-25 units in our favor) and seed 1 won; as Red on seed 0 also won. Avoid adding more search because games can take ~20-28s locally.
- Next teammate: after new official logs, check whether the score improves. If runtime becomes an issue, the hybrid black-magic base is the likely cause. If losses remain, inspect official bad boards; possible knobs are when to override black-magic with predicted prefire and whether to use opponent's exact blocked-prefire rule.

## Round 2 follow-up (current matchup: mitch84__crw_preempt) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: prior hybrid improved from **80/250** to **197/250** as Red vs Blue `mitch84__crw_preempt`, but 42 Blue wins remained, all late unit-count losses (no ties in parsed sims). Avg final units now favor us 20.8 vs 16.3, so the remaining problem is cleanup/survival in close endgames.
- Edited `robot.py` to replace the stale public-black-magic enemy plan seeding with an exact-ish tuple model of `mitch84__crw_preempt` (`predict_mitch_crw_actions`): target closest friend by `(walking_distance, health)`, retreat by Python `Direction` order when outnumbered/overpowered adjacent, prefire at range <=2 unless blocked by own unit, otherwise walk with the opponent's axis/blank-order rules. Kept the outer opportunistic predicted-prefire wrapper.
- Re-enabled the low-priority late chase score starting at turn >=35 to pressure evasive survivors before turn 100. This is matchup-specific; quick flail sanity regressed badly, so if the official opponent changes, revert the mitch-specific enemy model/chase before general play.
- Validation: `python3 -m py_compile robot.py`; local Blue-vs-`tools/mitch_crw_preempt.py` seeds 0,1,2,6,14 all won, with much larger margins on seeds 0/1/14 than before; seed 0 also won as Red. Local seed mapping remains imperfect, but the exact opponent action model is the main new change aimed at official bad seeds.
- Next teammate: after new logs, check if the 42 remaining Blue wins drop. If losses remain, inspect those final boards; possible knobs are stronger endgame chase/unit preservation or making the wrapper prefire condition less conservative.

## Round 1 (current matchup: entropicdrifter__glommer) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `entropicdrifter__glommer` was Blue and we were Red. We won the round but only **137/250**, with 101 Blue wins and 12 ties. Average final units were nearly even (Blue 17.0 vs Red 17.7), so many failures are close unit-count/endgame losses.
- Saved opponent source from `origin/human/entropicdrifter/glommer` to `tools/entropic_glommer.py`. It builds same-team clusters ("gloms") at walking distance <3, retreats from bad adjacent fights, attacks/pushes only when its glom is larger/healthier, otherwise regroups toward allies/center.
- Edited `robot.py` for this matchup: added an exact-ish `predict_glommer_actions` enemy model, switched scoring to health before surround (safer vs evasive retreat logic), and added planned-destination prefire as legal attack candidates so our one-ply planner can shoot squares where glommer units are expected to step/retreat. Also disabled the previous crw_preempt outer robot override by appending a final direct planned-action `robot` function.
- Local validation: `python3 -m py_compile robot.py`; as Red vs `tools/entropic_glommer.py`, seeds 0-4 all won after the predicted-destination prefire change with much larger margins (e.g. seed 1 changed from a local Blue win to Red 118 health / 28 units vs 31 / 9). As Blue, seeds 0-1 also won. Quick flail sanity seed 1 both sides still won.
- Next teammate: after new logs, check whether the glommer loss/tie count drops. If regressions appear, likely revert the planned-destination prefire block or the health-before-surround score order first; local seed mapping is imperfect but the sampled improvement was large.

## Round 2 follow-up (current matchup: entropicdrifter__glommer) - gpt-5-5 note
- Reviewed `/logs/rounds/0/` and new `/logs/rounds/1/`: after the glommer-specific enemy model / health-before-surround / predicted-destination prefire changes, official score improved from **137/250** to a perfect **250/250** as Red vs Blue `entropicdrifter__glommer`.
- `python3 tools/analyze_rounds.py` for round 1: opponent Blue avg final health/units 18.3/6.7 vs our Red 110.5/26.4, with minimum our final health 73 and minimum units 18. This is now a very safe sweep.
- Validation this round: `python3 -m py_compile robot.py`; `python3 tools/local_eval.py --seeds 1 --opponent tools/entropic_glommer.py --both-sides` won both colors.
- Left `robot.py` unchanged. While still facing `entropicdrifter__glommer`, preserve the current matchup-specific bot; further tuning has no score upside and could regress the sweep. If the opponent changes, remember this code is glommer-specialized and may need reverting to a more generic black-magic-style planner from earlier notes/history.

## Round 1 (current matchup: mousetail__coward-bot) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `mousetail__coward-bot` was Blue and our glommer-specific bot was Red. We were crushed: **8/250** with 234 Blue wins and 8 ties. Blue avg final health/units 95.8/26.3 vs our Red 61.9/19.1.
- Saved opponent source from `origin/human/mousetail/coward-bot` to `tools/mousetail_coward_bot.py`. It is a cautious wall/edge-averse bot: retreats from bad adjacent fights, evacuates terrain-adjacent/spawn-adjacent squares, advances toward ally/center when far, and uses range-2 prefire against unscreened targets.
- Edited `robot.py` to replace the glommer enemy model with an exact-ish `predict_coward_actions` model. The coordinated planner now includes attacks on predicted coward-bot move/retreat destinations, which locally flips the matchup from losses to large wins.
- Validation: `python3 -m py_compile robot.py`; local Red vs `tools/mousetail_coward_bot.py` seeds 0-4,10,50,100 all won (e.g. seed 0 changed from Blue 90/28 vs Red 78/25 before edit to Red 68/23 vs Blue 22/6 after edit). Local Blue seeds 0-4 also swept. A quick simple-bot sanity as Red still won; flail as Red is not safe with this matchup-specific code, so revert/tune if the opponent changes.
- Next teammate: after new official logs, check whether Red-side losses collapse. If any remain, inspect late endgames; likely knobs are the score tuple/chase term or making the coward model even closer around its `empty_surrounding_tiles`/edge evacuation rule. If the matchup changes, do not keep this coward-specific enemy model blindly.

## Round 2 follow-up (current matchup: mousetail__coward-bot)
- Reviewed new `/logs/rounds/1/`: the coward-specific predictor improved the matchup dramatically from round 0's **8/250** to **241/250** as Red vs Blue, with 8 remaining Blue wins and 1 tie. Blue-win sims were `24,46,48,69,91,114,117,145`; all were late turn-100 unit-count losses while our average final state strongly favored us (Red avg 60.9 health / 21.4 units vs Blue 21.1 / 6.3).
- Found a small modeling mismatch: Python `Direction` iteration order in the opponent is `[North, South, East, West]`, but its helper `surrounding_tiles` order is South, North, West, East. Updated the coward adjacency/evasion helper counts to use `_COWARD_DIRS=[South,North,West,East]` where appropriate. Local Red-vs-`tools/mousetail_coward_bot.py` sampled bad seed numbers still all won, with slightly better margins on some seeds.
- Added a conservative late all-in cleanup wrapper (`endgame_swarm_action`): from turn >=70, only when we are not ahead on unit count, units directly range-2 focus the weakest enemy or chase the nearest enemy. This is aimed at the official remaining turn-limit unit-count losses and is inactive in the many games where we are already ahead.
- Validation: `python3 -m py_compile robot.py`; local Red vs copied opponent seeds `24,46,48,69,117` all won; quick simple-bot Blue sanity seed 1 still won. Local seed mapping does not reproduce the official losses, so check round 2 logs after submission.
- If future logs still show rare Blue unit-count wins, inspect those final boards; next knobs are moving the all-in trigger earlier/stronger or improving predicted destination attacks. If the opponent changes, remember this bot is heavily coward-specific.

## Round 1 (current matchup: entropicdrifter__glommerv2) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `entropicdrifter__glommerv2` was Red, our prior coward-bot-specific bot was Blue, and we were crushed **17/250**. Red averaged 65.5 health / 24.2 units vs our 45.4 / 11.0.
- Saved opponent source from `origin/human/entropicdrifter/glommerv2` to `tools/entropic_glommerv2.py`. It is an upgraded glom/cluster bot: builds walking-distance<3 gloms, retreats from higher adjacent total threat, lets the biggest glom take center and range-2 attack, avoids spawn late in spawn cycles, and coordinates chain moves.
- Edited `robot.py` to switch the enemy model from `predict_coward_actions` to a new `predict_glommerv2_actions` model matching the above behavior. Kept the existing coordinated one-ply planner, health-before-surround scoring, predicted-destination prefire, and late cleanup wrapper.
- Local validation: `python3 -m py_compile robot.py`; as Blue vs `tools/entropic_glommerv2.py`, seeds 0-4 and official-bad-number seed 21 all won with large margins; as Red seed 0 also won. Simple-bot sanity seed 1 both colors won. Local sims take ~7-14s, so avoid much more search.
- Next teammate: after new logs, check if official losses collapse. If regressions remain, inspect bad boards; likely knobs are exact glommerv2 prediction details (glom target selection/iteration order, coordinated retreat into moving allies) or reverting/adjusting the late all-in cleanup if it causes over-aggression. If opponent changes, remember this bot is glommerv2-specialized.

## Round 2 follow-up (current matchup: entropicdrifter__glommerv2) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: the glommerv2-specific predictor from the prior round converted the matchup from round 0's **17/250** disaster to **246/250** as Red vs Blue `entropicdrifter__glommerv2`.
- Remaining official Blue wins were `sim_6`, `sim_111`, `sim_114`, and `sim_140`. All are late turn-100 unit-count wins for Blue; at turn 70/80/90 our Red side was already at or below Blue unit count, so the existing late `endgame_swarm_action` was active in the relevant phase.
- Local seed mapping does not reproduce these failures: current `robot.py` wins local seed 6 as both Blue and Red vs `tools/entropic_glommerv2.py` with large margins. I tested small endgame-trigger variants in `/tmp`, but they did not show a clear local improvement and risked over-aggression, so I left `robot.py` unchanged.
- Validation: `python3 -m py_compile robot.py` passes; local seed 6 both sides vs the copied opponent wins.
- Recommendation: preserve this glommerv2-specific bot unless new logs show regressions. If targeting the last 4 Red-side non-wins, inspect the official bad boards directly around turns 60-100; likely tuning area is smarter endgame cleanup/focus fire, not the opening predictor.

## Round 1 (current matchup: entropicdrifter__we-are-borg) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `entropicdrifter__we-are-borg` was Blue, our glommerv2-specific bot was Red. We won but not perfectly: **233/250** with 12 Blue wins and 5 ties. Blue wins were `sim_17,50,70,72,100,108,160,175,207,224,239,243`, all turn-100 unit-count wins despite Red usually having more total health.
- Saved opponent source as `tools/entropic_we_are_borg.py`. It is very close to `glommerv2` but has an axis-priority `direction_to`, a smaller spawn list, and retreats to the minimum adjacent-threat blank rather than first blank.
- Tweaked `robot.py` prediction to better match `we-are-borg`: added `borg_direction_to`, `is_borg_spawn`, used min-threat retreat choice, and re-enabled the existing `endgame_swarm_action` final wrapper so from turn >=70 and not ahead on units we focus/chase directly instead of holding formation. Local seed mapping does not reproduce official failures, but sampled local seeds `0,17,50,70,72,100` vs the copied opponent all win (both sides checked for 0,17,50,70).
- Validation: `python3 -m py_compile robot.py`; local eval batches noted above. Sims are slow; use small seed batches.
- Next teammate: after round 1 logs, check if the 12 unit-count losses/ties drop. If regressions appear, first consider reverting the final `robot` override to bypass `endgame_swarm_action`, or reverting the borg-specific predictor edits around `glommer2_retreat_dir`/`borg_direction_to`.

## Round 2 follow-up (current matchup: entropicdrifter__we-are-borg) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: score improved slightly from round 0's **233/250** to **239/250** as Red vs Blue `entropicdrifter__we-are-borg`, but 11 Blue turn-100 unit-count wins remained (`15,37,70,71,77,106,107,129,162,209,239`). No ties were parsed.
- Found a predictor mismatch: the opponent computes `biggest_glom` over **both teams' gloms** during init, while our `predict_glommerv2_actions` always marked the largest enemy glom as the biggest. When one of our clusters is larger than every enemy cluster, this overpredicts enemy center-taking/range-2 defensive behavior. Updated the predictor so `biggest=None` if a friendly glom is the largest overall.
- Also moved the direct cleanup wrapper trigger from turn >=70 to turn >=55. In official bad sim 15 we were already behind in unit count by the low/mid 50s, so waiting until 70 leaves too few turns to catch evasive borg clusters. The wrapper is still only active when our unit count is not ahead.
- Validation: `python3 -m py_compile robot.py`; local vs `tools/entropic_we_are_borg.py` seed 15 both sides swept with much better margins (Blue 85/24 vs 15/5; Red 99/25 vs 13/5). Local Blue seeds 37 and 70 also won after the predictor change. Broader both-side batches are slow and hit the 30s shell timeout, so keep testing in small batches.
- Next teammate: after new logs, check if the remaining Blue unit-count wins drop. If regressions appear, first try reverting only the endgame trigger from 55 back to 70; if predictor behavior seems suspect, inspect bad boards for cases where enemy biggest glom should/shouldn't be active.
- Correction before submit: I reverted the cleanup wrapper trigger back to turn >=70 after testing showed turn >=55 regressed local Red-vs-borg seed 37 into a loss (with trigger 70, seed 37 both sides wins again). The kept code change is the `biggest_glom` predictor fix only.

## Round 1 (current matchup: entropicdrifter__seven-of-nine) - gpt-5-5 note
- Reviewed `/logs/rounds/0/`: opponent `entropicdrifter__seven-of-nine` was Blue and our previous borg/glommerv2-specific bot was Red. We were crushed **1/250** with 247 Blue wins and 2 ties; Blue averaged 53.5 health / 19.8 units vs our Red 29.6 / 7.1.
- Saved opponent source from `origin/human/entropicdrifter/seven-of-nine` to `tools/entropic_seven_of_nine.py`.
- `seven-of-nine` is not the same as the later borg/glommerv2 family we were predicting; it is closer to an older glommer-style bot with a threat map / coordinated retreat. Our existing predictor badly mis-modeled it. With only a few steps left, the safest big improvement was to replace `robot.py` with a copy of `seven-of-nine` itself (mirror strategy). Local same-code mirror tests are close and much better than the prior bot: as Red vs copied opponent, sampled seeds 0-6 were roughly split (Red wins 0,3,4,5; Blue wins 1,2,6 before command timeouts), compared to the prior bot losing seed 0 both sides by large margins.
- Tried quick center/iteration variants but they were not clearly better in the official Red side sample, so kept an exact source copy. This is a matchup-specific emergency recovery, not a general bot.
- Validation: `python3 -m py_compile robot.py tools/entropic_seven_of_nine.py` passes. Future teammate: after new logs, if the mirror still underperforms, tune tie-breaks/color asymmetry in this copied bot (center target, ally iteration order, health sort) or build a predictor for seven's threat-map retreats; do not keep this bot if the opponent changes.

## Round 2 follow-up (current matchup: entropicdrifter__seven-of-nine) - gpt-5-5 note
- Reviewed new `/logs/rounds/1/`: copying/mirroring `seven-of-nine` massively improved round 0's 1/250 disaster to a near-even **112/250** as Blue vs Red, with 106 Red wins and 32 ties. Average final health/units are almost equal (Blue 64.3/20.8 vs Red 63.8/20.7), so the remaining problem is mirror tie-breaking/endgame unit-count edges.
- Local same-code seed mapping remains imperfect and sims are slow (~6-9s each), but small tie-break tests showed changing our ally planning order from weakest-first to strongest-first (`reverse=True` in the health sort) improved sampled Blue mirror seeds: current code lost/tied seeds 2-4, while strongest-first won seeds 2,3,4 and also seed 1; seed 0 regressed, so this is a tie-break gamble rather than a proven sweep.
- Edited `robot.py` accordingly: `allies = sorted(..., reverse=True)`. Kept the center at `(10,10)` from the previous round; other center tweaks were mixed (e.g. `(10,9)` won seeds 0-2 but lost 3-4) and not clearly safer.
- Validation: `python3 -m py_compile robot.py`; local Blue vs `tools/entropic_seven_of_nine.py` seeds 1-4 won with the candidate in split runs; local Red sampled seeds 0-2 were mixed but generally close. If official round 2 regresses, revert only this health-sort change first.

## Round 3 follow-up (current matchup: entropicdrifter__seven-of-nine) - gpt-5-5 note
- Reviewed `/logs/rounds/2/`: the round-2 strongest-first health ordering did **not** improve the mirror; score was **110/250** as Blue vs Red `entropicdrifter__seven-of-nine` (111 Red wins, 29 ties), slightly worse than round 1's 112/250. This remains a near-symmetric mirror/tie-break problem.
- Tested small tie-break variants locally. The best quick candidate was sorting our planned allies by `(health, id)` (weakest first, deterministic id tiebreak), while keeping the previous center `(10,10)`. It improved local Blue mirror seeds 0-2 from current results of loss/win/(not completed in first batch) to three wins, and also won local Red mirror seeds 0-1. Seed 3 was only a tie and seed 5 still lost in a quick sample, so this is not a proven sweep, but it looks safer than the submitted strongest-first order.
- Edited `robot.py`: changed `allies = sorted(allies, key=lambda unit: unit.health, reverse=True)` to `allies = sorted(allies, key=lambda unit: (unit.health, unit.id))`.
- Validation: `python3 -m py_compile robot.py`; local `./rumblebot run term --results-only --seed 0/1/2 robot.py tools/entropic_seven_of_nine.py` all Blue wins; local seeds 0-1 with our bot as Red both Red wins. Sims are slow (~6-9s each), so broad sweeps hit shell timeouts.
- Next teammate: after round 3 logs, compare against round 1/2. If this regresses, revert to the exact copied opponent order (`center = Coords(9,9)`, `allies = sorted(allies, key=lambda unit: unit.health)`) or continue exploring deterministic tie-breaks (center/ally order). This bot is still seven-of-nine-specific and should not be kept for a different opponent without reanalysis.
