import subprocess
import json

cmd = ["./rumblebot", "run", "term", "robot.py", "robot.py", "--seed", "0", "--raw"]
res = subprocess.run(cmd, capture_output=True, text=True)
data = json.loads(res.stdout)

# Let's count how many turns, winner, scores, and find any units with different types or ActionTypes used
print("Total turns:", len(data['turns']))
print("Winner:", data.get('winner'))
print("Scores:", data.get('scores'))

# Find all action types returned
action_types = set()
for turn in data['turns']:
    actions = turn.get('robot_actions', {})
    for act_dict in actions.values():
        if act_dict and 'Ok' in act_dict and act_dict['Ok']:
            action_types.add(act_dict['Ok'].get('type'))
print("Action types seen in match:", action_types)

# Find all Unit types
unit_types = set()
for turn in data['turns']:
    for obj in turn['state']['objs'].values():
        if obj.get('obj_type') == 'Unit':
            unit_types.add(obj.get('type'))
print("Unit types seen in match:", unit_types)
