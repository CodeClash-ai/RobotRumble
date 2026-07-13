import subprocess
from concurrent.futures import ThreadPoolExecutor

def run_match(args):
    blue, red = args
    cmd = ["./rumblebot", "run", "term", blue, red, "--results-only"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "Blue won" in res.stdout:
        return "Blue"
    elif "Red won" in res.stdout:
        return "Red"
    else:
        return "Tie"

def eval_pair(blue, red, count=5):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(run_match, [(blue, red)] * count))
    return results

print("Evaluating robot.py vs diag_lattice.py over 25 games:")
res1 = eval_pair("robot.py", "diag_lattice.py", 25)
print("As Blue:", f"Wins: {res1.count('Blue')}, Losses: {res1.count('Red')}, Ties: {res1.count('Tie')}")

res2 = eval_pair("diag_lattice.py", "robot.py", 25)
print("As Red:", f"Wins: {res2.count('Red')}, Losses: {res2.count('Blue')}, Ties: {res2.count('Tie')}")
