from defintion import *

def apply_vectors(pos: Vector2D, vectors: List[Vector2D], debug: bool = True) -> Tuple[bool, Vector2D]:
    """Apply a list of vectors to a position and check validity"""
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
    """Helper function to sum a list of vectors"""
    return sum((vec for vec in vectors), Vector2D(0, 0))


def compute_path_effect(vass: VASS2D, path: List[int]) -> Vector2D:
    """Compute the total effect vector of a path."""
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
    """Compute the guard for a cycle."""
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
    """Find all simple paths from start to end state with length <= max_length."""
    def dfs(current: int, path: List[int], visited: Set[int], paths: List[List[int]]):
        if len(path) > max_length:
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
    """Find all cycles for a given state, including self-loops."""
    cycles = []
    
    # Add self-loops explicitly
    for next_state, vector in vass.get_transitions(state):
        if next_state == state:
            cycles.append(Loop(
                effect=vector,
                guard=(abs(min(0, vector.x)), abs(min(0, vector.y)))
            ))
    
    def find_complex_cycles(current: int, path: List[int], visited: Set[int]):
        """Recursively find complex cycles."""
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

