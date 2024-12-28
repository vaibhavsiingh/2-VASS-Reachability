from defintion import *
from utils import find_cycles, find_simple_paths, compute_path_effect


def generate_linear_path_schemas(vass: VASS2D, start: int, end: int, 
                               max_path_length: int, max_cycles: int) -> List[LinearPathScheme]:
    """
    Generate linear path schemas from the given VASS.

    Args:
        vass (VASS2D): The VASS to generate path schemas from.
        start (int): The starting state.
        end (int): The ending state.
        max_path_length (int): The maximum length of paths to consider.
        max_cycles (int): The maximum number of cycles to consider.

    Returns:
        List[LinearPathScheme]: A list of linear path schemas.
    """
    schemas = []
    simple_paths = find_simple_paths(vass,start,end,max_path_length) # list all the paths starting from starting state to ending state

    for path in simple_paths:
        all_cycles = []  # List of (position, cycle) tuples

        for state_idx, state in enumerate(path):
            cycles = find_cycles(vass,state)
            for cycle in cycles:
                    all_cycles.append((state_idx, cycle))

        if len(all_cycles) == 0:
            # If no cycles are found in the path, create a linear path scheme with the path as prefix vectors and no loops.
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
            continue
            

        all_cycles = sorted(all_cycles, key=lambda x: x[0])  # sorting all_cycles w.r.t to their position in the path
        
        # Preparing prefix_vectors
        prefix_vectors = []
        first_cycle_pos = all_cycles[0][0] # first cycle of the path
        for idx in range(first_cycle_pos):
            current_state = path[idx]
            next_state = path[idx + 1]
            for transition in vass.get_transitions(current_state):
                if transition[0] == next_state:
                    prefix_vectors.append(transition[1])
                    break

        # Preparing loops and between vectors
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

        # Preparing suffix_vectors
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