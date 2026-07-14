#!/usr/bin/env bash
# Paired, color-balanced A/B test between two robot.py *files* (e.g. current
# vs a candidate change) against a fixed opponent bot.
#
# WHY THIS SCRIPT EXISTS (see README_agent.md's "MAJOR FINDING" sections):
# multiple past sessions discovered that a huge chunk of the *outcome* of any
# given (seed, opponent) match is driven by a strong, deterministic Blue/Red
# map-side advantage that is INDEPENDENT of which bot/code is playing which
# color (confirmed via robot.py-vs-itself self-play: one color wins
# decisively on almost every seed tested, regardless of bot identity).
# This means a naive fixed-color seed-sweep (robot.py always Blue) is not a
# valid way to A/B test a code change - you are mostly measuring map luck,
# not code quality.
#
# This script fixes that by testing EACH seed with BOTH color assignments
# for EACH candidate file, and summing a per-seed "combined health margin"
# (our_health_as_blue - their_health_as_blue) + (our_health_as_red -
# their_health_as_red) for that version. Since both versions get the exact
# same treatment (both colors, same seeds, same opponent), the color/map-luck
# term should average out much more fairly when comparing versions A vs B
# than any fixed-color sweep would.
#
# Usage:
#   ./scripts/paired_ab.sh <version_A.py> <version_B.py> <opponent.js> <num_seeds> [start_seed]
#
# Example:
#   ./scripts/paired_ab.sh robot.py robot_candidate.py builtin-bots/black-magic.js 10 100
#
# Notes:
# - Each match ~9-30s locally; this does 4 matches per seed (A-as-blue,
#   A-as-red, B-as-blue, B-as-red), so budget ~4x(num_seeds) matches worth of
#   wall time. ALWAYS background this (nohup ... & + sleep + cat), per every
#   prior session's notes about this environment's tool-call time cap.
# - Health parsing assumes the same "Final state: Health H1 H2 Units U1 U2"
#   output format `rumblebot run term --results-only` currently uses (H1/U1
#   correspond to whichever bot was passed as the FIRST cli arg = Blue).
set -u
VERSION_A="${1:?usage: paired_ab.sh <version_A.py> <version_B.py> <opponent.js> <num_seeds> [start_seed]}"
VERSION_B="${2:?usage: paired_ab.sh <version_A.py> <version_B.py> <opponent.js> <num_seeds> [start_seed]}"
OPPONENT="${3:?usage: paired_ab.sh <version_A.py> <version_B.py> <opponent.js> <num_seeds> [start_seed]}"
NUM_SEEDS="${4:?usage: paired_ab.sh <version_A.py> <version_B.py> <opponent.js> <num_seeds> [start_seed]}"
START_SEED="${5:-1}"

cd "$(dirname "$0")/.."

# Parses "Final state: Health H1 H2 Units U1 U2" from stdin, prints "H1 H2".
parse_health() {
  grep -oE 'Final state: Health [0-9]+ [0-9]+' | awk '{print $4, $5}'
}

# run_one <ours> <opponent> <seed> <color> -> prints "our_health their_health"
run_one() {
  local ours="$1" opp="$2" seed="$3" color="$4"
  local out
  if [ "$color" = "red" ]; then
    out=$(timeout 60 ./rumblebot run term --results-only --seed "$seed" "$opp" "$ours" 2>&1)
    echo "$out" | parse_health | awk '{print $2, $1}'
  else
    out=$(timeout 60 ./rumblebot run term --results-only --seed "$seed" "$ours" "$opp" 2>&1)
    echo "$out" | parse_health | awk '{print $1, $2}'
  fi
}

total_margin_a=0
total_margin_b=0

for i in $(seq 0 $((NUM_SEEDS - 1))); do
  seed=$((START_SEED + i))

  read a_blue_us a_blue_them <<< "$(run_one "$VERSION_A" "$OPPONENT" "$seed" blue)"
  read a_red_us a_red_them <<< "$(run_one "$VERSION_A" "$OPPONENT" "$seed" red)"
  read b_blue_us b_blue_them <<< "$(run_one "$VERSION_B" "$OPPONENT" "$seed" blue)"
  read b_red_us b_red_them <<< "$(run_one "$VERSION_B" "$OPPONENT" "$seed" red)"

  margin_a=$(( (a_blue_us - a_blue_them) + (a_red_us - a_red_them) ))
  margin_b=$(( (b_blue_us - b_blue_them) + (b_red_us - b_red_them) ))
  total_margin_a=$((total_margin_a + margin_a))
  total_margin_b=$((total_margin_b + margin_b))

  echo "seed $seed: A margin=$margin_a (blue ${a_blue_us}v${a_blue_them}, red ${a_red_us}v${a_red_them})  |  B margin=$margin_b (blue ${b_blue_us}v${b_blue_them}, red ${b_red_us}v${b_red_them})"
done

echo "=== TOTALS over $NUM_SEEDS seeds (both colors each) ==="
echo "Version A ($VERSION_A) total combined health margin: $total_margin_a"
echo "Version B ($VERSION_B) total combined health margin: $total_margin_b"
if [ "$total_margin_a" -gt "$total_margin_b" ]; then
  echo "-> A looks better on this sample"
elif [ "$total_margin_b" -gt "$total_margin_a" ]; then
  echo "-> B looks better on this sample"
else
  echo "-> tie on this sample"
fi
