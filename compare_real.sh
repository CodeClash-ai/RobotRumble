#!/bin/bash
# Usage: ./compare_real.sh <blue_bot> <red_bot> <num_seeds>
# Uses REAL game tie rule: winner = MORE UNITS ONLY. Health irrelevant.
BLUE=$1; RED=$2; N=${3:-20}
win=0; loss=0; tie=0
for s in $(seq 1 $N); do
  line=$(timeout 60 ./rumblebot run term "$BLUE" "$RED" --results-only --seed $s 2>&1 | grep "Final state")
  nums=$(echo "$line" | grep -oE '[0-9]+')
  ua=$(echo "$nums" | sed -n '3p'); ub=$(echo "$nums" | sed -n '4p')
  if [ "$ua" -gt "$ub" ]; then win=$((win+1))
  elif [ "$ub" -gt "$ua" ]; then loss=$((loss+1))
  else tie=$((tie+1)); fi
done
echo "BLUE=$BLUE vs RED=$RED over $N seeds (REAL rule): WIN(blue)=$win LOSS=$loss TIE=$tie"
