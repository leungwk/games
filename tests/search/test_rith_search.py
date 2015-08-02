from games.rith.piece import Player, PieceName
from games.rith.rith import Rith, RithBoard
from games.rith.piece import Circle, Triangle, Square, Pyramid, NONE_PIECE, OOB_PIECE

from games.search.rith.siege import PlusShape, EcksShape, _pieces_movable

rith = Rith(settings={'board_setup': 'fulke_1'})
# rith._board = RithBoard(16, 8) # blank it

shape_plus = PlusShape(rith._board, (8, 5))
assert shape_plus.start.coord == (8, 5)
assert shape_plus.start.piece == Triangle(9, Player.even)
assert shape_plus.east.coord == (9, 5)
assert shape_plus.east.piece == OOB_PIECE
assert shape_plus.north.coord == (8, 6)
assert shape_plus.north.piece == NONE_PIECE
assert shape_plus.west.piece == Triangle(6, Player.even)
assert shape_plus.south.piece == Square(15, Player.even)

pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
shape_ecks = EcksShape(rith._board, (1, 5))
assert shape_ecks.start.coord == (1, 5)
assert shape_ecks.start.piece == Triangle(81, Player.even)
assert shape_ecks.north_east.coord == (2, 6)
assert shape_ecks.north_east.piece == NONE_PIECE
assert shape_ecks.north_west.piece == OOB_PIECE
assert shape_ecks.south_west.piece == OOB_PIECE
assert shape_ecks.south_east.piece == pyramid_even


rith = Rith()
rith._board = RithBoard(16, 8) # blank it
rith._board[(5, 4)] = Circle(4, Player.even)
rith._board[(4, 4)] = Triangle(100, Player.odd)
rith._board[(4, 5)] = Circle(4, Player.even)
rith._board[(4, 3)] = Circle(6, Player.even)
rith._board[(4, 6)] = Triangle(72, Player.even)

pieces = [
    ((4, 5), Circle(4, Player.even)),
    ((4, 6), Triangle(72, Player.even)),
    ((4, 3), Circle(6, Player.even)),
    ]
assert set(_pieces_movable(rith, (3, 4))) == set(pieces)
assert set(_pieces_movable(rith, (8, 8))) == set([]) # nothing reachable
assert set(_pieces_movable(rith, (5, 4))) == set([]) # occupied
assert set(_pieces_movable(rith, (5, 4), allow_unoccupied=True)) == set(pieces)
