from enum import Enum

class Player(Enum):
    """Define the allowed players as a type"""

    invalid = 0
    black = 1
    white = 2
    none = 3

    def __str__(self):
        if self.value == 0:
            return '?'
        elif self.value == 1:
            return 'B'
        elif self.value == 2:
            return 'W'
        elif self.value == 3:
            return ' '
        else:
            return '!'


    def __repr__(self):
        if self.value == 0:
            return 'Player.invalid'
        elif self.value == 1:
            return 'Player.black'
        elif self.value == 2:
            return 'Player.white'
        elif self.value == 3:
            return 'Player.none'
        else:
            return 'Player.invalid' # filler


    @staticmethod
    def opponent(player):
        if player == Player.black:
            opponent = Player.white
        elif player == Player.white:
            opponent = Player.black
        elif player == Player.invalid:
            opponent = Player.invalid
        elif player == Player.none:
            opponent = Player.none # unsure what would happen...
        else:
            raise ValueError("Unknown value: {}".format(player))
        return opponent


class Cell(object):
    def __init__(self, num, player):
        self.num = num
        self.player = player


    def __eq__(self, other):
        return (self.num == other.num) and \
          (self.player == other.player)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        # return '{}{}'.format(self.num, '' if self.player == Player.black else '_') # because letters for colour are too distracting
        return '{}{}'.format(self.num, self.player) # ... but it becomes too confusing with no other indicators


    def __repr__(self):
        return 'Cell(num={num}, player={player})'.format(num=self.num, player=repr(self.player))


    def __hash__(self):
        return hash((self.num, self.player))


OOB_CELL = Cell(num=-1, player=Player.invalid)
