function robot(state, unit) {
  enemies = state.objsByTeam(state.otherTeam)
  // the `_` here is from lodash (https://lodash.com/), a set of nice js functions
  // it's included by default in RR
  closestEnemy = _.minBy(enemies,
    e => e.coords.distanceTo(unit.coords)
  )
  direction = unit.coords.directionTo(closestEnemy.coords)

  if (unit.coords.distanceTo(closestEnemy.coords) === 1) {
    // we're right next to them
    return Action.attack(direction)
  } else {
    return Action.move(direction)
  }
}

