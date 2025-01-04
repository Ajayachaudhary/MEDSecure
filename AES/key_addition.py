# key_addition.py
def add_round_key(state, round_key):
    if not (all(isinstance(row, list) for row in state) and all(isinstance(row, list) for row in round_key)):
        raise ValueError("state and round_key must be 2D lists (matrices)")

    if not (all(isinstance(val, int) for row in state for val in row) and all(isinstance(val, int) for row in round_key for val in row)):
        raise ValueError("All elements in state and round_key must be integers")

    if len(state) != 4 or len(round_key) != 4 or any(len(row) != 4 for row in state) or any(len(row) != 4 for row in round_key):
        raise ValueError("state and round_key must be 4x4 matrices")


    print("State before AddRoundKey:")
    for row in state:
        print(row)

    print("Round key:")
    for row in round_key:
        print(row)

    return [[state[i][j] ^ round_key[i][j] for j in range(4)] for i in range(4)]
