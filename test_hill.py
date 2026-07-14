import subprocess

normal_wins = 0
hill_wins = 0
ties = 0

for seed in range(1, 4):
    # Test Hill mode
    res_hill = subprocess.run(
        ["./rumblebot", "run", "term", "robot.py", "builtin-bots/black-magic.js", "--game-mode", "Hill", "--seed", str(seed), "--results-only"],
        capture_output=True, text=True
    ).stdout
    if "Blue won" in res_hill:
        hill_wins += 1
    elif "it was a tie" in res_hill:
        ties += 1

    # Test Normal mode
    res_norm = subprocess.run(
        ["./rumblebot", "run", "term", "robot.py", "builtin-bots/black-magic.js", "--game-mode", "Normal", "--seed", str(seed), "--results-only"],
        capture_output=True, text=True
    ).stdout
    if "Blue won" in res_norm:
        normal_wins += 1

print(f"Hill wins: {hill_wins}/3")
print(f"Normal wins: {normal_wins}/3")
