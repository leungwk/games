import copy
import random

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


## TODO: get a real cache
class _LRUCache(object):
    def __init__(self, capacity):
        self._cache = {}
        self.capacity = capacity
        self._stats = {k: 0 for k in ['cache_hit', 'cache_miss']}


    # def __getitem__(self, idx):
    #     return self._cache[idx]


    def __setitem__(self, idx, val):
        if len(self._cache) > self.capacity:
            self._cache = dict(random.sample(self._cache.items(), self.capacity//2))
        self._cache[idx] = val
    ## why throw most of it out? Because as a game evolves, a given move is unlikely to be reversed. This might not generalize though.


    def get(self, idx, default=None):
        if idx in self._cache:
            self._stats['cache_hit'] += 1
            res = self._cache[idx]
        else:
            self._stats['cache_miss'] += 1
            res = default
        return res


    def stats(self):
        return self._stats


class AlphaBetaSearch(object):
    """"""
    def __init__(self, **kwargs):
        self.explore_depth = kwargs.get('explore_depth', 4)
        # self.explore_depth = 6
        self.seed = kwargs.get('seed', None)
        self.debug = kwargs.get('debug', False)
        for key, value in kwargs.items():
            if key == 'invalid_move':
                self.invalid_move = value
            elif key == 'heuristic':
                self.heuristic = value
            elif key == 'colour':
                self.colour = value
            # elif key == 'move_contraction_set':
            #     self.move_contraction_set = value
        self._capacity_transposition_table = kwargs.get('capacity_transposition_table', None)
        if self._capacity_transposition_table is not None:
            self.transposition_table = _LRUCache(self._capacity_transposition_table)
            self.enabled_transposition_table = True
        else:
            self.enabled_transposition_table = False
        if self.debug:
            self._stats = self._init_stats()


    def _init_stats(self):
        return {k: 0 for k in ['n_move']}


    def alphabeta(self, state):
        if self.enabled_transposition_table:
            self.transposition_table = _LRUCache(self._capacity_transposition_table)
        self._stats = self._init_stats()
        neginf = float('-Inf')
        posinf = float('Inf')
        explore_depth = self.explore_depth
        _, ret_move = self._alphabeta(
            state, neginf, posinf, explore_depth, "max", "min", self.colour)
        if ret_move == self.invalid_move:
            ## when the search starts with "max", an invalid move returned means that all eventual moves will lead to a terminal state (-inf), because "min" will choose only victory moves
            ## it might also return something if using ">=" rather than ">" (see the code), but this will create needless moves
            return random.sample([m for m in state.get_moves(self.colour)], 1)[0] # at least return something rather than invalid
        if self.debug:
            # import ipdb; ipdb.set_trace()
            self._stats['num_ply'] = state.num_ply
            if self.enabled_transposition_table:
                self._stats.update(self.transposition_table.stats())
        return ret_move


    def _alphabeta(self, state, alpha, beta, depth, mm, parent_mm, player):
        ## depth: depth remaining till a leaf
        if state.terminal(player) or depth == 0:
            return (self.heuristic(state, player), self.invalid_move) # invalid move

        curr_move = self.invalid_move
        moves = state.get_moves(player)
        for move in moves:
            new_state = copy.deepcopy(state)
            new_state.do_move(move)
            if self.debug:
                self._stats['n_move'] += 1

            # if (move in self.move_contraction_set) and (parent_move not in self.move_contraction_set):
            #     ## prevent case where both players only play DONE_MOVE
            #     new_depth = depth
            # else:
            #     new_depth = depth -1
            ## needed for DONE_MOVE in rith, where changing turns is not always necessary

            ## for multi-ply-per-turn games (and includes one ply, one turn games)
            new_player = new_state.turn
            if new_player != player: # change view of player
                new_mm = "max" if mm == "min" else "min"
            else: # same player's move
                new_mm = mm

            ## wrap in a transposition table so to hopefully cache some results, and thus have another method of pruning
            if not self.enabled_transposition_table:
                ret_val, _ = self._alphabeta(
                    new_state, alpha, beta, depth -1, new_mm, mm, new_player)
            else:
                tab_val = self.transposition_table.get((depth, new_state), None)
                if tab_val is None:
                    ret_val, _ = self._alphabeta(
                        new_state, alpha, beta, depth -1, new_mm, mm, new_player)
                    #
                    self.transposition_table[(depth, new_state)] = ret_val
                else:
                    ret_val = tab_val

            if mm == "max":
                if ret_val > alpha: # '>=' causes wrong move to be selected (and it should update only on improvements)
                    curr_move = move
                alpha = max(alpha, ret_val)
                if alpha >= beta: # value of adversery has now been exceeded, so no need to search further
                    if mm != parent_mm:
                        return (beta, curr_move) # pruning
                    else:
                        return (alpha, curr_move) # so that it propagates all the way up to the switch in mm, ignoring the remaning unexplored branches below the switch
            else: # is "min"
                if ret_val < beta: # '<=' causes wrong move to be selected
                    curr_move = move
                beta = min(beta, ret_val)
                if beta <= alpha:
                    if mm != parent_mm:
                        return (alpha, curr_move) # pruning
                    else:
                        return (beta, curr_move)

        if mm == "max":
            return (alpha, curr_move)
        else: # is "min"
            return (beta, curr_move)
