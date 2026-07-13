from typing import *
DIRECTIONS = [Direction.North, Direction.South, Direction.East, Direction.West]
planned={}; enemy_set=set(); ally_set=set(); next_turn_spawn=False; my_home=None; ally_cx=9; ally_cy=9; focus=None
def rE(s): return s.objs_by_team(s.other_team)
def rA(s): return s.objs_by_team(s.our_team)
def init_turn(state):
    global planned,enemy_set,ally_set,next_turn_spawn,my_home,ally_cx,ally_cy,focus
    planned={}; next_turn_spawn=((state.turn+1)%10)==0
    E=rE(state); A=rA(state)
    enemy_set=set((e.coords.x,e.coords.y) for e in E)
    ally_set=set((a.coords.x,a.coords.y) for a in A)
    if A:
        ally_cx=sum(a.coords.x for a in A)/len(A); ally_cy=sum(a.coords.y for a in A)/len(A)
    if my_home is None and A:
        sx=sum(a.coords.x for a in A)//len(A); sy=sum(a.coords.y for a in A)//len(A)
        my_home=Coords(sx,sy)
    focus=None
    if E:
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
    # only attack if it's a favorable trade: this enemy is low, or we have >=2 allies also hitting it
    if adj:
        adj.sort(key=lambda t:(t[1].health,-cA(t[1].coords)))
        d,e=adj[0]
        allies_on=cA(e.coords)
        # attack if enemy weak OR we outnumber locally
        if e.health<=2 or allies_on>=1 or len(adj)==1:
            # retreat if wounded & not securing a kill (preserve unit count)
            not_killing = e.health>1
            if not_killing and ((len(adj)>=2 and unit.health<=3) or (unit.health<=2)):
                rb=None
                for d2 in DIRECTIONS:
                    nc=unit.coords+d2
                    if free(state,nc) and cE(nc)<len(adj):
                        rk=(cE(nc),abs(nc.x-ally_cx)+abs(nc.y-ally_cy))
                        if rb is None or rk<rb[0]: rb=(rk,d2,nc)
                if rb:
                    planned[(rb[2].x,rb[2].y)]=True; return Action.move(rb[1])
            return Action.attack(d)
    # advance cautiously: only step adjacent to enemy if we won't be outnumbered
    tgt=min(E,key=lambda e:unit.coords.walking_distance_to(e.coords))
    if focus is not None and unit.coords.walking_distance_to(focus.coords)<=6: tgt=focus
    best=None
    for d in DIRECTIONS:
        nc=unit.coords+d
        if not free(state,nc): continue
        th=cE(nc); su=cA(nc)
        if th>su+1: continue  # never overextend
        dist=nc.walking_distance_to(tgt.coords)
        cdist=abs(nc.x-ally_cx)+abs(nc.y-ally_cy)
        best_key=(dist,th-su,cdist,th)
        if best is None or best_key<best[0]: best=(best_key,d,nc)
    if best: planned[(best[2].x,best[2].y)]=True; return Action.move(best[1])
    return None
