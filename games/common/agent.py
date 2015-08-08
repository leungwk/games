import random
from games.search.mcts import MonteCarloTreeSearch
# from games.search.alphabeta import alphabeta
from games.search.alphabeta import AlphaBetaSearch

class Agent(object):
    """Base class for common properties and methods of an Agent"""

    def __init__(self, colour, **kwargs):
        self.colour = colour


    def decision(self, state):
        pass


    def params(self):
        """Agent specific params that change its behaviour"""
        return {'colour': str(self.colour)}


    def stats(self):
        """Statistics about Agent behaviour"""
        return {}



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
        self.debug = kwargs.get('debug', False)
        self.capacity_transposition_table = kwargs.get('capacity_transposition_table', None)
        for key, value in kwargs.items():
            if key == 'heuristic':
                self.heuristic = value
        self.search = AlphaBetaSearch(
            colour=self.colour,
            invalid_move=kwargs.get('invalid_move', None),
            heuristic=kwargs.get('heuristic', None),
            explore_depth=self.explore_depth,
            seed=self.seed,
            debug=self.debug,
            capacity_transposition_table=self.capacity_transposition_table,
            # move_contraction_set=kwargs.get('move_contraction_set', {}),
            )
        self._decision_stats = []


    def decision(self, state):
        move_obj = self.search.alphabeta(state)
        if self.debug:
            self._decision_stats.append(self.search._stats)
        return move_obj


    def params(self):
        res = super().params()
        res.update({
            'explore_depth': self.explore_depth,
            'heuristic': self.heuristic.__name__,
            'seed': self.seed,
            })
        return res

    def stats(self):
        res = super().stats()
        res.update({
            'alphabeta': self._decision_stats,
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
