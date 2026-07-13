import json
import subprocess

bots = [
    "builtin-bots/simple-bot.js",
    "builtin-bots/chaser.js",
    "builtin-bots/flail.js",
    "builtin-bots/heuristic-bot.js",
    "builtin-bots/needle-bot.js",
    "builtin-bots/random-bot.js",
]

for bot in bots:
    results = []
    for _ in range(1):
        cmd = ["./rumblebot", "run", "term", "robot.py", bot, "--results-only"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if "Blue won" in res.stdout:
            results.append("Blue")
        elif "Red won" in res.stdout:
            results.append("Red")
        else:
            results.append("Tie")
    blue_wins = results.count("Blue")
    red_wins = results.count("Red")
    ties = results.count("Tie")
    print(f"Vs {bot}: Blue(us) wins: {blue_wins}, Red wins: {red_wins}, Ties: {ties}")
