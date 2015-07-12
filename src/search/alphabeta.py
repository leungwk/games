import copy

def alphabeta(conga, alpha, beta, depth, player, mm, heuristic, invalid_move):
    if conga.terminal(player) or \
       depth == 0:
        return (heuristic(conga, player), invalid_move) # invalid move

    curr_move = invalid_move
    moves = conga.get_moves(player)
    for move in moves:
        new_conga = copy.deepcopy(conga)
        new_conga.do_move(move)
        # self.explore_count += 1

        opponent = conga.opponent(player)
        ret_val, ret_move = alphabeta(
            new_conga, alpha, beta, depth -1, opponent, "max" if mm == "min" else "min", heuristic, invalid_move)
        if mm == "max":
            if ret_val > alpha: # '>=' causes wrong move to be selected (and it should update only on improvements)
                curr_move = move
            alpha = max(alpha, ret_val)
            if alpha >= beta: # value of adversery has now been exceeded, so no need to search further
                # self.prune_count += len(moves) -moves.index(move)
                return (beta, curr_move) # pruning
#                alpha = max(alpha,ret_val)

        else: # is "min"
            if ret_val < beta: # '<=' causes wrong move to be selected
                curr_move = move
            beta = min(beta, ret_val)
            if beta <= alpha:
                # self.prune_count += len(moves) -moves.index(move)
                return (alpha, curr_move) # pruning
#                beta = min(beta,ret_val)

    if mm == "max":
        return (alpha, curr_move)
    else: # is "min"
        return (beta, curr_move)
