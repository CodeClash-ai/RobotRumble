// Faithful-ish crw_preempt proxy: cluster + preemptive retreat + preserve HP.
// Units stay near allies (clustered knot), flee from enemies but toward ally
// centroid (so they don't scatter off the board and die alone).
function robot(state, unit) {
  function getObj(x,y){ return state.objByCoords(new Coords(x,y)); }
  function legal(x,y){
    if(x<=0||x>17||y<=0||y>17) return false;
    if(y<=5-x) return false;
    if(y<=x-13) return false;
    if(y>=x+13) return false;
    if(y>=31-x) return false;
    return true;
  }
  var me=unit.coords;
  var enemies=state.objsByTeam(state.otherTeam);
  var friends=state.objsByTeam(state.ourTeam);
  var dirs=[Direction.North,Direction.East,Direction.South,Direction.West];
  function delta(d){
    if(d===Direction.North)return[0,-1];
    if(d===Direction.South)return[0,1];
    if(d===Direction.East)return[1,0];
    return[-1,0];
  }
  // ally centroid (excl self)
  var acx=0,acy=0,n=0;
  for(var i=0;i<friends.length;i++){
    if(friends[i].coords.x===me.x&&friends[i].coords.y===me.y)continue;
    acx+=friends[i].coords.x;acy+=friends[i].coords.y;n++;
  }
  if(n>0){acx/=n;acy/=n;}else{acx=9;acy=9;}
  if(enemies.length===0){
    // gather toward center gently
    var best=null,bs=999;
    for(var i=0;i<dirs.length;i++){
      var dl=delta(dirs[i]);var nx=me.x+dl[0],ny=me.y+dl[1];
      if(!legal(nx,ny)||getObj(nx,ny))continue;
      var sc=Math.abs(nx-9)+Math.abs(ny-9);
      if(sc<bs){bs=sc;best=dirs[i];}
    }
    return best?Action.move(best):null;
  }
  var ce=enemies[0], bd=999;
  for(var i=0;i<enemies.length;i++){
    var d=enemies[i].coords.distanceTo(me);
    if(d<bd){bd=d;ce=enemies[i];}
  }
  // count adjacent allies vs adjacent enemies (local superiority)
  function localSup(x,y){
    var af=0,ae=0;
    for(var i=0;i<friends.length;i++){var c=friends[i].coords;if(Math.abs(c.x-x)+Math.abs(c.y-y)<=1&&!(c.x===me.x&&c.y===me.y))af++;}
    for(var i=0;i<enemies.length;i++){var c=enemies[i].coords;if(Math.abs(c.x-x)+Math.abs(c.y-y)<=1)ae++;}
    return af-ae;
  }
  // adjacent enemy: attack if killable or we have local superiority, else flee
  if(bd===1){
    if(ce.health<=1 || localSup(me.x,me.y)>=1){
      for(var i=0;i<dirs.length;i++){var dl=delta(dirs[i]);if(me.x+dl[0]===ce.coords.x&&me.y+dl[1]===ce.coords.y)return Action.attack(dirs[i]);}
    }
  }
  // preemptive retreat when enemy within 2 and no local advantage:
  // flee AWAY from enemy but TOWARD ally centroid (stay clustered).
  if(bd<=2 && localSup(me.x,me.y)<1){
    var best=null,bs=-1e9;
    for(var i=0;i<dirs.length;i++){
      var dl=delta(dirs[i]);var nx=me.x+dl[0],ny=me.y+dl[1];
      if(!legal(nx,ny)||getObj(nx,ny))continue;
      var away=Math.abs(nx-ce.coords.x)+Math.abs(ny-ce.coords.y);
      var toally=-(Math.abs(nx-acx)+Math.abs(ny-acy));
      var sc=away*2+toally;
      if(sc>bs){bs=sc;best=dirs[i];}
    }
    if(best)return Action.move(best);
  }
  // otherwise stay near allies (cluster) — move toward centroid if far
  var mydist=Math.abs(me.x-acx)+Math.abs(me.y-acy);
  if(mydist>2){
    var best=null,bs=999;
    for(var i=0;i<dirs.length;i++){
      var dl=delta(dirs[i]);var nx=me.x+dl[0],ny=me.y+dl[1];
      if(!legal(nx,ny)||getObj(nx,ny))continue;
      var sc=Math.abs(nx-acx)+Math.abs(ny-acy);
      if(sc<bs){bs=sc;best=dirs[i];}
    }
    if(best)return Action.move(best);
  }
  return null;
}
