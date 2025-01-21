from src.definition import *
from src.generate_lps import generate_linear_path_schemas   
from src.reachabilty_lps import is_reachable
from src.utils import convert_json_to_vass
import argparse
import json
import sys
import os

if __name__ == '__main__':
    
    if '--config' not in sys.argv:
        print("Error: --config argument is required")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config', type=str, help='Path to the config file')

    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print(f"Error: The file {args.config} does not exist")
        sys.exit(1)

    with open(args.config, 'r') as file:
        json_data = json.load(file)


    vass, start_state, end_state, start_vector, target_vector = convert_json_to_vass(json_data)
    n_states = len(json_data["states"])
    n_transitions = len(json_data["transitions"])
    max_path_length = 2*n_states*n_transitions    # |p| <= 2*|U|*|E|
    max_cycles = n_transitions                    # |p| <= |E|

    lps_list = generate_linear_path_schemas(vass, start_state, end_state, max_path_length, max_cycles)

    for lps in lps_list:
        reachable, null_space = is_reachable(start_vector, target_vector, lps, False)
        if reachable:
            print(f"Target {target_vector} is reachable")
            exit(0)
    
    print(f"Target {target_vector} is not reachable")