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

print("Normal match:", run_match("robot.py", "builtin-bots/black-magic.js", "Normal", "12345"))
