# RobotRumble Strategy - Optimized Heuristic Search

We have fixed the core discrepancy in the Python implementation of the `black-magic.js` heuristic search algorithm and added strategic enhancements.

### Current Features & Performance:
1. **Perfect Distance Mechanics**: Re-implemented standard Euclidean distance calculation matching the original JS reference instead of Manhattan walking distance.
2. **Hill Control Integration**: Incorporated central Hill priority into the decision utility function, boosting performance on multiple map types.
3. **Verified Stability**: Consistently outperforms `black-magic.js` and other baseline bots under arbitrary seeds.
