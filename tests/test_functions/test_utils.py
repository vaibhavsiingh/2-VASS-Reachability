from src.defintion import Vector2D, VASS2D, Loop, State
from src.utils import sum_vectors, convert_json_to_vass, compute_path_effect, compute_guard, find_simple_paths, find_cycles
from collections import Counter

def test_convert_json_to_vass():
    # Test input JSON
    json_data = {
        "states": [0, 1, 2],
        "transitions": [
            {"from": 0, "to": 1, "vector": [1, 2]},
            {"from": 1, "to": 2, "vector": [3, 4]},
            {"from": 2, "to": 0, "vector": [-1, -2]},
        ],
        "initial_state": 0,
        "final_state": 2,
        "initial_vector": [0, 0],
        "final_vector": [5, 6],
    }

    # Expected results
    expected_vass = VASS2D({
        0: State(0, [(1, Vector2D(1, 2))]),
        1: State(1, [(2, Vector2D(3, 4))]),
        2: State(2, [(0, Vector2D(-1, -2))]),
    })
    expected_start_state = 0
    expected_end_state = 2
    expected_start_vector = Vector2D(0, 0)
    expected_target_vector = Vector2D(5, 6)

    # Call the function
    vass, start_state, end_state, start_vector, target_vector = convert_json_to_vass(json_data)

    # Assertions
    assert vass.states == expected_vass.states, "VASS states do not match expected"
    assert start_state == expected_start_state, f"Expected start_state {expected_start_state}, got {start_state}"
    assert end_state == expected_end_state, f"Expected end_state {expected_end_state}, got {end_state}"
    assert start_vector == expected_start_vector, f"Expected start_vector {expected_start_vector}, got {start_vector}"
    assert target_vector == expected_target_vector, f"Expected target_vector {expected_target_vector}, got {target_vector}"


def test_sum_vectors():
    # Test case 1: Empty list of vectors
    vectors = []
    result = sum_vectors(vectors)
    assert result == Vector2D(0, 0), f"Expected Vector2D(0, 0), got {result}"
    
    # Test case 2: Single vector
    vectors = [Vector2D(3, 4)]
    result = sum_vectors(vectors)
    assert result == Vector2D(3, 4), f"Expected Vector2D(3, 4), got {result}"
    
    # Test case 3: Multiple vectors
    vectors = [Vector2D(1, 2), Vector2D(3, 4), Vector2D(-2, -6)]
    result = sum_vectors(vectors)
    assert result == Vector2D(2, 0), f"Expected Vector2D(2, 0), got {result}"
    
    # Test case 4: Negative vectors
    vectors = [Vector2D(-1, -2), Vector2D(-3, -4)]
    result = sum_vectors(vectors)
    assert result == Vector2D(-4, -6), f"Expected Vector2D(-4, -6), got {result}"
    
    # Test case 5: Mixed positive and negative vectors
    vectors = [Vector2D(1, 1), Vector2D(-1, -1)]
    result = sum_vectors(vectors)
    assert result == Vector2D(0, 0), f"Expected Vector2D(0, 0), got {result}"


def test_compute_path_effect():
    # Create a sample VASS2D instance
    vass = VASS2D({
        0: State(0, [(1, Vector2D(1, 2))]),
        1: State(1, [(2, Vector2D(3, 4)), (3, Vector2D(5, 6))]),
        2: State(2, [(3, Vector2D(-2, -3))]),
        3: State(3, []),
    })

    # Test case 1: Simple path
    path = [0, 1, 2, 3]
    expected_effect = Vector2D(1, 2) + Vector2D(3, 4) + Vector2D(-2, -3)
    assert compute_path_effect(vass, path) == expected_effect, f"Test case 1 failed: Expected {expected_effect}, got {compute_path_effect(vass, path)}"

    # Test case 2: Path with no transitions
    path = [3]
    expected_effect = Vector2D(0, 0)
    assert compute_path_effect(vass, path) == expected_effect, f"Test case 2 failed: Expected {expected_effect}, got {compute_path_effect(vass, path)}"

    # Test case 3: Path with an invalid transition
    path = [0, 2]
    expected_effect = Vector2D(0, 0)  # No valid transition between 0 and 2
    assert compute_path_effect(vass, path) == expected_effect, f"Test case 3 failed: Expected {expected_effect}, got {compute_path_effect(vass, path)}"

    # Test case 4: Empty path
    path = []
    expected_effect = Vector2D(0, 0)
    assert compute_path_effect(vass, path) == expected_effect, f"Test case 4 failed: Expected {expected_effect}, got {compute_path_effect(vass, path)}"

    # Test case 5: Single-state path
    path = [1]
    expected_effect = Vector2D(0, 0)
    assert compute_path_effect(vass, path) == expected_effect, f"Test case 5 failed: Expected {expected_effect}, got {compute_path_effect(vass, path)}"


def test_compute_guard():
    # Create a sample VASS2D instance
    vass = VASS2D({
        0: State(0, [(1, Vector2D(3, -1))]),
        1: State(1, [(2, Vector2D(-5, 2)), (0, Vector2D(1, -1)),(1, Vector2D(-3, -1))]),
        2: State(2, [(0, Vector2D(2, -3))]),
    })


    cycle = [0, 1, 2, 0]
    expected_guard = (2, 2)
    assert compute_guard(vass, cycle) == expected_guard, f"Test case 1 failed: Expected {expected_guard}, got {compute_guard(vass, cycle)}"


    cycle = [0, 1, 0]
    expected_guard = (0, 2)  
    assert compute_guard(vass, cycle) == expected_guard, f"Test case 2 failed: Expected {expected_guard}, got {compute_guard(vass, cycle)}"

    # Test case 3: Single-state cycle
    cycle = [1,1]
    expected_guard = (3, 1)  # No transitions occur, so guard is (0, 0)
    assert compute_guard(vass, cycle) == expected_guard, f"Test case 3 failed: Expected {expected_guard}, got {compute_guard(vass, cycle)}"


def test_find_simple_paths():
    # Create a sample VASS2D instance
    vass = VASS2D({
        0: State(0, [(1, Vector2D(1, 0)), (2, Vector2D(2, -1))]),
        1: State(1, [(2, Vector2D(-1, 2)), (3, Vector2D(0, 1))]),
        2: State(2, [(3, Vector2D(3, 0))]),
        3: State(3, [(3, Vector2D(1, -3)), (0, Vector2D(2, -1))])
    })

    # Test case 1: Simple path from 0 to 3
    start, end, max_length = 0, 3, 4
    expected_paths = [[0, 1, 3], [0, 1, 2, 3], [0, 2, 3]]
    result_paths = find_simple_paths(vass, start, end, max_length)
    assert sorted(map(sorted, expected_paths)) == sorted(map(sorted, result_paths)), \
        f"Test case 1 failed: Expected paths {expected_paths} to be in {result_paths}"

    # Test case 2: Path with a smaller max_length constraint
    start, end, max_length = 0, 3, 2
    result_paths = find_simple_paths(vass, start, end, max_length)
    expected_paths = [[0, 2, 3],[0, 1, 3]]
    assert sorted(map(sorted, expected_paths)) == sorted(map(sorted, result_paths)), \
        f"Test case 2 failed: Expected paths {expected_paths} to be in {result_paths}"

    # Test case 3: No path exists
    start, end, max_length = 3, 4, 4
    expected_paths = []
    result_paths = find_simple_paths(vass, start, end, max_length)
    assert sorted(map(sorted, expected_paths)) == sorted(map(sorted, result_paths)), \
        f"Test case 3 failed: Expected paths {expected_paths} to be in {result_paths}"

    # Test case 4: Start and end are the same
    start, end, max_length = 1, 1, 3
    expected_paths = [[1]]
    result_paths = find_simple_paths(vass, start, end, max_length)
    assert sorted(map(sorted, expected_paths)) == sorted(map(sorted, result_paths)), \
        f"Test case 4 failed: Expected paths {expected_paths} to be in {result_paths}"

    # Test case 5: Cycle in the graph but limited by max_length
    vass = VASS2D({
        0: State(0, [(1, Vector2D(1, 0)), (2, Vector2D(2, -1))]),
        1: State(1, [(0, Vector2D(-1, 0)), (3, Vector2D(0, 1))]),
        2: State(2, [(3, Vector2D(3, 0))]),
        3: State(3, [])
    })
    start, end, max_length = 0, 3, 4
    expected_paths = [[0, 1, 3], [0, 2, 3]]
    result_paths = find_simple_paths(vass, start, end, max_length)
    assert sorted(map(sorted, expected_paths)) == sorted(map(sorted, result_paths)), \
        f"Test case 5 failed: Expected {expected_paths}, got {find_simple_paths(vass, start, end, max_length)}"

    start, end, max_length = 0, 3, 6
    expected_paths = [[0, 1, 3], [0, 2, 3]]
    result_paths = find_simple_paths(vass, start, end, max_length)
    assert sorted(map(sorted, expected_paths)) == sorted(map(sorted, result_paths)), \
        f"Test case 6 failed: Expected {expected_paths}, got {find_simple_paths(vass, start, end, max_length)}"


def test_find_cycles():
    # Create a sample VASS2D instance
    vass = VASS2D({
        0: State(0, [(0, Vector2D(1, -1)), (1, Vector2D(2, 3))]),
        1: State(1, [(0, Vector2D(-2, -3)), (2, Vector2D(0, 1))]),
        2: State(2, [(1, Vector2D(1, -1)), (2, Vector2D(0, 0))])
    })

    # Test case 1: Finding cycles starting from state 0
    state = 0
    expected_cycles = [
        Loop(effect=Vector2D(1, -1), guard=(0, 1)),  # Self-loop at state 0
        Loop(effect=Vector2D(0, 0), guard=(0, 0))
    ]
    cycles = find_cycles(vass, state)
    assert len(cycles) == len(expected_cycles), \
        f"Test case 1 failed: Expected {len(expected_cycles)} cycles, got {len(cycles)}"
    assert all(cycles[i].effect == expected_cycles[i].effect and cycles[i].guard == expected_cycles[i].guard 
               for i in range(len(expected_cycles))), \
        f"Test case 1 failed: Expected {expected_cycles}, got {cycles}"

    # Test case 2: Finding cycles starting from state 1
    state = 1
    expected_cycles = [
        Loop(effect=Vector2D(0, 0), guard=(2, 3)),  # Self-loop at state 1
        Loop(effect=Vector2D(1, 0), guard=(0, 0))  # Cycle: 1 -> 0 -> 1
    ]
    cycles = find_cycles(vass, state)
    assert len(cycles) == len(expected_cycles), \
        f"Test case 2 failed: Expected {len(expected_cycles)} cycles, got {len(cycles)}"
    assert all(cycles[i].effect == expected_cycles[i].effect and cycles[i].guard == expected_cycles[i].guard 
               for i in range(len(expected_cycles))), \
        f"Test case 2 failed: Expected {expected_cycles}, got {cycles}"

    # Test case 3: Finding cycles starting from state 2
    state = 2
    expected_cycles = [
        Loop(effect=Vector2D(0, 0), guard=(0, 0)),  # Self-loop at state 2
        Loop(effect=Vector2D(1, 0), guard=(0, 1))  
    ]
    cycles = find_cycles(vass, state)
    assert len(cycles) == len(expected_cycles), \
        f"Test case 3 failed: Expected {len(expected_cycles)} cycles, got {len(cycles)}"
    assert all(cycles[i].effect == expected_cycles[i].effect and cycles[i].guard == expected_cycles[i].guard 
               for i in range(len(expected_cycles))), \
        f"Test case 3 failed: Expected {expected_cycles}, got {cycles}"

    # Test case 4: No cycles
    vass_no_cycles = VASS2D({
        0: State(0, [(1, Vector2D(1, 0))]),
        1: State(1, [(2, Vector2D(0, 1))]),
        2: State(2, [])
    })
    state = 0
    expected_cycles = []
    cycles = find_cycles(vass_no_cycles, state)
    assert len(cycles) == len(expected_cycles), \
        f"Test case 4 failed: Expected {len(expected_cycles)} cycles, got {cycles}"
