import subprocess
import json

def run_match(blue, red, seed):
    # Runs a single match using term subcommand
    cmd = ["./rumblebot", "run", "term", blue, red, "--results-only", "--seed", str(seed)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout + "\n" + res.stderr
    winner = "Draw"
    if "Blue won" in out:
        winner = "Blue"
    elif "Red won" in out:
        winner = "Red"
    return winner

# Let's run 20 matches of robot.py vs robot.py with different seeds to see if there is any first/second player advantage
blue_wins = 0
red_wins = 0
for i in range(20):
    w = run_match("robot.py", "robot.py", i)
    if w == "Blue":
        blue_wins += 1
    elif w == "Red":
        red_wins += 1

print(f"Self-play: Blue wins: {blue_wins}, Red wins: {red_wins}")
