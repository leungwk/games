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


def area_count(state, player):
    """Count the number of cells taken up by player"""
    ## TODO: this might not work generally...
    area_count = 0
    for cell in state._board.values():
        if cell.player == player:
            area_count += 1
    return area_count
