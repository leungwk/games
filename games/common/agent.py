import random
from games.search.mcts import MonteCarloTreeSearch
from games.search.alphabeta import alphabeta

class Agent(object):
    """Base class for common properties and methods of an Agent"""

    def __init__(self, colour, **kwargs):
        self.colour = colour


    def decision(self, state):
        pass


    def params(self):
        """Agent specific params that change its behaviour"""
        return {'colour': str(self.colour)}


class RandomAgent(Agent):
    """Randomly decide upon one feasible move.

    Intended as a baseline to compare against other AI.
    """
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        self.seed = kwargs.get('seed', None)
        for key, value in kwargs.items():
            if key =='invalid_move':
                self.invalid_move = value


    def decision(self, state):
        moves = list(state.get_moves(self.colour))
        if not moves:
            return self.invalid_move
        return random.sample(moves, 1)[0]


    def params(self):
        return super().params()


class AlphaBetaAgent(Agent):
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        self.explore_depth = kwargs.get('explore_depth', 4)
        self.seed = kwargs.get('seed', None)
        for key, value in kwargs.items():
            if key == 'invalid_move':
                self.invalid_move = value
            elif key == 'heuristic':
                self.heuristic = value
        self.alphabeta = alphabeta


    def decision(self, state):
        ## one_ply_lookahead_terminal removed, though this might be unwise...

        neginf = float('-Inf')
        posinf = float('Inf')
        explore_depth = self.explore_depth
        ret_val, ret_move = self.alphabeta(
            state, neginf, posinf, explore_depth, self.colour, "max", self.heuristic, self.invalid_move)
        if ret_move == self.invalid_move:
            ## when the search starts with "max", an invalid move returned means that all eventual moves will lead to a terminal state (-inf), because "min" will choose only victory moves
            ## it might also return something if using ">=" rather than ">" (see the code), but this will create needless moves
            return random.sample([m for m in state.get_moves(self.colour)], 1)[0] # at least return something rather than invalid
        return ret_move


    def params(self):
        res = super().params()
        res.update({
            'explore_depth': self.explore_depth,
            'heuristic': self.heuristic.__name__,
            'seed': self.seed,
            })
        return res


class MonteCarloTreeSearchAgent(Agent):
    """An aheuristic and asymmetric approximation to minimax. 2 player version"""
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        self.n_iter = self.seed = kwargs.get('n_iter', int(1e3))
        self.invalid_move = None
        self.hold_tree = kwargs.get('hold_tree', False)
        self.seed = kwargs.get('seed', None)
        for key, value in kwargs.items():
            if key == 'invalid_move':
                self.invalid_move = value
        self.search = MonteCarloTreeSearch(self.n_iter, self.invalid_move, hold_tree=self.hold_tree, seed=self.seed)


    def decision(self, root_state):
        return self.search.uct_search(root_state, self.colour)


    def params(self):
        res = super().params()
        res.update({
            'n_iter': self.n_iter,
            'seed': self.seed,
            })
        return res
