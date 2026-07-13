// strategy: move towards center, attack any adjacent robots encountered along the way

const center = new Coords(MAP_SIZE/2, MAP_SIZE/2)

function robot(state, unit) {
  let moveDir = unit.coords.directionTo(center)
  
  const moveDirs = [Direction.North, Direction.East, Direction.South, Direction.West]
  const attackDir = moveDirs.reduce((acc, dir) => {
    if (acc) return acc
    
    let neighbor = state.objByCoords(unit.coords.add(dir))
    if (neighbor) {
      if (neighbor.objType === ObjType.Unit && neighbor.team !== unit.team) {
        return dir
      }
    }
    
    return undefined
  }, undefined)
  
  if (attackDir) {
    return Action.attack(attackDir)
  }
  
  return Action.move(moveDir)
}
  
