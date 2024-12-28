from defintion import *
from utils import find_cycles, find_simple_paths, compute_path_effect


def generate_linear_path_schemas(vass: VASS2D, start: int, end: int, 
                               max_path_length: int, max_cycles: int) -> List[LinearPathScheme]:
    schemas = []

    simple_paths = find_simple_paths(vass,start,end,max_path_length)

    for path in simple_paths:
        all_cycles = []  # List of (position, cycle) tuples
        idx_to_state_map = {}
        for state_idx, state in enumerate(path):
            idx_to_state_map[state_idx] = state
            cycles = find_cycles(vass,state)
            for cycle in cycles:
                    all_cycles.append((state_idx, cycle))

        if len(all_cycles) == 0:
            prefix_vectors = []
            for idx,state in enumerate(path[:-1]):
                for next_state,vector in vass.get_transitions(state):
                    if(next_state == path[idx+1]):
                        prefix_vectors.append(vector)
                        break
            
            schema = LinearPathScheme(
                prefix_vectors=prefix_vectors,
                loops=[],
                between_vectors=[],
                suffix_vectors=[]
            )
            schemas.append(schema)
        
        if len(all_cycles) == 0:
            continue

        all_cycles.sort(key=lambda x: x[0])
        
        prefix_vectors = []
        first_cycle_pos = all_cycles[0][0]
        for idx in range(first_cycle_pos):
            current_state = path[idx]
            next_state = path[idx + 1]
            for transition in vass.get_transitions(current_state):
                if transition[0] == next_state:
                    prefix_vectors.append(transition[1])
                    break

        loops = [cycle for _, cycle in all_cycles]
        between_vectors = []
        for cycle_idx,state_cycle in enumerate(all_cycles[:-1]):
            state_idx, cycle = state_cycle
            next_state_idx, next_cycle = all_cycles[cycle_idx+1]
            if(state_idx == next_state_idx):
                between_vectors.append([])
                continue
            else:
                transitions = []
                upcoming_path = path[state_idx:next_state_idx+1]
                for i,curr_state in enumerate(upcoming_path[:-1]):
                    next_state = upcoming_path[i+1]
                    for neighbooring_state,vector in vass.get_transitions(curr_state):
                        if(neighbooring_state == next_state):
                            transitions.append(vector)
                            break

                between_vectors.append(transitions)

        suffix_vectors = []
        last_cycle_pos = all_cycles[-1][0]
        for idx in range(last_cycle_pos, len(path) - 1):
            current_state = path[idx]
            next_state = path[idx + 1]
            for transition in vass.get_transitions(current_state):
                if transition[0] == next_state:
                    suffix_vectors.append(transition[1])
                    break
        

        schema = LinearPathScheme(
            prefix_vectors=prefix_vectors,
            loops=loops,
            between_vectors=between_vectors,
            suffix_vectors=suffix_vectors
        )
        schemas.append(schema)

    return schemas