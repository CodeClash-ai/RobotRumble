import json
import os

with open('/logs/rounds/1/results.json') as f:
    r1 = json.load(f)

print("Round 1 Results:")
print(f"Winner: {r1['winner']}")
print(f"Scores: {r1['scores']}")
