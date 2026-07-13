#!/bin/bash
MY=$1; OPP=$2; N=$3
w=0; l=0; t=0
for i in $(seq 1 $N); do
  if [ $((i % 2)) -eq 0 ]; then
    res=$(timeout 60 ./rumblebot run term "$MY" "$OPP" --results-only 2>/dev/null)
    if echo "$res" | grep -q "Blue won"; then w=$((w+1)); elif echo "$res" | grep -q "Red won"; then l=$((l+1)); else t=$((t+1)); fi
  else
    res=$(timeout 60 ./rumblebot run term "$OPP" "$MY" --results-only 2>/dev/null)
    if echo "$res" | grep -q "Red won"; then w=$((w+1)); elif echo "$res" | grep -q "Blue won"; then l=$((l+1)); else t=$((t+1)); fi
  fi
  echo "game $i: $res" | tr '\n' ' '; echo
done
echo "MY wins: $w  OPP wins: $l  ties: $t"
