from src.defintion import *

def convert_json_to_vass(json_data):
    """
    Convert JSON data to a VASS2D instance.
    
    Args:
        json_data (dict): The JSON data containing states, transitions, and vectors.
        
    Returns:
        Tuple[VASS2D, int, int, Vector2D, Vector2D]: The VASS2D instance, start state, end state, 
                                                     initial vector, and final vector.
    """
    states = {}
    for state_id in json_data["states"]:
        # Create transitions for the current state
        transitions = [
            (transition["to"], Vector2D(*transition["vector"]))
            for transition in json_data["transitions"]
            if transition["from"] == state_id
        ]
        states[state_id] = State(state_id, transitions)
    
    vass = VASS2D(states)
    # Extract the start state, end state, initial vector, and final vector from the JSON data
    start_state = json_data["initial_state"]
    end_state = json_data["final_state"]
    start_vector = Vector2D(*json_data["initial_vector"])
    target_vector = Vector2D(*json_data["final_vector"])
    
    return vass, start_state, end_state, start_vector, target_vector

def apply_vectors(pos: Vector2D, vectors: List[Vector2D], debug: bool = True) -> Tuple[bool, Vector2D]:
    """
    Applies a list of vectors to an initial position and checks for negative coordinates.

    Args:
        pos (Vector2D): The initial position.
        vectors (List[Vector2D]): A list of vectors to be applied to the initial position.
        debug (bool, optional): If True, prints debug information. Defaults to True.

    Returns:
        Tuple[bool, Vector2D]: A tuple containing a boolean indicating whether all resulting coordinates 
                               are non-negative and the final position after applying all vectors.
    """

    for i, vec in enumerate(vectors):
        pos = pos + vec
        if debug:
            print(f"After vector {i}: {pos}")
        if pos.x < 0 or pos.y < 0:
            if debug:
                print(f"Negative coordinates after vector {i}: {pos}")
            return False, pos
    return True, pos

def sum_vectors(vectors: List[Vector2D]) -> Vector2D:
    """
    Sums a list of 2D vectors.

    Args:
        vectors (List[Vector2D]): A list of Vector2D objects to be summed.

    Returns:
        Vector2D: The resulting Vector2D object after summing all vectors in the list.
    """
    return sum((vec for vec in vectors), Vector2D(0, 0))


def compute_path_effect(vass: VASS2D, path: List[int]) -> Vector2D:
    """
    Compute the cumulative effect of a given path in a 2D Vector Addition System with States (VASS).

    Args:
        vass (VASS2D): An instance of the VASS2D class representing the vector addition system.
        path (List[int]): A list of integers representing the sequence of states in the path.

    Returns:
        Vector2D: The cumulative effect as a 2D vector resulting from following the given path.
    """
    effect = Vector2D(0, 0)
    for i in range(len(path) - 1):
        current = path[i]
        next_state = path[i + 1]
        for target, vector in vass.get_transitions(current):
            if target == next_state:
                effect = effect + vector
                break
    return effect

def compute_guard(vass: VASS2D, cycle: List[int]) -> Tuple[int, int]:
    """
    Compute the guard values for a given VASS2D and cycle.
    This function calculates the minimum x and y coordinates encountered
    during the traversal of the cycle in the VASS2D. It returns the absolute
    values of these minimum coordinates as a tuple.
    Args:
        vass (VASS2D): The VASS2D object containing the state transitions.
        cycle (List[int]): A list of state indices representing the cycle.
    Returns:
        Tuple[int, int]: A tuple containing the absolute values of the minimum
                         x and y coordinates encountered during the cycle traversal.
    """

    min_x = min_y = 0
    current_x = current_y = 0
    
    for i in range(len(cycle) - 1):
        current = cycle[i]
        next_state = cycle[i + 1]
        for target, vector in vass.get_transitions(current):
            if target == next_state:
                current_x += vector.x
                current_y += vector.y
                min_x = min(min_x, current_x)
                min_y = min(min_y, current_y)
                break
    
    return (abs(min_x), abs(min_y))

def find_simple_paths(vass: VASS2D, start: int, end: int, max_length: int) -> List[List[int]]:
    """
    Find all paths in a 2D VASS (Vector Addition System with States) from a start state to an end state
    with a maximum path length constraint.
    Args:
        vass (VASS2D): The 2D VASS object which contains states and transitions.
        start (int): The starting state.
        end (int): The target end state.
        max_length (int): The maximum allowed length for any path.
    Returns:
        List[List[int]]: A list of paths, where each path is represented as a list of states (integers).
    """

    # Helper DFS function to recursively identify the paths
    def dfs(current: int, path: List[int], visited: Set[int], paths: List[List[int]]):
        if len(path) > max_length+1:
            return
        if current == end:
            paths.append(path[:])
            return
        
        for next_state, _ in vass.get_transitions(current):
            if next_state == current:
                continue
            if next_state not in visited:
                visited.add(next_state)
                path.append(next_state)
                dfs(next_state, path, visited, paths)
                path.pop()
                visited.remove(next_state)
    
    paths = []
    dfs(start, [start], {start}, paths)
    return paths


def find_cycles(vass: VASS2D, state: int) -> List[Loop]:
    """
    Find all cycles in a given VASS2D starting from a specific state.
    This function identifies both self-loops and more complex cycles in the VASS2D.
    It first explicitly adds self-loops and then explores more complex cycles using
    a depth-first search approach.
    Args:
        vass (VASS2D): The VASS2D instance to analyze.
        state (int): The starting state from which to find cycles.
    Returns:
        List[Loop]: A list of Loop objects representing the cycles found in the VASS2D.
    """
    cycles = []
    
    # Add self-loops explicitly
    for next_state, vector in vass.get_transitions(state):
        if next_state == state:
            cycles.append(Loop(
                effect=vector,
                guard=(abs(min(0, vector.x)), abs(min(0, vector.y)))
            ))
    
    # DFS-like function to identify cycles of length > 1
    def find_complex_cycles(current: int, path: List[int], visited: Set[int]):
        for next_state, vector in vass.get_transitions(current):
            if next_state == state:
                # Add non-trivial cycles
                if len(path) > 1:
                    cycle_path = path + [state]
                    effect = compute_path_effect(vass, cycle_path)
                    guard = compute_guard(vass, cycle_path)
                    cycles.append(Loop(effect=effect, guard=guard))
            elif next_state not in visited:
                # Explore further if the state hasn't been visited yet
                visited.add(next_state)
                path.append(next_state)
                find_complex_cycles(next_state, path, visited)
                path.pop()
                visited.remove(next_state)
    
    # Start exploring for complex cycles
    find_complex_cycles(state, [state], {state})
    return cycles

