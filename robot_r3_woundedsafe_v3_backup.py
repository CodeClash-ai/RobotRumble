from typing import *
DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]
planned={}; enemy_set=set(); ally_set=set(); next_turn_spawn=False; ally_cx=9; ally_cy=9; focus=None
attackers_on={}
def rE(s): return s.objs_by_team(s.other_team)
def rA(s): return s.objs_by_team(s.our_team)
def init_turn(state):
    global planned,enemy_set,ally_set,next_turn_spawn,ally_cx,ally_cy,focus,attackers_on
    planned={}; next_turn_spawn=((state.turn+1)%10)==0
    E=rE(state); A=rA(state)
    enemy_set=set((e.coords.x,e.coords.y) for e in E)
    ally_set=set((a.coords.x,a.coords.y) for a in A)
    if A:
        ally_cx=sum(a.coords.x for a in A)/len(A); ally_cy=sum(a.coords.y for a in A)/len(A)
    attackers_on={}
    for e in E:
        cnt=0
        for d in DIRECTIONS:
            c=e.coords+d
            if (c.x,c.y) in ally_set: cnt+=1
        attackers_on[(e.coords.x,e.coords.y)]=cnt
    focus=None
    if E:
        # global focus: weakest enemy nearest our centroid (whole team converges)
        focus=min(E,key=lambda e:(e.health,abs(e.coords.x-ally_cx)+abs(e.coords.y-ally_cy)))
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
def cDiag(c): return sum(1 for dx in(-1,1) for dy in(-1,1) if (c.x+dx,c.y+dy) in enemy_set)
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
        def killable(t):
            e=t[1]; ac=attackers_on.get((e.coords.x,e.coords.y),0)
            return ac>=e.health
        adj.sort(key=lambda t:(0 if killable(t) else 1, t[1].health, -attackers_on.get((t[1].coords.x,t[1].coords.y),0)))
        d,e=adj[0]
        ac=attackers_on.get((e.coords.x,e.coords.y),0)
        can_kill = ac>=e.health
        favorable = can_kill or e.health<=2 or ac>=2 or len(adj)==1
        if favorable:
            not_killing = not can_kill and e.health>1
            if (unit.health<=2 and not can_kill) or (not_killing and len(adj)>=2 and unit.health<=3):
                rb=None
                for d2 in DIRECTIONS:
                    nc=unit.coords+d2
                    if free(state,nc) and cE(nc)<len(adj):
                        rk=(cE(nc),abs(nc.x-ally_cx)+abs(nc.y-ally_cy))
                        if rb is None or rk<rb[0]: rb=(rk,d2,nc)
                if rb:
                    planned[(rb[2].x,rb[2].y)]=True; return Action.move(rb[1])
            return Action.attack(d)
    # advance: whole team converges on the global focus (unlimited radius) -> strong concentration
    tgt=focus if focus is not None else min(E,key=lambda e:unit.coords.walking_distance_to(e.coords))
    best=None
    wounded = unit.health<=2
    for d in DIRECTIONS:
        nc=unit.coords+d
        if not free(state,nc): continue
        th=cE(nc); su=cA(nc)
        if th>su+1: continue
        # wounded units must not step where they'd be exposed (they draw fire & die)
        diag=cDiag(nc)
        if wounded and (th+diag)>su: continue
        dist=nc.walking_distance_to(tgt.coords)
        cdist=abs(nc.x-ally_cx)+abs(nc.y-ally_cy)
        # heavily prioritize cohesion (tight clustering) then closing distance
        best_key=(dist,cdist,th,diag,th-su)
        if best is None or best_key<best[0]: best=(best_key,d,nc)
    if best: planned[(best[2].x,best[2].y)]=True; return Action.move(best[1])
    return None
