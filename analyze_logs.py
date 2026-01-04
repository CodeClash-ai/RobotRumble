#!/usr/bin/env python3
"""
Analyze Robot Rumble game logs to understand performance.
Usage: python analyze_logs.py /logs/rounds/X
"""

import json
import sys
import os
import re

def analyze_round(round_dir):
    """Analyze a single round directory."""
    results_file = os.path.join(round_dir, 'results.json')
    
    if not os.path.exists(results_file):
        print(f"No results.json found in {round_dir}")
        return
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"Round {results['round_num']} Analysis")
    print(f"{'='*60}")
    print(f"\nWinner: {results['winner']}")
    print(f"\nScores:")
    for player, score in results['scores'].items():
        print(f"  {player}: {score}")
    
    print(f"\nDetails:")
    for detail in results['details']:
        print(f"  {detail}")
    
    # Analyze individual simulation files
    sim_files = [f for f in os.listdir(round_dir) if f.startswith('sim_') and f.endswith('.txt')]
    
    if sim_files:
        print(f"\n{'='*60}")
        print(f"Simulation Analysis ({len(sim_files)} games)")
        print(f"{'='*60}")
        
        final_states = []
        for sim_file in sorted(sim_files):
            sim_path = os.path.join(round_dir, sim_file)
            with open(sim_path, 'r') as f:
                content = f.read()
                
            # Extract final state
            if 'Final state:' in content:
                final_line = content.split('Final state:')[-1].strip()
                # Parse "Health X Y Units A B"
                match = re.search(r'Health (\d+) (\d+) Units (\d+) (\d+)', final_line)
                if match:
                    blue_health, red_health, blue_units, red_units = map(int, match.groups())
                    final_states.append({
                        'blue_health': blue_health,
                        'red_health': red_health,
                        'blue_units': blue_units,
                        'red_units': red_units
                    })
        
        if final_states:
            avg_blue_health = sum(s['blue_health'] for s in final_states) / len(final_states)
            avg_red_health = sum(s['red_health'] for s in final_states) / len(final_states)
            avg_blue_units = sum(s['blue_units'] for s in final_states) / len(final_states)
            avg_red_units = sum(s['red_units'] for s in final_states) / len(final_states)
            
            print(f"\nAverage Final Stats:")
            print(f"  Blue: {avg_blue_health:.1f} health, {avg_blue_units:.1f} units")
            print(f"  Red:  {avg_red_health:.1f} health, {avg_red_units:.1f} units")
            
            # Find best and worst games
            blue_margins = [(s['blue_health'] - s['red_health'], i) for i, s in enumerate(final_states)]
            best_game = max(blue_margins, key=lambda x: x[0])
            worst_game = min(blue_margins, key=lambda x: x[0])
            
            print(f"\nBest game for Blue: sim_{best_game[1]}.txt (margin: +{best_game[0]})")
            print(f"Worst game for Blue: sim_{worst_game[1]}.txt (margin: {worst_game[0]:+d})")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python analyze_logs.py /logs/rounds/X")
        sys.exit(1)
    
    round_dir = sys.argv[1]
    analyze_round(round_dir)
