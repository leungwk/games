import random

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
