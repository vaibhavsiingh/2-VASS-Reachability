from src.defintion import *
from scipy.optimize import nnls
from scipy import linalg
from src.utils import sum_vectors, apply_vectors
import numpy as np


def find_solution_space_basis(A: np.ndarray, b: np.ndarray, debug: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find a basis for the complete solution space of Ax = b.
    
    Args:
        A: The coefficient matrix (2 x n)
        b: The target vector (2 x 1)
        debug: Whether to print debug information
    
    Returns:
        Tuple of (particular_solution, solution_space_basis)
        where solution_space_basis contains basis vectors spanning the solution space
    """
    
    # Find particular solution using least squares
    particular_solution, residual = nnls(A, b)
    
    if debug:
        print(f"Particular solution: {particular_solution}")
        print(f"Residual: {residual}")
    
    null_space = linalg.null_space(A)
    
    if debug:
        print(f"Null space basis:\n{null_space}")
    
    # The complete solution space is: particular_solution + span(null_space)
    return particular_solution, null_space

def generate_solution_candidates(
    particular_solution: np.ndarray,
    basis_vectors: np.ndarray,
    max_coefficient: int = 5,
    debug: bool = True
) -> List[np.ndarray]:
    """
    Generate integer solution candidates by exploring the solution space.
    
    Args:
        particular_solution: A particular solution to Ax = b
        basis_vectors: Basis vectors spanning the solution space
        max_coefficient: Maximum absolute value for coefficients when exploring basis combinations
        debug: Whether to print debug information
    
    Returns:
        List of candidate integer solutions
    """
    solutions = []
    
    rounded_particular = np.round(particular_solution)
    if np.all(rounded_particular >= 0):
        solutions.append(rounded_particular)
    
    if basis_vectors.size == 0:
        return solutions
    
    coefficients = np.arange(-max_coefficient, max_coefficient + 1)
    num_basis = basis_vectors.shape[1]
    
    # For each combination of coefficients
    from itertools import product
    for coeff_combo in product(coefficients, repeat=num_basis):
        # Compute linear combination
        combination = np.zeros_like(particular_solution)
        for i, coeff in enumerate(coeff_combo):
            combination += coeff * basis_vectors[:, i]
        
        # Add to particular solution
        candidate = particular_solution + combination
        
        # Round to integers and check validity
        candidate_int = np.round(candidate)
        
        # Check if all components are non-negative
        if np.all(candidate_int >= 0):
            solutions.append(candidate_int)
            
            if debug:
                print(f"Found valid solution: {candidate_int}")
    
    return solutions


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
    Args:
        start (Vector2D): The starting position.
        target (Vector2D): The target position.
        scheme (LinearPathScheme): The scheme defining the path with prefix, between, and suffix vectors, as well as loops.
        debug (bool, optional): If True, prints debug information. Defaults to True.
    Returns:
        Tuple[bool, Optional[List[int]]]: A tuple where the first element is a boolean indicating if the target is reachable,
                                        and the second element is a list of integers representing the number of iterations
                                        for each loop in the scheme if reachable, otherwise None.
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
    
    num_loops = len(scheme.loops)
    if num_loops == 0:
        if debug:
            print("No loops in scheme")
        valid, final_pos = simulate_path(start,scheme,[],debug)
        if valid and final_pos == target:
            return True,None
        else:
            return False, None

        
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
        print(f"Matrix A shape: {A.shape}")
        print(f"Vector b shape: {b.shape}")
        print(f"Matrix A:\n{A}")
        print(f"Vector b: {b}")
    
    try:
        particular_solution, solution_basis = find_solution_space_basis(A, b, debug)
        
        # Generate candidate solutions
        candidates = generate_solution_candidates(particular_solution, solution_basis, debug=debug)
        
        # Test each candidate
        for candidate in candidates:
            iterations = [int(x) for x in candidate]
            if debug:
                print(f"Testing candidate solution: {iterations}")
            
            valid, final_pos = simulate_path(start, scheme, iterations, debug)
            
            if valid and final_pos == target:
                return True, iterations

    except ImportError:
        print("SciPy not available")
        return [], None
    
    return False, None