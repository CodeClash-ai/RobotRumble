#!/bin/bash
# Usage: ./compare_bots.sh <blue_bot> <red_bot> <num_seeds>
BLUE=$1; RED=$2; N=${3:-20}
win=0; loss=0; tie=0
for s in $(seq 1 $N); do
  line=$(timeout 60 ./rumblebot run term "$BLUE" "$RED" --results-only --seed $s 2>&1 | grep "Final state")
  nums=$(echo "$line" | grep -oE '[0-9]+')
  ha=$(echo "$nums" | sed -n '1p'); hb=$(echo "$nums" | sed -n '2p')
  ua=$(echo "$nums" | sed -n '3p'); ub=$(echo "$nums" | sed -n '4p')
  if [ "$ua" -gt "$ub" ]; then win=$((win+1))
  elif [ "$ub" -gt "$ua" ]; then loss=$((loss+1))
  elif [ "$ha" -gt "$hb" ]; then win=$((win+1))
  elif [ "$hb" -gt "$ha" ]; then loss=$((loss+1))
  else tie=$((tie+1)); fi
done
echo "BLUE=$BLUE vs RED=$RED over $N seeds: WIN=$win LOSS=$loss TIE=$tie"
