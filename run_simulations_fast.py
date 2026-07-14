import subprocess
import json

def run_match(blue, red, mode="Normal", seed="12345"):
    # Run WITHOUT --raw to make it extremely fast and lightweight!
    cmd = ["./rumblebot", "run", "term", "--results-only", "--game-mode", mode, "--seed", seed, blue, red]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "Blue won" in res.stdout or "Done! Blue won" in res.stdout:
        return "Blue"
    elif "Red won" in res.stdout or "Done! Red won" in res.stdout:
        return "Red"
    else:
        # Fallback to stdout parsing
        for line in res.stdout.splitlines():
            if "won" in line:
                if "Blue" in line: return "Blue"
                if "Red" in line: return "Red"
        print("Stdout:", res.stdout)
        return None

modes = ["Normal", "Hill"]
wins = {"Blue": 0, "Red": 0}
for mode in modes:
    for i in range(5): # Let us do 5 matches per mode to keep it well under 10 seconds total
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
