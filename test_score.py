import math
from typing import Dict, Tuple

def is_hill_coordinate(x: int, y: int) -> bool:
    return 8 <= x <= 10 and 8 <= y <= 10

def score(friends: Dict[Tuple[int, int], int], enemies: Dict[Tuple[int, int], int]) -> Tuple[float, float, float, float, float]:
    unit_score = len(friends) - len(enemies)

    health_score = 0.0
    for h in friends.values():
        health_score += math.pow(h, 0.5)
    for h in enemies.values():
        health_score -= math.pow(h, 0.5)

    map_score = {}
    for pos in friends:
        map_score[pos] = {"surround": 0, "distance": 0.0}
    for pos in enemies:
        map_score[pos] = {"surround": 0, "distance": 0.0}

    hill_score = 0.0
    for pos in friends:
        if is_hill_coordinate(pos[0], pos[1]):
            hill_score += 1.0
    for pos in enemies:
        if is_hill_coordinate(pos[0], pos[1]):
            hill_score -= 1.0

    for f_pos in friends:
        fx, fy = f_pos
        for e_pos in enemies:
            ex, ey = e_pos
            # Use exact Euclidean distance matching black-magic.js
            d = math.sqrt((fx - ex) ** 2 + (fy - ey) ** 2)
            if d < 1e-9:
                d = 0.1
            d_score = 1.0 / (d ** 2)
            map_score[e_pos]["distance"] += d_score
            map_score[f_pos]["distance"] -= d_score
            
            # Manhattan distance of 1 for surround condition
            manhattan = abs(fx - ex) + abs(fy - ey)
            if manhattan == 1:
                map_score[e_pos]["surround"] += 1
                map_score[f_pos]["surround"] -= 1

    surround_score = 0.0
    distance_score = 0.0
    for x in map_score.values():
        surround_score += math.pow(x["surround"], 2)
        distance_score += math.pow(x["distance"], 2)

    return (unit_score, surround_score, health_score, hill_score, distance_score)

print(score({(1,1): 5}, {(2,1): 5}))
