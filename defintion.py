from dataclasses import dataclass
from typing import List, Set, Dict, Tuple, Optional

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
    states: Dict[int, State]
    
    def get_transitions(self, state_id: int) -> List[Tuple[int, Vector2D]]:
        return self.states[state_id].transitions if state_id in self.states else []
