#!/bin/bash
# Usage: ./test_bot.sh <mybot> <oppbot> <n>
MY=${1:-robot.py}
OPP=${2:-builtin-bots/black-magic.js}
N=${3:-10}
bwin=0; rwin=0; tie=0
for i in $(seq 1 $N); do
  # alternate colors
  if [ $((i % 2)) -eq 0 ]; then
    res=$(timeout 60 ./rumblebot run term "$MY" "$OPP" --results-only 2>/dev/null | tail -2)
    if echo "$res" | grep -q "Blue won"; then bwin=$((bwin+1));
    elif echo "$res" | grep -q "Red won"; then rwin=$((rwin+1));
    else tie=$((tie+1)); fi
  else
    res=$(timeout 60 ./rumblebot run term "$OPP" "$MY" --results-only 2>/dev/null | tail -2)
    if echo "$res" | grep -q "Red won"; then bwin=$((bwin+1));
    elif echo "$res" | grep -q "Blue won"; then rwin=$((rwin+1));
    else tie=$((tie+1)); fi
  fi
done
echo "MY wins: $bwin  OPP wins: $rwin  ties: $tie  (of $N)"
