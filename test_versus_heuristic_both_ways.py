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

results_1 = [run_match("robot.py", "builtin-bots/heuristic-bot.js") for _ in range(4)]
results_2 = [run_match("builtin-bots/heuristic-bot.js", "robot.py") for _ in range(4)]

print("robot.py as Blue (us) vs heuristic-bot.js as Red:")
print(f"Wins: {results_1.count('Blue')}, Losses: {results_1.count('Red')}, Ties: {results_1.count('Tie')}")

print("heuristic-bot.js as Blue vs robot.py as Red (us):")
print(f"Wins: {results_2.count('Red')}, Losses: {results_2.count('Blue')}, Ties: {results_2.count('Tie')}")
