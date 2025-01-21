# 2-VASS Linear Path Schema Generator

This project implements a system for analyzing 2-VASS (Two-Variable Vector Addition Systems with States). It includes tools for generating linear path schemas (LPS), simulating paths, and testing reachability within a 2-VASS system.

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
- [Example Configuration](#example-configuration)
- [Files and Functionality](#files-and-functionality)
  - [`definition.py`](#definitionpy)
  - [`generate_lps.py`](#generate_lpspy)
  - [`main.py`](#mainpy)
  - [`reachability_lps.py`](#reachability_lpspy)
- [Requirements](#requirements)
- [How to Run](#how-to-run)

## Overview

A 2-VASS consists of states, transitions, and 2-dimensional vectors associated with each transition. This project allows you to:

- Define 2-VASS systems using JSON configurations.
- Generate linear path schemas that include prefix vectors, loops, between vectors, and suffix vectors.
- Check whether a target vector is reachable from a given initial state and vector.

## Usage

To analyze a 2-VASS system, follow these steps:
1. Create a JSON configuration file defining the 2-VASS system (see the example below).
2. Use `main.py` with the `--config` flag to specify the configuration file.
3. The program will generate linear path schemas and check reachability for the target vector.

## Example Configuration

Example JSON file `examples/1.json`:

```json
{
    "states": [0, 1, 2, 3],
    "transitions": [
        {"from": 0, "to": 1, "vector": [1, 1]},
        {"from": 0, "to": 2, "vector": [1, 0]},
        {"from": 1, "to": 2, "vector": [0, 1]},
        {"from": 2, "to": 1, "vector": [1, 0]},
        {"from": 2, "to": 2, "vector": [-1, 2]},
        {"from": 1, "to": 1, "vector": [2, -1]},
        {"from": 1, "to": 3, "vector": [1, 0]},
        {"from": 2, "to": 3, "vector": [0, 1]}
    ],
    "initial_state": 0,
    "final_state": 3,
    "initial_vector": [0, 0],
    "final_vector": [11, 16]
}
```
## Files and Functionality
```src/definition.py``` \
Defines core data structures for 2-VASS, such as:

- ```Vector2D```: Represents a 2D vector with operations like addition and scaling.
- ```Loop```: Represents a loop with an effect and guard conditions.
- ```LinearPathScheme```: Stores prefix vectors, loops, between vectors, and suffix vectors.
- ```State``` and ```VASS2D```: Represents states and transitions in a 2-VASS system.

```src/generate_lps.py```\
Implements generate_linear_path_schemas, which:

- Identifies simple paths between the initial and final states.
- Generates LPS for paths with or without cycles.
- Supports multi-loop paths with between and suffix vectors.

```main.py```\
Entry point of the program:

- Reads JSON configuration files.
- Converts the JSON into a 2-VASS structure.
- Generates linear path schemas and checks target vector reachability.

```src/reachability_lps.py```\
Implements is_reachable to:

- Simulate paths based on a given LPS.
- Check if a target vector is reachable using prefix, loop, between, and suffix vectors.
- Uses the nnls function for solving non-negative least squares problems to find loop iterations.

## Requirements
- Python 3.8 or higher
- Required Python libraries:
- ```numpy```
-  ```scipy```
-  ```dataclasses```

## How to Run
- Install the required libraries:

```bash
pip install numpy scipy
```
- Prepare the JSON configuration file.

- Run the program:

```bash
python main.py --config <path to your json file>
```

## Testing
I have created tests for functions in ```utils.py``` in ```tests/test_functions/test_utils.py```. To run the tests, run the following command in home directory
```bash
pytest
```
There are 6 tests in total for 6 different functions. 
