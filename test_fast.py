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

builtin_bots = [
    "builtin-bots/simple-bot.js",
    "builtin-bots/chaser.js",
    "builtin-bots/flail.js",
    "builtin-bots/heuristic-bot.js",
    "builtin-bots/needle-bot.js",
    "builtin-bots/random-bot.js",
]

for bot in builtin_bots:
    results = [run_match("robot.py", bot) for _ in range(2)]
    blue_wins = results.count("Blue")
    red_wins = results.count("Red")
    ties = results.count("Tie")
    print(f"Vs {bot}: Blue(us) wins: {blue_wins}, Red wins: {red_wins}, Ties: {ties}")
