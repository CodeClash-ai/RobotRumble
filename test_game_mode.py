import subprocess
import json

def run_match_get_output(blue, red, seed):
    cmd = ["./rumblebot", "run", "term", blue, red, "--seed", str(seed)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout

print(run_match_get_output("robot.py", "robot.py", 0)[:2000])
