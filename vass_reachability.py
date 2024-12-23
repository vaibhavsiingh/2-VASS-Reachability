from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class Vector2D:
    x: int
    y: int
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

@dataclass
class Loop:
    effect: Vector2D
    guard: Tuple[int, int]

@dataclass
class LinearPathScheme:
    prefix_vectors: List[Vector2D]  # Multiple prefix vectors
    loops: List[Loop]
    between_vectors: List[List[Vector2D]]  # List of vector lists between each loop
    suffix_vectors: List[Vector2D]  # Multiple suffix vectors

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

def simulate_path(current: Vector2D, scheme: LinearPathScheme, iterations: List[int], debug: bool = True) -> Tuple[bool, Optional[Vector2D]]:
    """Simulates the path with given iterations and returns if valid and final position"""
    pos = current
    
    if debug:
        print(f"Simulating from position: {pos}")
        print(f"Applying prefix vectors")
    
    # Apply prefix vectors
    
    valid, pos = apply_vectors(pos, scheme.prefix_vectors, debug)
    if not valid:
        return False, None
    
    # Apply each loop and its between vectors
    for i, count in enumerate(iterations):
        # Always apply between vectors for the previous section
        if i > 0 and i - 1 < len(scheme.between_vectors):
            if debug:
                print(f"Applying vectors between loop {i-1} and {i}")
            valid, pos = apply_vectors(pos, scheme.between_vectors[i - 1], debug)
            if not valid:
                return False, None
        
        if count > 0:  # Only check guard and apply loop if we're actually using it
            # Check guard before loop execution
            if pos.x < scheme.loops[i].guard[0] or pos.y < scheme.loops[i].guard[1]:
                if debug:
                    print(f"Failed guard check at loop {i}: pos={pos}, guard={scheme.loops[i].guard}")
                return False, None
                
            # Apply loop effect
            effect = scheme.loops[i].effect * count
            pos = pos + effect
            
            if debug:
                print(f"After loop {i} ({count} times): {pos}")
                
            if pos.x < 0 or pos.y < 0:
                if debug:
                    print(f"Negative coordinates after loop {i}: {pos}")
                return False, None
    
    # Apply the last set of between vectors
    if len(iterations) > 0 and len(iterations) - 1 < len(scheme.between_vectors):
        if debug:
            print(f"Applying vectors between loop {len(iterations)-1} and {len(iterations)}")
        valid, pos = apply_vectors(pos, scheme.between_vectors[len(iterations) - 1], debug)
        if not valid:
            return False, None
    
    # Apply suffix vectors
    if debug:
        print(f"Applying suffix vectors")
    valid, pos = apply_vectors(pos, scheme.suffix_vectors, debug)
    if not valid:
        return False, None
    
    return True, pos

def sum_vectors(vectors: List[Vector2D]) -> Vector2D:
    """Helper function to sum a list of vectors"""
    return sum((vec for vec in vectors), Vector2D(0, 0))

def is_reachable(
    start: Vector2D,
    target: Vector2D,
    scheme: LinearPathScheme,
    debug: bool = True
) -> Tuple[bool, Optional[List[int]]]:
    current = start
    if debug:
        print(f"\nTesting reachability from {start} to {target}")
    
    # Apply prefix vectors
    for vec in scheme.prefix_vectors:
        current = current + vec
        if debug:
            print(f"After prefix vector: {current}")
    
    # All between vectors will be applied regardless of loops
    total_between_effect = Vector2D(0, 0)
    for vectors in scheme.between_vectors:
        total_between_effect = total_between_effect + sum_vectors(vectors)
    
    # Calculate total effect of suffix vectors
    suffix_effect = sum_vectors(scheme.suffix_vectors)
    
    # Add the total fixed effect from between vectors to current position
    current = current + total_between_effect
    
    # Check if we're already at target after prefix and between vectors
    if current + suffix_effect == target:
        return True, [0] * len(scheme.loops)
    
    if current.x < 0 or current.y < 0:
        print(current)
        return False, None
    
    num_loops = len(scheme.loops)
    A = np.zeros((2, num_loops))
    
    # Build coefficient matrix
    for i, loop in enumerate(scheme.loops):
        A[0][i] = loop.effect.x
        A[1][i] = loop.effect.y
    
    # Target vector 
    b = np.array([
        target.x - current.x - suffix_effect.x,
        target.y - current.y - suffix_effect.y
    ])
    try:
        from scipy.optimize import nnls
        x, residual = nnls(A, b)
        if residual < 1e-10:
            iterations = [round(val) for val in x]
            if debug:
                print(f"Proposed iterations: {iterations}")
            
            # Simulate the path to verify
            valid, final_pos = simulate_path(start, scheme, iterations, debug)  # Note: starting from original position
            if not valid:
                print("simulate_path returned invalid")
                return False, None
            
            if debug:
                print(f"Final position: {final_pos}")
            
            # Check if target reached
            if final_pos == target:
                return True, iterations
            
            if debug:
                print(f"Did not reach target. Got {final_pos}, wanted {target}")
    except ImportError:
        print("SciPy not available")
    
    return False, None

def run_tests():
    # Create a scheme with between vectors that should be applied regardless of loops
    scheme = LinearPathScheme(
        prefix_vectors=[Vector2D(1, 0),Vector2D(1, 2)],
        loops=[
            Loop(Vector2D(2, -1), (1, 1)),
            Loop(Vector2D(-1, 2), (0, 2))
        ],
        between_vectors=[
            [Vector2D(0, 1),Vector2D(0, 2)],  # This should be applied even if second loop isn't used
            [Vector2D(1, 0)]   # This should be applied even if no loops are used
        ],
        suffix_vectors=[Vector2D(0, 1)]
    )
    
    # Test Case 1: Using both loops
    print("\n=== Test Case 1: Using both loops ===")
    start = Vector2D(0, 0)
    target = Vector2D(2, 8)
    reachable, iterations = is_reachable(start, target, scheme, False)
    print(f"Target {target} reachable: {reachable}")
    if reachable:
        print(f"Loop iterations required: {iterations}")

    # Test Case 2: Using no loops (should still apply between vectors)
    print("\n=== Test Case 2: No loops, but using between vectors ===")
    target2 = Vector2D(3, 2)  # Should be reachable with just prefix + between + suffix
    reachable, iterations = is_reachable(start, target2, scheme)
    print(f"Target {target2} reachable: {reachable}")
    if reachable:
        print(f"Loop iterations required: {iterations}")

    # Test Case 3: Using first loop only
    print("\n=== Test Case 3: Using first loop only ===")
    target3 = Vector2D(4, 3)
    reachable, iterations = is_reachable(start, target3, scheme)
    print(f"Target {target3} reachable: {reachable}")
    if reachable:
        print(f"Loop iterations required: {iterations}")

run_tests()