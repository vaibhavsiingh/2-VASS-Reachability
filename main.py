from defintion import *
from generate_lps import generate_linear_path_schemas   
from reachabilty_lps import is_reachable
from utils import convert_json_to_vass
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
    max_path_length = 5
    max_cycles = 3

    lps_list = generate_linear_path_schemas(vass, start_state, end_state, max_path_length, max_cycles)

    for lps in lps_list:
        print(lps)
        reachable, iterations = is_reachable(start_vector, target_vector, lps, False)
        print(f"Target {target_vector} reachable: {reachable}")
        if reachable:
            break