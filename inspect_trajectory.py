import json

with open("/logs/edits/gemini-3-5-flash_r1.traj.json") as f:
    data = json.load(f)

# Let's inspect the keys and structure
print("Keys:", data.keys())
if "events" in data:
    print("Num events:", len(data["events"]))
    for i, event in enumerate(data["events"][:10]):
        print(f"Event {i}: {event.get('type')}")
