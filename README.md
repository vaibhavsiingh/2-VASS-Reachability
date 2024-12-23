# Linear Path Scheme Implementation

A Python implementation for determining reachability in a 2D grid using vectors and loops with guard conditions.

## Overview

The Linear Path Scheme implementation provides a framework for analyzing and validating paths in a two-dimensional grid system. The system determines whether specific points are reachable through a combination of fixed vectors and repeatable loop patterns, while maintaining non-negative coordinate constraints and respecting guard conditions.

## Requirements

- Python 3.7+
- NumPy
- SciPy

## Installation

Clone the repository and install the required dependencies:

```bash
pip install numpy scipy
```

## Core Components

### Vector2D

The Vector2D class serves as the foundational building block, representing positions and movements in 2D space. It provides:

- Vector addition and scalar multiplication
- Equality comparison
- String representation
- Coordinate access (x, y)

Example:
```python
vector = Vector2D(1, 2)
result = vector * 3  # Scales the vector
sum_vector = vector + Vector2D(2, 1)  # Adds vectors
```

### Loop

The Loop class represents repeatable movement patterns with guard conditions:

- ```effect```: Vector2D representing movement per iteration
- ```guard```: Tuple(int, int) specifying minimum (x, y) coordinates required

Example:
```python
loop = Loop(Vector2D(2, -1), (1, 1))  # Movement of (2,-1), requires x≥1, y≥1
```

### LinearPathScheme

Combines multiple components into a complete path specification:

```python
scheme = LinearPathScheme(
    prefix_vectors=[Vector2D(1, 0)],
    loops=[Loop(Vector2D(2, -1), (1, 1))],
    between_vectors=[[Vector2D(0, 1)]],
    suffix_vectors=[Vector2D(0, 1)]
)
```

## Core Functions

### Path Simulation

```python
def simulate_path(current: Vector2D, 
                 scheme: LinearPathScheme, 
                 iterations: List[int], 
                 debug: bool = True) -> Tuple[bool, Optional[Vector2D]]
```

Simulates complete path execution:
1. Applies prefix vectors
2. Executes loops with specified iterations
3. Applies between vectors
4. Applies suffix vectors
5. Validates coordinates and guards

### Reachability Check

```python
def is_reachable(start: Vector2D,
                 target: Vector2D,
                 scheme: LinearPathScheme,
                 debug: bool = True) -> Tuple[bool, Optional[List[int]]]
```

Determines if target is reachable and finds required iterations:
1. Calculates fixed vector effects
2. Solves for loop iterations
3. Verifies solution through simulation

## Usage Example

```python
# Create vectors and scheme
scheme = LinearPathScheme(
    prefix_vectors=[Vector2D(1, 0), Vector2D(1, 2)],
    loops=[
        Loop(Vector2D(2, -1), (1, 1)),
        Loop(Vector2D(-1, 2), (0, 2))
    ],
    between_vectors=[
        [Vector2D(0, 1), Vector2D(0, 2)],
        [Vector2D(1, 0)]
    ],
    suffix_vectors=[Vector2D(0, 1)]
)

# Check reachability
start = Vector2D(0, 0)
target = Vector2D(2, 8)
reachable, iterations = is_reachable(start, target, scheme)

print(f"Target reachable: {reachable}")
if reachable:
    print(f"Required iterations: {iterations}")
```

## Testing

Run the built-in test suite:

```python
python vass_reachability.py
```

## Implementation Details

### Non-negative Linear System Solver

The implementation uses SciPy's Non-Negative Least Squares (NNLS) optimizer to:
- Convert reachability into a linear system
- Find minimum non-negative integer solutions
- Optimize loop iterations efficiently

### Validation System

Comprehensive validation includes:
- Non-negative coordinate checking
- Guard condition enforcement
- Solution verification through simulation
- Detailed error reporting

### Debug Support

Debug mode provides:
- Step-by-step execution traces
- Position updates after each vector
- Guard condition validation details
- Solution verification results
