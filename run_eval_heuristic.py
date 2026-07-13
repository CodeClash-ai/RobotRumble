import subprocess

def run_match(blue, red):
    cmd = ["./rumblebot", "run", "term", blue, red, "--results-only"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "Blue won" in res.stdout:
        return "Blue"
    elif "Red won" in res.stdout:
        return "Red"
    else:
        return "Tie"

results_1 = [run_match("robot.py", "builtin-bots/heuristic-bot.js") for _ in range(5)]
results_2 = [run_match("builtin-bots/heuristic-bot.js", "robot.py") for _ in range(5)]

print("robot.py vs heuristic-bot.js:", results_1)
print("heuristic-bot.js vs robot.py:", results_2)
