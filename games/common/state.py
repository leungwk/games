class State(object):
    """abstract base class?"""

    def do_move(self, move):
        pass

    def get_moves(self, player):
        """Get all legal and valid moves for player.

        Typically required only for search algorithms.
        """
        pass

    def terminal(self, player):
        pass

    ## TODO: add in __copy__?
