#!/bin/bash
# Usage: ./psweep.sh <blue_bot> <red_bot> <start> <end>
# Parallel; prints W/L/T (blue perspective, REAL unit-only rule).
BLUE=$1; RED=$2; START=${3:-1}; END=${4:-40}
run_one() {
  s=$1; BLUE=$2; RED=$3
  line=$(timeout 60 ./rumblebot run term "$BLUE" "$RED" --results-only --seed $s 2>&1 | grep "Final state")
  ua=$(echo "$line" | grep -oE '[0-9]+' | sed -n '3p')
  ub=$(echo "$line" | grep -oE '[0-9]+' | sed -n '4p')
  if [ -z "$ua" ] || [ -z "$ub" ]; then echo "ERR $s"; 
  elif [ "$ua" -gt "$ub" ]; then echo "W $s $ua $ub"
  elif [ "$ub" -gt "$ua" ]; then echo "L $s $ua $ub"
  else echo "T $s $ua $ub"; fi
}
export -f run_one
seq $START $END | xargs -P8 -I{} bash -c 'run_one "$@"' _ {} "$BLUE" "$RED" > /tmp/psweep_out.txt 2>&1
w=$(grep -c '^W' /tmp/psweep_out.txt); l=$(grep -c '^L' /tmp/psweep_out.txt); t=$(grep -c '^T' /tmp/psweep_out.txt)
echo "BLUE=$BLUE vs RED=$RED [$START..$END]: W=$w L=$l T=$t"
echo "Losses/Ties:"; grep -E '^[LT]' /tmp/psweep_out.txt | sort -n -k2
