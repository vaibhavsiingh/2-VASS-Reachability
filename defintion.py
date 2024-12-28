from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional

@dataclass
class Vector2D:
    x: int
    y: int
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar: int) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other: 'Vector2D') -> bool:
        return self.x == other.x and self.y == other.y

@dataclass
class Loop:
    # 'effect' represents the net change caused by the Loop, and 'guard' specifies the minimum state vector values required to execute the loop
    effect: Vector2D
    guard: Tuple[int, int]

@dataclass
class LinearPathScheme:
    # prefix_vectors are the vectors preceding the first loop, between_vectors[i] contains the vectors between the i-th and (i+1)-th loops (0-indexed), and suffix_vectors are the vectors following the last loop up to the final state
    prefix_vectors: List[Vector2D]  
    loops: List[Loop]
    between_vectors: List[List[Vector2D]]  # List of vector lists between each loop
    suffix_vectors: List[Vector2D]  

@dataclass
class State:
    id: int
    transitions: List[Tuple[int, Vector2D]]  # (target_state_id, vector)

@dataclass
class VASS2D:
    # A dictionary mapping state IDs to their corresponding State objects, which include transition information
    states: Dict[int, State]
    
    def get_transitions(self, state_id: int) -> List[Tuple[int, Vector2D]]:
        return self.states[state_id].transitions if state_id in self.states else []
