import subprocess
import json

cmd = ["./rumblebot", "run", "term", "robot.py", "robot.py", "--seed", "0", "--raw"]
res = subprocess.run(cmd, capture_output=True, text=True)
data = json.loads(res.stdout)
for i in range(len(data['turns'])):
    state = data['turns'][i]['state']
    objs = state['objs']
    units = [o for o in objs.values() if o.get('obj_type') == 'Unit']
    print(f"Turn {i}: {len(units)} units")
    if i >= 15:
        break
