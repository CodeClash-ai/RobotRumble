import subprocess
import json

def run_match(blue, red, mode="Normal", seed="12345"):
    cmd = ["./rumblebot", "run", "term", "--results-only", "--raw", "--game-mode", mode, "--seed", seed, blue, red]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout.strip())
        return data["winner"]
    except Exception as e:
        if "Red won" in res.stdout:
            return "Red"
        elif "Blue won" in res.stdout:
            return "Blue"
        else:
            return None

modes = ["Normal", "Hill"]
wins = {"robot_as_blue": 0, "robot_as_red": 0, "black_magic_as_blue": 0, "black_magic_as_red": 0}

for mode in modes:
    for i in range(2): # Just run 2 seeds per mode to keep it fast
        seed = f"seed_{mode}_{i}"
        w1 = run_match("robot.py", "builtin-bots/black-magic.js", mode, seed)
        if w1 == "Blue": wins["robot_as_blue"] += 1
        elif w1 == "Red": wins["black_magic_as_red"] += 1
        
        w2 = run_match("builtin-bots/black-magic.js", "robot.py", mode, seed)
        if w2 == "Blue": wins["black_magic_as_blue"] += 1
        elif w2 == "Red": wins["robot_as_red"] += 1

print("Detailed Results:")
print(wins)
