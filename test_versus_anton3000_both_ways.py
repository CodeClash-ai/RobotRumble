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

results_1 = [run_match("robot.py", "anton3000.py") for _ in range(10)]
results_2 = [run_match("anton3000.py", "robot.py") for _ in range(10)]

blue_wins_1 = results_1.count("Blue")
red_wins_1 = results_1.count("Red")
ties_1 = results_1.count("Tie")

blue_wins_2 = results_2.count("Blue")
red_wins_2 = results_2.count("Red")
ties_2 = results_2.count("Tie")

print(f"As Blue vs anton3000 (Red): wins: {blue_wins_1}, losses: {red_wins_1}, ties: {ties_1}")
print(f"As Red vs anton3000 (Blue): wins: {red_wins_2}, losses: {blue_wins_2}, ties: {ties_2}")
