import copy

def alphabeta(state, alpha, beta, depth, player, mm, heuristic, invalid_move):
    """\alpha-\beta search is minimax with pruning, a kind of branch and bound. 2 player version.


    Explanation of the pruning:

    max        (-inf)         (6)         (6)                (6)
               /              /           /  .              /   \
    min       .              /           /    (inf)        /     (5)
             . .     ==>    / \  ==>    / \    .   ==>    / \    /\
            .   .          /   \       /      . .        /      /  \
           .   . .        /   / \     /      .   .      /      /    \
    ...  (6)            (6)         (6)     (5)       (6)     (5)

    If max=6 (which was propagated from a leaf), then if player Min sees
    5, it would only accept any unexplored moves who values are 5 or
    lower. But because Max will choose 6, and Min will not choose
    anything lower than 5, there are no possible states that would
    change Max's decision given that Min would choose 5 or lower. Hence,
    the potential search tree for Min at 5 may be pruned.
    """
    if state.terminal(player) or \
       depth == 0:
        return (heuristic(state, player), invalid_move) # invalid move

    curr_move = invalid_move
    moves = state.get_moves(player)
    for move in moves:
        new_state = copy.deepcopy(state)
        new_state.do_move(move)

        ## for multi-ply-per-turn games (and includes one ply, one turn games)
        new_player = new_state.turn
        if new_player != player: # change view of player
            new_mm = "max" if mm == "min" else "min"
        else: # same player's move
            new_mm = mm
        ret_val, ret_move = alphabeta(
            new_state, alpha, beta, depth -1, new_player, new_mm, heuristic, invalid_move)

        if mm == "max":
            if ret_val > alpha: # '>=' causes wrong move to be selected (and it should update only on improvements)
                curr_move = move
            alpha = max(alpha, ret_val)
            if alpha >= beta: # value of adversery has now been exceeded, so no need to search further
                return (beta, curr_move) # pruning
        else: # is "min"
            if ret_val < beta: # '<=' causes wrong move to be selected
                curr_move = move
            beta = min(beta, ret_val)
            if beta <= alpha:
                return (alpha, curr_move) # pruning

    if mm == "max":
        return (alpha, curr_move)
    else: # is "min"
        return (beta, curr_move)
