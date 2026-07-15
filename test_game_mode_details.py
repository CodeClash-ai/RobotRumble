import subprocess
import json

cmd = ["./rumblebot", "run", "term", "robot.py", "robot.py", "--seed", "0", "--raw"]
res = subprocess.run(cmd, capture_output=True, text=True)
data = json.loads(res.stdout)
print("Turns key type:", type(data['turns']))
if len(data['turns']) > 0:
    print("Keys in a turn:", data['turns'][0].keys())
