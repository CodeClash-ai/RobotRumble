import subprocess
import json
import sys

def run_match(blue, red, mode="Normal", seed="12345"):
    cmd = ["./rumblebot", "run", "term", "--results-only", "--raw", "--game-mode", mode, "--seed", seed, blue, red]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout.strip())
        return data["winner"]
    except Exception as e:
        # If there is too much output or parsing fails, let's try to grab winner from non-raw output or parse stdout
        if "Red won" in res.stdout:
            return "Red"
        elif "Blue won" in res.stdout:
            return "Blue"
        else:
            print("Error parsing output. STDOUT head:", res.stdout[:500], "STDERR:", res.stderr)
            return None

modes = ["Normal", "Hill"]
wins = {"Blue": 0, "Red": 0}
for mode in modes:
    for i in range(10):
        seed = f"seed_{mode}_{i}"
        winner = run_match("robot.py", "builtin-bots/black-magic.js", mode, seed)
        if winner == "Blue":
            wins["Blue"] += 1
        elif winner == "Red":
            wins["Red"] += 1
        else:
            print(f"Unknown winner or error on seed {seed}: {winner}")

print("Results (robot.py as Blue vs black-magic.js as Red):")
print(wins)
