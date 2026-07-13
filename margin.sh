#!/bin/bash
MY=$1; OPP=$2; N=$3
tot=0
for i in $(seq 1 $N); do
  if [ $((i % 2)) -eq 0 ]; then
    res=$(timeout 60 ./rumblebot run term "$MY" "$OPP" --results-only 2>/dev/null)
    u=$(echo "$res" | grep -oP 'Units \K[0-9]+ [0-9]+')
    a=$(echo "$u" | awk '{print $1}'); b=$(echo "$u" | awk '{print $2}')
    diff=$((a-b))
  else
    res=$(timeout 60 ./rumblebot run term "$OPP" "$MY" --results-only 2>/dev/null)
    u=$(echo "$res" | grep -oP 'Units \K[0-9]+ [0-9]+')
    a=$(echo "$u" | awk '{print $1}'); b=$(echo "$u" | awk '{print $2}')
    diff=$((b-a))
  fi
  tot=$((tot+diff))
  echo "game $i: MY margin $diff"
done
echo "TOTAL MY unit margin over $N games: $tot"
