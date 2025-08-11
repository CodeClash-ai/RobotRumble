The complete API reference
==========================

The Standard Library
--------------------

.. class:: Direction(enum)

    .. attribute:: North, South, East, West
    .. attribute:: opposite
        :type: Direction
    .. attribute:: to_coords
        :type: Coords

        Convert to a coordinate pair like ``(1, 0)`` or ``(0, -1)``

    .. attribute:: rotate_cw
        :type: Direction
    .. attribute:: rotate_ccw
        :type: Direction

.. class:: Coords

    .. attribute:: x
        :type: int
    .. attribute:: y
        :type: int

    .. method:: __init__(x: int, y: int)

    .. method:: is_spawn() -> bool
    .. method:: is_hill() -> bool

        Only applies to the "king of the hill" gamemode.
        
    .. method:: distance_to(other: Coords) -> float
    .. method:: walking_distance_to(other: Coords) -> int
    .. method:: direction_to(other: Coords) -> Direction

    .. method:: __add__(other: Union[Coords, Direction]) -> Coords
    .. method:: __sub__(other: Union[Coords, Direction]) -> Coords
    .. method:: __mul__(other: int) -> Coords

        Languages without operator overloading have similarly named functions: ``add``, ``sub``, ``mul``.

.. class:: Team(enum)

    .. attribute:: Red, Blue
    .. attribute:: opposite
        :type: Team

.. class:: ObjType(enum)

    .. attribute:: Unit, Terrain

.. class:: Obj

    Anything that can exist within a grid tile.

    .. attribute:: id
        :type: str
    .. attribute:: coords
        :type: Coords
    .. attribute:: obj_type
        :type: ObjType
    .. attribute:: team
        :type: Optional[Team]
    .. attribute:: health
        :type: Optional[int]

        These are null if this object is not a unit.

.. class:: State

    Root class for all game state.

    .. attribute:: turn
        :type: int
    .. attribute:: our_team
        :type: Team
    .. attribute:: other_team
        :type: Team

    .. method:: obj_by_id(id) -> Optional[Obj]

    .. method:: ids_by_team(team) -> List[str]
    .. method:: objs_by_team(team) -> List[Obj]

    .. method:: id_by_coords(coords) -> Optional[str]
    .. method:: obj_by_coords(coords) -> Optional[Obj]

.. class:: ActionType(enum)

    You should never have to worry about this class if you use the :class:`Action` static methods.

    .. attribute:: Attack, Move

.. class:: Action

    .. method:: __init__(type: ActionType, direction: Direction)

    .. staticmethod:: move(direction: Direction) -> Action
    .. staticmethod:: attack(direction: Direction) -> Action

.. class:: Debug

    A class for debugging through the webapp GUI. Available through the global ``debug`` variable.

    .. method:: inspect(key: str, val: Any) -> None

        Calling this function with a key value pair will create a robot-specific information table. You can inspect it by selecting robots in the map.

    .. method:: locate(unit: Obj) -> None

        Highlight a unit in the map. Useful for locating a specific robot (whether ally or enemy).

.. data:: MAP_SIZE
    :type: int

.. data:: SPAWN_COORDS
    :type: Set[Coords]

.. data:: HILL_COORDS
    :type: Set[Coords]

        Only applies to the "king of the hill" gamemode.

User-defined functions
----------------------


.. function:: robot(state: State, unit: Obj) -> Action

    The main robot function. You must define it.

    :param State state: The State instance for this battle.
    :param Obj unit: The Obj instance for this specific unit.
    :return: An action, obtained using one of the static methods of the :class:`Action` class.

.. function:: init_turn(state: State) -> None

    An optional initialization function called at the beginning of every turn. Use it to initialize global state.

Python Details
--------------
 - Stdlib source here__.

__ https://github.com/robot-rumble/logic/blob/master/lang-runners/python/stdlib/rumblelib.py

 - You can ``import`` most of the Python standard library modules.

 - Install the robot-rumble-stdlib__ package to get autocompletion for your robot. Just put ``from rumblelib import *`` at the top of your file. `example <https://github.com/robot-rumble/lang-support/blob/master/python/typed.py>`_

__ https://pypi.org/project/robot-rumble-stdlib/

 - Implemented with the RustPython__ project.

__ https://github.com/RustPython/RustPython

Javascript Details
------------------
 - Stdlib source here__. Every identifier is in camelCase.

__ https://github.com/robot-rumble/logic/blob/master/lang-runners/javascript/stdlib.js

 - Javascript "enums" are implemented using the method proposed by 2ality__. In a nutshell, this method leverages static class members to create a Java-like Enum superclass. In practice, the result should feel no different from the Python enums.

__ https://2ality.com/2020/01/enum-pattern.html

 - ``console.log`` is the only available ``console`` method.

 - You cannot use ``import``/``require``.

 - Lodash__ is available under the global ``_`` variable. Every module is available but ``String``.

__ https://lodash.com/docs/4.17.15

 - There isn't yet a package with typescript types on npm, but in the meantime you can use this__ great boilerplate.

__ https://github.com/tylermenezes/robot-rumble-ts-starter/

 - Implemented with the QuickJS__ project.

__ https://bellard.org/quickjs/

