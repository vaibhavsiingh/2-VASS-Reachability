from defintion import *
from generate_lps import generate_linear_path_schemas   
from reachabilty_lps import is_reachable

vass = VASS2D({
        0: State(0, [
            (1, Vector2D(1, 1)),  
            (2, Vector2D(1, 0))   
        ]),
        1: State(1, [
            (1, Vector2D(2, -1)), 
            (2, Vector2D(0, 1)),  
            (3, Vector2D(1, 0))
        ]),
        2: State(2, [
            (2, Vector2D(-1, 2)), 
            (1, Vector2D(1, 0)),  
            (3, Vector2D(0, 1))   
        ]),
        3: State(3, [])
    })

start_state = 0
end_state = 3
start_vector = Vector2D(0,0)
target_vector = Vector2D(11,16)

max_path_length = 5
max_cycles = 3

lps_list = generate_linear_path_schemas(vass, start_state, end_state, max_path_length, max_cycles)

for lps in lps_list:
    reachable, iterations = is_reachable(start_vector, target_vector, lps, False)
    print(f"Target {target_vector} reachable: {reachable}")
    if reachable:
        break