class Agent(object):
    """Base class for common properties and methods of Agents"""

    def __init__(self, colour):
        self.colour = colour

    def decision(self, state):
        pass

    def params(self):
        """Agent specific params that affect its behaviour"""
        return {}
