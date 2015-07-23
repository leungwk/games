## for uncategoried functions

import copy

def one_ply_lookahead_terminal(state, player):
    """Check if, in one move, player reaches a terminal state.

    Meant to encode "obviousness", or "common sense".
    """
    moves = state.get_moves(player)
    for move in moves:
        new_state = copy.deepcopy(state)
        new_state.do_move(move)
        if new_state.terminal(player):
            return move
    return None
