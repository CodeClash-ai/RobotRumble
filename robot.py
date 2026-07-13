from typing import *
DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]
planned={}; enemy_set=set(); ally_set=set(); next_turn_spawn=False; focus_id=None
def rE(s): return s.objs_by_team(s.other_team)
def rA(s): return s.objs_by_team(s.our_team)
def init_turn(state):
    global planned,enemy_set,ally_set,next_turn_spawn,focus_id
    planned={}; next_turn_spawn=((state.turn+1)%10)==0
    E=rE(state); A=rA(state)
    enemy_set=set((e.coords.x,e.coords.y) for e in E)
    ally_set=set((a.coords.x,a.coords.y) for a in A)
    focus_id=None
    if E and A:
        def sc(e): return (e.health, min(a.coords.walking_distance_to(e.coords) for a in A))
        focus_id=min(E,key=sc).id
def inb(c): return 0<=c.x<MAP_SIZE and 0<=c.y<MAP_SIZE
def free(s,c):
    if not inb(c) or s.obj_by_coords(c) is not None or planned.get((c.x,c.y)): return False
    if next_turn_spawn and c.is_spawn(): return False
    return True
def adjE(s,c):
    r=[]
    for d in DIRECTIONS:
        o=s.obj_by_coords(c+d)
        if o is not None and o.obj_type==ObjType.Unit and o.team==s.other_team: r.append((d,o))
    return r
def cE(c): return sum(1 for d in DIRECTIONS if ((c+d).x,(c+d).y) in enemy_set)
def cA(c): return sum(1 for d in DIRECTIONS if ((c+d).x,(c+d).y) in ally_set)
def robot(state,unit):
    E=rE(state)
    if not E: return None
    if next_turn_spawn and unit.coords.is_spawn():
        best=None
        for d in DIRECTIONS:
            nc=unit.coords+d
            if not inb(nc) or nc.is_spawn() or state.obj_by_coords(nc) is not None or planned.get((nc.x,nc.y)): continue
            sc=-cE(nc)+cA(nc)
            if best is None or sc>best[0]: best=(sc,d,nc)
        if best: planned[(best[2].x,best[2].y)]=True; return Action.move(best[1])
    adj=adjE(state,unit.coords)
    if adj:
        adj.sort(key=lambda t:(t[1].health,0 if t[1].id==focus_id else 1))
        return Action.attack(adj[0][0])
    tgt=state.obj_by_id(focus_id) if focus_id else None
    nearest=min(E,key=lambda e:unit.coords.walking_distance_to(e.coords))
    if tgt is None: tgt=nearest
    elif nearest.coords.walking_distance_to(unit.coords)+4<tgt.coords.walking_distance_to(unit.coords): tgt=nearest
    best=None
    for d in DIRECTIONS:
        nc=unit.coords+d
        if not free(state,nc): continue
        dist=nc.walking_distance_to(tgt.coords)
        k=(dist,cE(nc)-cA(nc))
        if best is None or k<best[0]: best=(k,d,nc)
    if best: planned[(best[2].x,best[2].y)]=True; return Action.move(best[1])
    return None
