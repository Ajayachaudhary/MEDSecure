def shift_rows(state):
    state[1] = state[1][1:] + state[1][:1]  
    state[2] = state[2][2:] + state[2][:2]  
    state[3] = state[3][3:] + state[3][:3]  
    return state

def inv_shift_rows(state):
    state[1] = state[1][-1:] + state[1][:-1]  
    state[2] = state[2][-2:] + state[2][:-2]  
    state[3] = state[3][-3:] + state[3][:-3]  
    return state
