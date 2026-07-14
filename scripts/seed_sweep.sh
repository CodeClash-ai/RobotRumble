#!/usr/bin/env bash
# Seed-sweep helper: run robot.py vs a given opponent bot across many seeds
# and report a win/loss/tie tally. Addresses the repeatedly-suggested-but-
# never-written "real win-rate" measurement mentioned in README_agent.md's
# Round 2-5 notes.
#
# Usage:
#   ./scripts/seed_sweep.sh <opponent-bot-path> <num_seeds> [start_seed] [our_color]
#
# Examples:
#   ./scripts/seed_sweep.sh builtin-bots/black-magic.js 10
#   ./scripts/seed_sweep.sh builtin-bots/black-magic.js 10 100 red
#
# Notes:
# - Each match takes ~10-32s locally (see README_agent.md timing notes), and
#   this environment's tool-call wall-clock cap is ~30s, so this script is
#   meant to be run via `nohup ... &` + polling, OR just run directly if your
#   shell/environment allows longer-running foreground commands than the
#   agent tool used to develop this bot did. Example backgrounded usage:
#     nohup ./scripts/seed_sweep.sh builtin-bots/black-magic.js 10 \
#       > /tmp/sweep.log 2>&1 &
#     sleep 250 && cat /tmp/sweep.log
# - "our_color" (optional, default "blue") controls whether robot.py is
#   passed first (Blue) or second (Red) to `rumblebot run term`, since past
#   rounds' notes flagged (then debunked, but worth re-checking if the bot
#   changes) a hypothesis that Blue/Red side mattered.
set -u
OPPONENT="${1:?usage: seed_sweep.sh <opponent-bot-path> <num_seeds> [start_seed] [our_color:blue|red]}"
NUM_SEEDS="${2:?usage: seed_sweep.sh <opponent-bot-path> <num_seeds> [start_seed] [our_color:blue|red]}"
START_SEED="${3:-1}"
OUR_COLOR="${4:-blue}"

wins=0
losses=0
ties=0
errors=0

cd "$(dirname "$0")/.."

for i in $(seq 0 $((NUM_SEEDS - 1))); do
  seed=$((START_SEED + i))
  if [ "$OUR_COLOR" = "red" ]; then
    out=$(timeout 60 ./rumblebot run term --results-only --seed "$seed" "$OPPONENT" robot.py 2>&1)
  else
    out=$(timeout 60 ./rumblebot run term --results-only --seed "$seed" robot.py "$OPPONENT" 2>&1)
  fi
  echo "--- seed $seed ($OUR_COLOR) ---"
  echo "$out"
  if echo "$out" | grep -qi "Blue won"; then
    result="blue"
  elif echo "$out" | grep -qi "Red won"; then
    result="red"
  elif echo "$out" | grep -qi "tie"; then
    result="tie"
  else
    result="error"
  fi

  our_result="unknown"
  if [ "$result" = "tie" ]; then
    our_result="tie"
  elif [ "$result" = "error" ]; then
    our_result="error"
  elif [ "$OUR_COLOR" = "red" ] && [ "$result" = "red" ]; then
    our_result="win"
  elif [ "$OUR_COLOR" = "blue" ] && [ "$result" = "blue" ]; then
    our_result="win"
  else
    our_result="loss"
  fi

  case "$our_result" in
    win) wins=$((wins+1));;
    loss) losses=$((losses+1));;
    tie) ties=$((ties+1));;
    *) errors=$((errors+1));;
  esac
done

echo "==================================="
echo "Opponent: $OPPONENT | our_color=$OUR_COLOR | seeds ${START_SEED}..$((START_SEED+NUM_SEEDS-1))"
echo "Wins: $wins  Losses: $losses  Ties: $ties  Errors: $errors"
