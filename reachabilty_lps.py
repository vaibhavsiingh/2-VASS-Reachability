from defintion import *
from scipy.optimize import nnls
from utils import sum_vectors, apply_vectors
import numpy as np


def simulate_path(current: Vector2D, scheme: LinearPathScheme, iterations: List[int], debug: bool = True) -> Tuple[bool, Optional[Vector2D]]:
    """
    Simulates the path of a vector through a series of transformations defined by a LinearPathScheme.
    Args:
        current (Vector2D): The starting position of the vector.
        scheme (LinearPathScheme): The scheme defining the transformations, including prefix, between, and suffix vectors, as well as loop effects and guards.
        iterations (List[int]): A list of integers where each integer represents the number of times to apply the corresponding loop in the scheme.
        debug (bool, optional): If True, prints debug information during the simulation. Defaults to True.
    Returns:
        Tuple[bool, Optional[Vector2D]]: A tuple where the first element is a boolean indicating whether the simulation was successful, and the second element is the final position of the vector if the simulation was successful, otherwise None.
    """

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

def is_reachable(
    start: Vector2D,
    target: Vector2D,
    scheme: LinearPathScheme,
    debug: bool = True
) -> Tuple[bool, Optional[List[int]]]:
    
    """
    Determines if the target position is reachable from the start position using a given linear path scheme.
    """
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
    if debug:
        print(A,b)
    
    try:
        
        x, residual = nnls(A, b)
        if residual < 1e-10:
            iterations = [round(val) for val in x]
            if debug:
                print(f"Proposed iterations: {iterations}")
            
            # Simulate the path to verify
            valid, final_pos = simulate_path(start, scheme, iterations, debug)  # Note: starting from original position
            if not valid:
                if debug:
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