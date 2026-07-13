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

results_1 = [run_match("robot.py", "diag_lattice.py") for _ in range(5)]
results_2 = [run_match("diag_lattice.py", "robot.py") for _ in range(5)]

blue_wins_1 = results_1.count("Blue")
red_wins_1 = results_1.count("Red")
ties_1 = results_1.count("Tie")

blue_wins_2 = results_2.count("Blue")
red_wins_2 = results_2.count("Red")
ties_2 = results_2.count("Tie")

print(f"As Blue vs diag_lattice (Red): wins: {blue_wins_1}, losses: {red_wins_1}, ties: {ties_1}")
print(f"As Red vs diag_lattice (Blue): wins: {red_wins_2}, losses: {blue_wins_2}, ties: {ties_2}")
