import subprocess
import json

def run_match(blue, red, mode="Normal", seed="12345"):
    cmd = ["./rumblebot", "run", "term", "--results-only", "--raw", "--game-mode", mode, "--seed", seed, blue, red]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
        return data["winner"]
    except Exception as e:
        print("Error parsing output:", res.stdout, res.stderr)
        return None

# Let's run a batch of games on different seeds
modes = ["Normal", "Hill"]
wins = {"blue": 0, "red": 0}
for mode in modes:
    for i in range(10):
        seed = f"seed_{mode}_{i}"
        winner = run_match("robot.py", "builtin-bots/black-magic.js", mode, seed)
        if winner == "blue":
            wins["blue"] += 1
        elif winner == "red":
            wins["red"] += 1
        else:
            print(f"Unknown winner or error: {winner}")

print("Results vs black-magic.js:")
print(wins)
