import json
import subprocess

def run_match():
    cmd = ["./rumblebot", "run", "term", "robot.py", "robot.py", "--results-only", "--raw"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
        return data
    except Exception as e:
        print("Error parsing:", res.stdout, res.stderr)
        return None

results = [run_match() for _ in range(20)]
ties = sum(1 for r in results if r and r.get('winner') == 'Tie')
blue = sum(1 for r in results if r and r.get('winner') == 'Blue')
red = sum(1 for r in results if r and r.get('winner') == 'Red')
print(f"Ties: {ties}, Blue (us): {blue}, Red: {red}")
