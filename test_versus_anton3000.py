import json
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

# Let's see if we can find anton's bot. He might not be local, but let's test robot.py vs robot.py (which is symmetric) first
results = [run_match("robot.py", "robot.py") for _ in range(20)]
blue_wins = results.count("Blue")
red_wins = results.count("Red")
ties = results.count("Tie")
print(f"Robot vs Robot: Blue: {blue_wins}, Red: {red_wins}, Ties: {ties}")
