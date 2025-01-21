# from src.generate_lps import generate_linear_path_schemas
# from src.definition import State,Vector2D,VASS2D,LinearPathScheme,Loop
# from collections import Counter

# def test_generate_linear_path_schemas():
    
#     vass = VASS2D({
#         0: State(0, [(1, Vector2D(1, 2))]),
#         1: State(1, [(2, Vector2D(3, 4))]),
#         2: State(2, [(0, Vector2D(-1, -2))]),
#     })

#     start=0
#     end=2
#     max_path_length=3
#     max_cycles=3
#     lps = generate_linear_path_schemas(vass,start,end,max_path_length,max_cycles)
#     expexted_lps = [
#         LinearPathScheme(
#             prefix_vectors=[],
#             loops=[
#                 Loop(effect=Vector2D(x=1, y=0), guard=(0, 0)),
#                 Loop(effect=Vector2D(x=1, y=0), guard=(0, 2))
#             ],
#             between_vectors=[[Vector2D(x=1, y=2)]],
#             suffix_vectors=[Vector2D(x=3, y=4)]
#         )
#     ]
    

#     assert Counter(lps) == Counter(expexted_lps)