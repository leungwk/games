from collections import namedtuple

from common.board import Board

import copy

#### ================================================================
#### Board
#### ================================================================

Move = namedtuple('Move', ['src', 'dest'])
class Cell(object):
    def __init__(self, num, player):
        self.num = num
        self.player = player


    def __eq__(self, other):
        return (self.num == other.num) and \
          (self.player == other.player)


    def __ne__(self, other):
        return not self.__eq__(other)


EMPTY_CELL = Cell(num=0, player=None)

nrows = 5
ncols = 3
board = Board(nrows=nrows, ncols=ncols, constructor=lambda: EMPTY_CELL)
coord = (3,2)
assert board[coord] == EMPTY_CELL
try:
    board[(10,10)]
except KeyError:
    assert True
else:
    assert False

## __eq__
board_2 = copy.deepcopy(board)
assert board == board_2
board_2[(3,2)] = Cell(num=1, player='W')
assert board != board_2


## __iter__
## check all valid coords
assert set([coord for coord in board]) == set([
    (1, 2),
    (3, 2),
    (1, 3),
    (3, 3),
    (3, 1),
    (2, 1),
    (2, 4),
    (1, 5),
    (2, 3),
    (1, 4),
    (2, 2),
    (2, 5),
    (3, 4),
    (1, 1),
    (3, 5),
    ])

## iteration, vector
board[(2, 4)] = Cell(num=2, player='B')
move = Move((1, 3), (2, 4))
res = board.values_vec(move)
assert list(res) == [
    EMPTY_CELL,
    Cell(num=2, player='B'),
    EMPTY_CELL,
    ]

## iteration, neighbours
assert set(board.keys_neighbours((1,5))) == set([
    (1,4),
    (2,4),
    (2,5),
    ])
