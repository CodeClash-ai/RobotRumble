# RobotRumble Strategy - Black Magic + Hill Control Heuristics

We have built upon the translated highly optimized Python version (`robot.py`) of the `black-magic.js` heuristic search algorithm.

### Key Improvements Made:
1. **Hill Control Integration**: Added a dedicated `is_hill_coordinate` function and scoring parameter to prioritize control of the central 3x3 hill coordinates.
2. **Refined Heuristic Weight Hierarchy**: Reordered and customized the multi-criterion evaluation return tuple so that tactical board positions and hill dominance are valued higher than basic positioning:
   * **Priority Hierarchy**: `Unit Differential` > `Hill Control` > `Surround Advantage` > `Health` > `Distance Positioning`.
3. **Validation**: Successfully tested against the standard `black-magic.js` baseline in both "Normal" and "Hill" modes, achieving robust and dominant victories across multiple random seeds.
