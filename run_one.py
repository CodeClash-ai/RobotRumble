import subprocess
import json

def run_match(blue, red, mode="Hill", seed="12345"):
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

print("Hill match seed_Hill_0:", run_match("robot.py", "builtin-bots/black-magic.js", "Hill", "seed_Hill_0"))
print("Hill match seed_Hill_1:", run_match("robot.py", "builtin-bots/black-magic.js", "Hill", "seed_Hill_1"))
