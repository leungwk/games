from games.rith import Player, Piece, PieceName, Rith, RithBoard, Move, Take, Drop
from games.rith import NONE_PIECE
from games.rith import DECLARE_VICTORY_MOVE, DONE_MOVE
from games.rith import Circle, Triangle, Square, Pyramid
from games.rith import PlayerAgent
from games.common.board import Board
from functools import partial

import copy

####

assert Player.even == Player.opponent(Player.odd)
assert Player.odd == Player.opponent(Player.even)
assert Player.invalid == Player.opponent(Player.invalid)
assert Player.none == Player.opponent(Player.none)

#### pieces

assert Square(36, Player.even) == Square(36, Player.even)

pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_even_2 = copy.deepcopy(pyramid_even)
assert pyramid_even == pyramid_even_2

piece_S25 = Square(25, Player.even)
new_pyramid = Pyramid.remove_component(pyramid_even_2, piece_S25)
assert pyramid_even == pyramid_even_2 != new_pyramid != piece_S25

assert piece_S25 in [piece_S25, Square(36, Player.even)]
assert piece_S25 in pyramid_even.pieces
assert pyramid_even in set([pyramid_even_2])
assert piece_S25 not in set([pyramid_even_2, Square(36, Player.even)])
assert 1 == len(set([Square(36, Player.even), Square(36, Player.even)]))


#### Agent

agent_player = PlayerAgent(Player.even)
cmd = 'move (8, 13) (7, 10)'
assert tuple(agent_player._parse_cmd(cmd)) == (
    'move',
    '(8, 13)',
    '(7, 10)',
    )

cmd = 'take (7, 5) (7, 10) Triangle(36, Player.odd)'
assert tuple(agent_player._parse_cmd(cmd)) == (
    'take',
    '(7, 5)',
    '(7, 10)',
    'Triangle(36, Player.odd)'
    )

cmd = 'take (7, 5) (7, 10) T36_'
assert tuple(agent_player._parse_cmd(cmd)) == (
    'take',
    '(7, 5)',
    '(7, 10)',
    'Triangle(36, Player.odd)'
    )

cmd = 'take (7, 5) (7, 10) T36'
assert tuple(agent_player._parse_cmd(cmd)) == (
    'take',
    '(7, 5)',
    '(7, 10)',
    'Triangle(36, Player.even)'
    )

## move obj

assert Move((4, 4), (3, 3)) in set([Move((4, 4), (3, 3)), Move((4, 4), (3, 2))])
assert Move((4, 4), (3, 3)) not in set([Move((4, 4), (3, 1)), Move((4, 4), (3, 2))])
assert Take((5, 4), (6, 7), Circle(36, Player.even)) == Take((5, 4), (6, 7), Circle(36, Player.even))
assert Take((5, 4), (6, 7), Circle(36, Player.even)) != Take((5, 4), (6, 7), Circle(2, Player.even))
assert Drop(1, (1, 1)) == Drop(1, (1, 1))
assert Drop(1, (1, 1)) != Drop(2, (1, 1))
assert DECLARE_VICTORY_MOVE == DECLARE_VICTORY_MOVE
assert DONE_MOVE == DONE_MOVE
assert DECLARE_VICTORY_MOVE != DONE_MOVE
assert Move((4, 4), (3, 3)) not in set([Move((4, 4), (3, 1)), Move((4, 4), (3, 2)), Drop(1, (1, 1)), DONE_MOVE])


#### ================================================================
#### moving
#### ================================================================

pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])

rith = Rith()
rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 3)] = pyramid_even
rith._board[(4, 4)] = Circle(4, Player.even)
rith._board[(5, 5)] = Triangle(36, Player.odd)
rith._board[(5, 4)] = Square(49, Player.odd)
rith._board[(4, 6)] = pyramid_odd
rith._board[(6, 7)] = Circle(36, Player.even)
rith._board[(4, 7)] = Triangle(49, Player.even)

## marches and flights
## blank
assert not rith.is_legal_move(Move((0, 0), (1, 1))) # not on board
assert not rith.is_legal_move(Move((1, 1), (2, 2))) # nothing there

## Circle
assert not rith.is_legal_move(Move((4, 4), (3, 3))) # occupied by own piece
assert not rith.is_legal_move(Move((4, 4), (5, 5))) # blocked
assert not rith.is_legal_move(Move((4, 4), (6, 6))) # blocked and invalid step
assert not rith.is_legal_move(Move((4, 4), (4, 5))) # invalid dir, valid step size
assert not rith.is_legal_move(Move((4, 4), (4, 6))) # invalid dir, invalid step size
assert not rith.is_legal_move(Move((4, 4), (2, 2))) # valid dir, invalid step size
assert not rith.is_legal_move(Move((4, 4), (3, 3))) # valid dir, valid step size, but own piece in the way
assert rith.is_legal_move(Move((4, 4), (3, 5))) # valid dir, valid step size

## Triangle
assert not rith.is_legal_move(Move((5, 5), (5, 3))) # regular blocked, valid step size
assert not rith.is_legal_move(Move((5, 5), (6, 5))) # valid dir, invalid step size
rith.turn = Player.odd
assert rith.is_legal_move(Move((5, 5), (7, 5))) # regular, valid dir, valid step size
assert rith.is_legal_move(Move((5, 5), (7, 6))) # flying
assert rith.is_legal_move(Move((5, 5), (3, 6))) # flying
assert rith.is_legal_move(Move((5, 5), (4, 3))) # flying (jumps over C4)
assert not rith.is_legal_move(Move((5, 5), (4, 2))) # flying but wrong step
assert not rith.is_legal_move(Move((4, 7), (2, 8))) # valid movement, but not even's turn

## Square
assert not rith.is_legal_move(Move((5, 4), (5, 7))) # blocked regular, valid step size
assert not rith.is_legal_move(Move((5, 4), (2, 4))) # blocked regular, valid step size
assert not rith.is_legal_move(Move((5, 4), (7, 5))) # flying, wrong step size
assert not rith.is_legal_move(Move((5, 4), (7, 4))) # valid dir, invalid step size
assert rith.is_legal_move(Move((5, 4), (8, 4))) # valid dir, valid step size
assert rith.is_legal_move(Move((5, 4), (8, 5))) # flying, right step size

## Pyramid
# b = S64_ S49_ T36_ T25_ C16_
assert rith.is_legal_move(Move((4, 6), (3, 5))) # valid C
assert rith.is_legal_move(Move((4, 6), (2, 6))) # valid T
assert rith.is_legal_move(Move((4, 6), (1, 6))) # valid S
assert not rith.is_legal_move(Move((4, 6), (4, 4))) # valid T dir and step size but blocked by C4
assert not rith.is_legal_move(Move((4, 6), (4, 3))) # valid S dir and step size but blocked by C4
assert not rith.is_legal_move(Move((4, 6), (5, 4))) # flying T blocked by S49_
assert rith.is_legal_move(Move((4, 6), (5, 3))) # flying S

## pyramid-pyramid
rith.turn = Player.even
assert not rith.is_legal_move(Move((3, 3), (5, 4)))





#### _cond_steps
rith = Rith()
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = Circle(4, Player.even)
rith._board[(6, 6)] = Triangle(36, Player.odd)
rith._board[(5, 4)] = Square(49, Player.odd)
rith._board[(8, 4)] = Triangle(42, Player.even)

assert all(rith._cond_steps(0, (4, 4), (+1, 0)))
assert not all(rith._cond_steps(1, (4, 4), (+1, 0)))
assert all(rith._cond_steps(3 -1, (8, 4), (-1, 0)))
assert not all(rith._cond_steps(4 -1, (5, 4), (+1, 0)))
assert all(rith._cond_steps(1, (4, 4), (+1, +1)))




## drop
rith = Rith()
rith.turn = Player.even
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 1)] = Square(153, Player.even)
rith._board.prisoners_held_by_even = [Circle(9, Player.even), Square(28, Player.even)]
assert rith._is_legal_drop(Drop(1, (1, 1)))
assert not rith._is_legal_drop(Drop(1, (4, 1))) # already occupied
assert not rith._is_legal_drop(Drop(1, (1, 2))) # wrong row
rith.turn = Player.odd
assert not rith._is_legal_drop(Drop(1, (1, 1))) # wrong turn
rith.turn = Player.even
rith._board.prisoners_held_by_even = []
assert not rith._is_legal_drop(Drop(1, (1, 1))) # no prisoners



#### ================================================================
#### taking
#### ================================================================

#### _is_legal_take

## setup
#### equality
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
rith = Rith()
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = Circle(4, Player.even)
rith._board[(5, 5)] = piece_T36_ = Triangle(36, Player.odd)
rith._board[(5, 4)] = piece_S49_ = Square(49, Player.odd)
rith._board[(4, 6)] = pyramid_odd
rith._board[(6, 7)] = piece_C36 = Circle(36, Player.even)
rith._board[(2, 6)] = piece_T49 = Triangle(49, Player.even)
rith._board[(8, 4)] = Triangle(42, Player.even)
rith._board[(4, 10)] = piece_T16_ = Triangle(16, Player.odd)
rith._board[(5, 10)] = Square(66, Player.odd)
rith._board[(6, 10)] = piece_C16 = Circle(16, Player.even)
rith._board[(4, 9)] = pyramid_even
rith._board[(3, 12)] = piece_T81 = Triangle(81, Player.even)
rith._board[(5, 12)] = piece_S81_ = Square(81, Player.odd)

## piece-piece
assert not rith._valid_taking_by_equality(Take((5, 4), (6, 7), piece_C36)) # wrong number, irregular move
assert not rith._valid_taking_by_equality(Take((5, 5), (6, 7), piece_C36)) # right number, irregular move
assert not rith._valid_taking_by_equality(Take((4, 10), (6, 10), piece_C16)) # no clear line of sight
assert not rith._valid_taking_by_equality(Take((6, 10), (4, 10), piece_T16_)) # wrong number, regular move
assert rith._valid_taking_by_equality(Take((3, 12), (5, 12), piece_S81_)) # right number, regular move
assert not rith._valid_taking_by_equality(Take((3, 12), (5, 12), piece_T81)) # right number, regular move, wrong piece specified

## piece-pyramid
assert rith._valid_taking_by_equality(Take((2, 6), (4, 6), Square(49, Player.odd))) # right number, regular move
assert not rith._valid_taking_by_equality(Take((4, 6), (2, 6), piece_T49)) # ie. not necessarily symmetric (right number, not enough spaces in the regular move)

## pyramid-piece
assert not rith._valid_taking_by_equality(Take((4, 6), (5, 4), piece_S49_)) # cannot take own piece (and 'taking.equality.flight' disabled)
assert not rith._valid_taking_by_equality(Take((4, 6), (5, 5), piece_T36_)) # cannot take own piece
assert not rith._valid_taking_by_equality(Take((4, 9), (4, 10), piece_T16_)) # not the right component, nor is the pyramid's sum

## pyramid-pyramid
assert not rith._valid_taking_by_equality(Take((4, 6), (4, 9), Square(36, Player.even)))
assert rith._valid_taking_by_equality(Take((4, 9), (4, 6), Triangle(36, Player.odd))) # S36 takes T36_
assert rith._valid_taking_by_equality(Take((4, 9), (4, 6), Triangle(25, Player.odd))) # S25 takes T25_
assert not rith._valid_taking_by_equality(Take((4, 9), (4, 6), Circle(16, Player.odd))) # right coord and spaces, wrong piece



## take whole pyramid (or whole pyramid take), and where neither component can
pyramid_even = Pyramid(25, Player.even, pieces=[
    # Square(36, Player.even),
    # Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    # Circle(4, Player.even),
    # Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(90, Player.odd, pieces=[
    # Square(64, Player.odd),
    Square(49, Player.odd),
    # Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
rith = Rith()
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = pyramid_even
rith._board[(4, 6)] = piece_C25_ = Circle(25, Player.odd)
rith._board[(8, 4)] = pyramid_odd
rith._board[(8, 6)] = piece_T90 = Triangle(90, Player.even) # from capture

# piece-pyramid
assert not rith._valid_taking_by_equality(Take((8, 4), (8, 6), piece_T90)) # wrong turn
rith.turn = Player.odd
assert rith._valid_taking_by_equality(Take((8, 4), (8, 6), piece_T90))
rith.turn = Player.even
assert rith._valid_taking_by_equality(Take((8, 6), (8, 4), pyramid_odd))

# pyramid-piece
rith.turn = Player.even
assert rith._valid_taking_by_equality(Take((4, 4), (4, 6), piece_C25_)) # P25 takes C25_
rith.turn = Player.odd
assert not rith._valid_taking_by_equality(Take((4, 6), (4, 4), pyramid_even))






## taking by equality (flight)
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])

settings = {
    'taking.equality.flight': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 3)] = pyramid_even
rith._board[(4, 4)] = piece_C4 = Circle(4, Player.even)
rith._board[(5, 4)] = piece_S49_ = Square(49, Player.odd)
rith._board[(5, 5)] = piece_C36 = Circle(36, Player.even)
rith._board[(4, 6)] = piece_T36_ = Triangle(36, Player.odd)
rith._board[(6, 7)] = pyramid_odd
rith._board[(4, 7)] = piece_T49 = Triangle(49, Player.even)
rith._board[(6, 10)] = piece_C64 = Circle(64, Player.even)
rith._board[(6, 8)] = Square(361, Player.odd)

rith._board[(3, 8)] = Square(25, Player.even)

## piece-piece
rith.turn = Player.odd
assert rith._valid_taking_by_equality(Take((5, 4), (4, 7), piece_T49)) # jump
rith.turn = Player.even
assert rith._valid_taking_by_equality(Take((5, 5), (4, 6), piece_T36_)) # regular
rith.turn = Player.even
assert not rith._valid_taking_by_equality(Take((4, 7), (5, 4), piece_S49_)) # asymmetric
# assert rith._valid_taking_by_equality(Move((5, 5), (4, 6))) # not a jump

## piece-pyramid
rith.turn = Player.even
assert not rith._valid_taking_by_equality(Take((5, 5), (6, 7), Square(36, Player.odd))) # not within marches
# assert rith._valid_taking_by_equality(Move((4, 7), (6, 7))) # not a jump check
rith.turn = Player.even
assert rith._valid_taking_by_equality(Take((3, 8), (6, 7), Triangle(25, Player.odd)))
rith.turn = Player.even
assert not rith._valid_taking_by_equality(Take((3, 8), (6, 7), Circle(16, Player.odd))) # wrong piece

## pyramid-piece
rith.turn = Player.even
assert not rith._valid_taking_by_equality(Take((3, 3), (5, 4), piece_S49_)) # no common number
rith.turn = Player.even
assert not rith._valid_taking_by_equality(Take((3, 3), (4, 4), piece_C4)) # cannot take own piece
rith.turn = Player.odd
assert rith._valid_taking_by_equality(Take((6, 7), (5, 5), piece_C36)) # T36_ in P can take C36 by flight
# assert not rith._valid_taking_by_equality(Move((6, 7), (4, 7))) # not a jump check
rith.turn = Player.odd
assert not rith._valid_taking_by_equality(Take((6, 7), (6, 10), piece_C64)) # blocked by S361_

## whole pyramid takes piece
settings = {
    'taking.equality.flight': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
pyramid_even = Pyramid(49, Player.even, pieces=[
    Square(36, Player.even),
    # Square(25, Player.even),
    # Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    # Circle(1, Player.even),
    ])
rith._board[(3, 3)] = pyramid_even
rith._board[(5, 4)] = piece_S49_ = Square(49, Player.odd)

assert rith._valid_taking_by_equality(Take((3, 3), (5, 4), piece_S49_)) ## total value of even pyramid can capture S49_ using T's flying (the pyramid moves like the union of its moves when looking at its total sum)



## pyramid-pyramid
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])

settings = {
    'taking.equality.flight': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = pyramid_even
rith._board[(5, 7)] = pyramid_odd

assert rith._valid_taking_by_equality(Take((4, 4), (5, 7), Triangle(36, Player.odd))) # S36 takes T36_
assert not rith._valid_taking_by_equality(Take((5, 7), (4, 4), Square(36, Player.even))) # T36_ cannot take S36





## eruption
## should always be symmetric
settings = {
    'taking.eruption': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
# self._board[(6, 6)].piece = Circle(2, Player.even)
rith._board[(4, 4)] = piece_T9 = Triangle(9, Player.even)
rith._board[(7, 7)] = piece_T36_ = Triangle(36, Player.odd)
rith._board[(3, 6)] = Triangle(6, Player.even)
rith._board[(4, 6)] = piece_T12_ = Triangle(12, Player.odd)
rith._board[(3, 11)] = piece_C36 = Circle(36, Player.even)
rith._board[(7, 15)] = Pyramid(55, Player.even, pieces=[
    # Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
rith._board[(5, 15)] = pyramid_odd = Pyramid(165, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    # Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
rith._board[(5, 11)] = piece_C6 = Circle(6, Player.even)

## piece-piece
assert rith._valid_taking_by_eruption(Take((4, 4), (7, 7), piece_T36_)) # 9*4 = 36
assert not rith._valid_taking_by_eruption(Take((7, 7), (4, 4), piece_T9)) # 4*9 = 36 # wrong turn
rith.turn = Player.odd
assert rith._valid_taking_by_eruption(Take((7, 7), (4, 4), piece_T9)) # 4*9 = 36
rith.turn = Player.odd
assert not rith._valid_taking_by_eruption(Take((7, 7), (4, 4), piece_T36_)) # wrong piece at dest
rith.turn = Player.even
assert not rith._valid_taking_by_eruption(Take((4, 4), (4, 6), piece_T12_)) # 9*3 != 12
rith.turn = Player.even
assert rith._valid_taking_by_eruption(Take((3, 6), (4, 6), piece_T12_)) # 6*2 = 12
rith.turn = Player.even
assert not rith._valid_taking_by_eruption(Take((3, 6), (3, 11), piece_C36)) # same colour
rith.turn = Player.odd
assert not rith._valid_taking_by_eruption(Take((4, 6), (4, 11), NONE_PIECE)) # nothing there

## piece-pyramid
rith.turn = Player.odd
assert rith._valid_taking_by_eruption(Take((7, 7), (7, 15), Circle(4, Player.even))) # T36_/9 = C4
rith.turn = Player.odd
assert not rith._valid_taking_by_eruption(Take((7, 7), (7, 15), Circle(1, Player.even))) # T36_/9 = C4

## pyramid-piece
rith.turn = Player.even
assert rith._valid_taking_by_eruption(Take((7, 15), (7, 7), piece_T36_)) # C4*9 = T36_
rith.turn = Player.odd
assert not rith._valid_taking_by_eruption(Take((5, 15), (5, 11), piece_C6)) # T36_/5 != C6
rith.turn = Player.even
assert not rith._valid_taking_by_eruption(Take((5, 11), (5, 15), Triangle(36, Player.odd))) # T36_/5 != C6

## pyramid-pyramid
rith.turn = Player.even
assert rith._valid_taking_by_eruption(Take((7, 15), (5, 15), pyramid_odd))







## siege
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
settings = {
    # 'taking.siege': True,
    'taking.siege.block_marches': True,
    'taking.siege.surrounded': False,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = piece_T6 = Triangle(6, Player.even)
rith._board[(4, 6)] = Circle(3, Player.odd)
rith._board[(6, 4)] = Circle(5, Player.odd)
rith._board[(3, 4)] = Square(28, Player.odd)
rith._board[(4, 2)] = piece_T100_ = Triangle(100, Player.odd)
rith._board[(5, 5)] = piece_C6 = Circle(6, Player.even)
rith._board[(6, 6)] = Circle(7, Player.odd)
rith._board[(3, 3)] = Square(361, Player.odd)
rith._board[(4, 9)] = piece_S49 = Square(49, Player.even)
rith._board[(4, 10)] = Triangle(12, Player.odd)
rith._board[(5, 9)] = Triangle(8, Player.even)
rith._board[(3, 9)] = piece_S66_ = Square(66, Player.odd)
rith._board[(6, 9)] = Square(121, Player.odd)
rith._board[(3, 7)] = Circle(4, Player.even)
rith._board[(3, 12)] = piece_T72 = Triangle(72, Player.even)
rith._board[(2, 11)] = Circle(9, Player.odd)
rith._board[(4, 11)] = Circle(25, Player.odd)
rith._board[(2, 13)] = Circle(49, Player.odd)
rith._board[(4, 13)] = piece_C81_ = Circle(81, Player.odd)
rith._board[(5, 13)] = Circle(64, Player.even)
rith._board[(4, 14)] = Circle(36, Player.even)
rith._board[(1, 12)] = piece_T49 = Triangle(49, Player.even)
rith._board[(1, 14)] = piece_S81 = Square(81, Player.even)
rith._board[(3, 14)] = Square(153, Player.even)
rith._board[(3, 2)] = pyramid_even
rith._board[(2, 2)] = Square(120, Player.odd)
rith._board[(5, 2)] = Square(289, Player.even)
rith._board[(4, 1)] = pyramid_odd

## block_marches
## piece-piece
assert not rith._valid_taking_by_siege(Take(None, (4, 4), piece_T6)) # wrong turn
rith.turn = Player.odd
assert rith._valid_taking_by_siege(Take(None, (4, 4), piece_T6))
rith.turn = Player.odd
assert not rith._valid_taking_by_siege(Take(None, (5, 5), piece_C6)) # some regular moves are not blocked by opponent pieces
rith.turn = Player.odd
assert rith._valid_taking_by_siege(Take(None, (4, 9), piece_S49)) # even though T8 in the way, S121_ blocks the spaces of S49 potential marches (Fulke first kind)
rith.turn = Player.even
assert rith._valid_taking_by_siege(Take(None, (3, 9), piece_S66_)) # S66_ has its march in the (-1,0) direction blocked by board edge

## piece-pyramid
# T and S of P have no valid marches
rith.turn = Player.odd
assert rith._valid_taking_by_siege(Take(None, (3, 2), Square(36, Player.even)))
assert rith._valid_taking_by_siege(Take(None, (3, 2), Square(25, Player.even)))
assert not rith._valid_taking_by_siege(Take(None, (3, 2), Square(16, Player.even))) # piece not there (and S16 not seen in initial setup in classical descriptions)
assert rith._valid_taking_by_siege(Take(None, (3, 2), Triangle(16, Player.even)))
assert rith._valid_taking_by_siege(Take(None, (3, 2), Triangle(9, Player.even)))
assert not rith._valid_taking_by_siege(Take(None, (3, 2), Square(4, Player.even)))
assert not rith._valid_taking_by_siege(Take(None, (3, 2), Square(1, Player.even)))



## pyramid-piece
rith.turn = Player.even
assert rith._valid_taking_by_siege(Take(None, (4, 2), piece_T100_)) # enough blocking (3 by even player, 1 by board edge)

## pyramid-pyramid
# C of b have no valid marches due to P and S289
rith.turn = Player.even
assert not rith._valid_taking_by_siege(Take(None, (4, 1), pyramid_odd)) # because it is asking whether it can take the entire pyramid (as opposed to a particular component)
assert not rith._valid_taking_by_siege(Take(None, (4, 1), Square(64, Player.odd)))
assert not rith._valid_taking_by_siege(Take(None, (4, 1), Square(49, Player.odd)))
assert not rith._valid_taking_by_siege(Take(None, (4, 1), Triangle(36, Player.odd)))
assert not rith._valid_taking_by_siege(Take(None, (4, 1), Triangle(25, Player.odd)))
assert rith._valid_taking_by_siege(Take(None, (4, 1), Circle(16, Player.odd)))




## surrounded
## piece-piece
rith.settings['taking.siege.surrounded'] = True
rith.turn = Player.odd
assert rith._valid_taking_by_siege(Take(None, (3, 12), piece_T72)) # T72 is surrounded, even though it has legal marching moves available
rith.turn = Player.even
assert not rith._valid_taking_by_siege(Take(None, (4, 13), piece_C81_)) # not enough surrounding by '+' or 'x' shape (number of pieces is insufficient)
rith.turn = Player.odd
assert rith._valid_taking_by_siege(Take(None, (1, 12), piece_T49)) # surrounded by 2 cornerwise and board edge
rith.turn = Player.odd
assert not rith._valid_taking_by_siege(Take(None, (1, 14), piece_S81))


## piece-pyramid
rith.settings['taking.siege.block_marches'] = False
rith.turn = Player.odd
assert not rith._valid_taking_by_siege(Take(None, (3, 2), pyramid_even)) # not completely surrounded
rith._board[(3, 1)] = Triangle(56, Player.odd)
rith.turn = Player.odd
assert rith._valid_taking_by_siege(Take(None, (3, 2), pyramid_even)) # now completely surrounded
rith._board[(3, 1)] = NONE_PIECE
rith._board[(3, 1)] = pyramid_odd
rith._board[(4, 1)] = NONE_PIECE

## pyramid-pyramid (pyramid-piece)
assert rith._valid_taking_by_siege(Take(None, (3, 2), pyramid_even)) # now completely surrounded
assert rith._valid_taking_by_siege(Take(None, (3, 2), Square(25, Player.even))) # and so are all components





## addition/subtraction
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
settings = {
    'taking.addition.marches': True,
    'taking.addition.line_adjacency': False,
    'taking.addition.any_adjacency': False,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = piece_C25_ = Circle(25, Player.odd)
rith._board[(2, 4)] = Triangle(9, Player.even)
rith._board[(3, 5)] = piece_C4 = Circle(4, Player.even)
rith._board[(5, 5)] = piece_C16 = Circle(16, Player.even)
rith._board[(5, 6)] = Circle(9, Player.odd)
rith._board[(4, 6)] = piece_C5_ = Circle(5, Player.odd)
rith._board[(3, 6)] = Triangle(20, Player.even)
rith._board[(4, 9)] = piece_S25 = Square(25, Player.even)
rith._board[(5, 8)] = Circle(3, Player.odd)
rith._board[(7, 9)] = piece_S28_ = Square(28, Player.odd)
rith._board[(6, 9)] = Square(121, Player.odd)
rith._board[(7, 8)] = Circle(36, Player.even)
rith._board[(7, 10)] = Circle(8, Player.even)

rith._board[(1, 4)] = piece_T90_ = Triangle(90, Player.odd)
rith._board[(1, 3)] = Triangle(81, Player.even)
rith._board[(4, 12)] = piece_T30_ = Triangle(30, Player.odd)
rith._board[(6, 12)] = pyramid_even
rith._board[(4, 15)] = Square(66, Player.even) # by capture

rith._board[(1, 6)] = pyramid_odd
rith._board[(2, 7)] = piece_C16 = Circle(16, Player.even)

## piece-piece
# search
assert rith._valid_taking_by_addition(Take(None, (4, 4), piece_C25_)) # T9 + C16 = C25_
# specified
assert rith._valid_taking_by_addition(Take([(2, 4), (5, 5)], (4, 4), piece_C25_)) # T9 + C16 = C25_
assert rith._valid_taking_by_addition(Take([(5, 5), (2, 4)], (4, 4), piece_C25_)) # T9 + C16 = C25_ # symmetric
assert not rith._valid_taking_by_addition(Take([(5, 5), (2, 4), (3, 5)], (4, 4), piece_C25_)) # T9 + C16 = C25_ # malformed
assert not rith._valid_taking_by_addition(Take([(5, 5)], (4, 4), piece_C25_)) # T9 + C16 = C25_ # malformed
assert not rith._valid_taking_by_addition(Take([], (4, 4), piece_C25_)) # T9 + C16 = C25_ # malformed
assert not rith._valid_taking_by_addition(Take([(2, 7), (2, 4)], (4, 4), piece_C25_)) # T9 + C16 = C25_ # right numbers, wrong location

assert not rith._valid_taking_by_addition(Take(None, (5, 5), piece_C16)) # right difference, wrong movement
assert not rith._valid_taking_by_addition(Take([(4, 4), (5, 6)], (5, 5), piece_C16)) # right difference, wrong movement

assert not rith._valid_taking_by_addition(Take(None, (3, 5), piece_C4)) # right movement, wrong sum; as well, difference involves player's own piece
assert not rith._valid_taking_by_addition(Take([(2, 4), (4, 6)], (3, 5), piece_C4)) # right movement, wrong sum; as well, difference involves player's own piece

assert not rith._valid_taking_by_addition(Take(None, (4, 6), piece_C5_)) # T20 is too close
assert not rith._valid_taking_by_addition(Take([(3, 6), (4, 9)], (4, 6), piece_C5_)) # T20 is too close

assert not rith._valid_taking_by_addition(Take(None, (4, 9), piece_S25)) # blocked by S121_
assert not rith._valid_taking_by_addition(Take([(7, 9), (5, 8)], (4, 9), piece_S25)) # blocked by S121_



## piece-pyramid
assert not rith._valid_taking_by_addition(Take(None, (6, 12), pyramid_even)) # S121_ -S30_ = P91 (full) # wrong turn
assert not rith._valid_taking_by_addition(Take([(4, 12), (6, 9)], (6, 12), pyramid_even)) # S121_ -S30_ = P91 (full) # wrong turn
rith.turn = Player.odd
assert rith._valid_taking_by_addition(Take(None, (6, 12), pyramid_even)) # S121_ -S30_ = P91 (full)
assert rith._valid_taking_by_addition(Take([(4, 12), (6, 9)], (6, 12), pyramid_even)) # S121_ -S30_ = P91 (full)
assert not rith._valid_taking_by_addition(Take([(4, 12), (6, 9)], (6, 12), Square(25, Player.even))) # right coord, wrong piece

rith.turn = Player.even
assert rith._valid_taking_by_addition(Take(None, (1, 6), Triangle(36, Player.odd))) # T20+C16=T36 (component)
assert not rith._valid_taking_by_addition(Take(None, (1, 6), Triangle(36, Player.even))) # wrong colour
assert not rith._valid_taking_by_addition(Take(None, (1, 6), pyramid_even))
assert rith._valid_taking_by_addition(Take([(2, 7), (3, 6)], (1, 6), Triangle(36, Player.odd))) # T20+C16=T36 (component)



## pyramid-piece
rith.turn = Player.even
assert not rith._valid_taking_by_addition(Take(None, (4, 12), piece_T30_)) # 66-36=30 but it is not S36's marching move # this case tests whether the S36 inside the pyramid is used in determining the marches, rather than P as a whole, whose marches are the union of all components
## see also 'taking.multiplication.marches'
## assert not rith._valid_taking_by_multiplication(Move((4, 4), (4, 7)))
## for a similar situation (when looking at the code)
assert not rith._valid_taking_by_addition(Take([(6, 12), (4, 15)], (4, 12), piece_T30_))




## line_adjacency
rith.settings['taking.addition.line_adjacency'] = True
rith.turn = Player.even
assert rith._valid_taking_by_addition(Take(None, (7, 9), piece_S28_)) # line adjacency
assert rith._valid_taking_by_addition(Take([(7, 8), (7, 10)], (7, 9), piece_S28_)) # line adjacency
assert rith._valid_taking_by_addition(Take([(7, 10), (7, 8)], (7, 9), piece_S28_)) # line adjacency; symmetric

rith.settings['taking.addition.marches'] = False
rith.turn = Player.odd
assert not rith._valid_taking_by_addition(Take(None, (5, 5), piece_C16)) # right numbers, not a line
assert not rith._valid_taking_by_addition(Take([(4, 4), (5, 6)], (5, 5), piece_C16))
rith.settings['taking.addition.marches'] = True

rith.settings['taking.addition.line_adjacency'] = False


rith.turn = Player.even
assert not rith._valid_taking_by_addition(Take(None, (1, 4), piece_T90_))
assert not rith._valid_taking_by_addition(Take([(1, 3), (2, 4)], (1, 4), piece_T90_))
rith.settings['taking.addition.any_adjacency'] = True
assert rith._valid_taking_by_addition(Take(None, (1, 4), piece_T90_)) # any adjacency
assert rith._valid_taking_by_addition(Take([(1, 3), (2, 4)], (1, 4), piece_T90_)) # any adjacency
rith.settings['taking.addition.any_adjacency'] = False
# TODO: what if there are 3+ pieces adjacent?

## TODO: pyramid-pyramid and combos of
## piece-pyramid
## pyramid-piece
## pyramid-pyramid
## for adjacency taking




## marches
## pyramid-pyramid
settings = {
    'taking.addition.marches': True,
}
pyramid_even = Pyramid(50, Player.even, pieces=[
    Square(36, Player.even),
    # Square(25, Player.even),
    # Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(154, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    # Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = pyramid_even
rith._board[(4, 7)] = pyramid_odd
rith._board[(7, 4)] = Square(28, Player.odd)

# pyramid-pyramid
rith.turn = Player.odd
assert rith._valid_taking_by_addition(Take(None, (4, 4), Square(36, Player.even))) # S64_-S28_=S36
assert not rith._valid_taking_by_addition(Take(None, (4, 4), Triangle(9, Player.even)))
assert rith._valid_taking_by_addition(Take([(4, 7), (7, 4)], (4, 4), Square(36, Player.even))) # S64_-S28_=S36
assert not rith._valid_taking_by_addition(Take([(4, 7), (7, 4)], (4, 4), Triangle(9, Player.even)))







## multiplication/division
settings = {
    'taking.multiplication.marches': True,
    'taking.multiplication.void_spaces': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = piece_T36_ = Triangle(36, Player.odd)
rith._board[(2, 4)] = piece_T72 = Triangle(72, Player.even)
rith._board[(5, 5)] = piece_C2 = Circle(2, Player.even)
rith._board[(6, 6)] = piece_T90_ = Triangle(90, Player.odd)
rith._board[(6, 3)] = Square(45, Player.even)
rith._board[(2, 13)] = piece_C9_ = Circle(9, Player.odd)
rith._board[(3, 8)] = piece_S28_ = Square(28, Player.odd)
rith._board[(6, 8)] = pyramid_even = Pyramid(14, Player.even, pieces=[
    # Square(36, Player.even),
    # Square(25, Player.even),
    # Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
rith._board[(7, 10)] = piece_C81 = Circle(81, Player.odd)
rith._board[(7, 8)] = Triangle(9, Player.even)

## piece-piece
assert rith._valid_taking_by_multiplication(Take(None, (4, 4), piece_T36_)) # 36 = 72/2
rith.turn = Player.odd
assert not rith._valid_taking_by_multiplication(Take(None, (4, 4), piece_T36_)) # 36 = 72/2 # wrong turn
rith.turn = Player.even

assert rith._valid_taking_by_multiplication(Take([(2, 4), (5, 5)], (4, 4), piece_T36_)) # 36 = 72/2
assert not rith._valid_taking_by_multiplication(Take([(2, 4), (5, 5), (6, 4)], (4, 4), piece_T36_)) # 36 = 72/2 # malformed
assert not rith._valid_taking_by_multiplication(Take([(2, 4)], (4, 4), piece_T36_)) # 36 = 72/2 # malformed
assert not rith._valid_taking_by_multiplication(Take([], (4, 4), piece_T36_)) # 36 = 72/2 # malformed
# TODO: add case where right number and wrong moves (even if underneath it uses the same case as taking by addition)

assert rith._valid_taking_by_multiplication(Take(None, (6, 6), piece_T90_)) # 90 = 45*2
assert rith._valid_taking_by_multiplication(Take([(6, 3), (5, 5)], (6, 6), piece_T90_)) # 90 = 45*2

assert not rith._valid_taking_by_multiplication(Take(None, (5, 5), piece_C2)) # 2 != 90/36
assert not rith._valid_taking_by_multiplication(Take([(4, 4), (6, 6)], (5, 5), piece_C2)) # 2 != 90/36

# check that flying moves are /not/ valid
assert not rith._valid_taking_by_multiplication(Take(None, (7, 10), piece_C81)) # 81=9*9, but one of them requires a flying move
assert not rith._valid_taking_by_multiplication(Take([(6, 8), (7, 8)], (7, 10), piece_C81)) # 81=9*9, but one of them requires a flying move


## void spaces

## piece-piece
rith.turn = Player.odd
assert not rith._valid_taking_by_multiplication(Take((2, 4), (2, 13), piece_C9_)) # 72 = 8*9 # wrong turn
rith.turn = Player.even
assert rith._valid_taking_by_multiplication(Take((2, 4), (2, 13), piece_C9_)) # 72 = 8*9
rith.turn = Player.odd
assert rith._valid_taking_by_multiplication(Take((2, 13), (2, 4), piece_T72)) # 72 = 8*9 # is symmetric

## piece-pyramid
rith.turn = Player.odd
assert rith._valid_taking_by_multiplication(Take((3, 8), (6, 8), pyramid_even)) # capture pyramid's total

## pyramid-piece
rith.turn = Player.even
assert rith._valid_taking_by_multiplication(Take((6, 8), (3, 8), piece_S28_)) # pyramid's total captures S28_

## pyramid-pyramid
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
settings = {
    'taking.multiplication.void_spaces': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = pyramid_even
rith._board[(4, 9)] = pyramid_odd

## move.src needs to be specified
rith.turn = Player.even
assert rith._valid_taking_by_multiplication(Take((4, 4), (4, 9), Triangle(36, Player.odd))) # T16*4 = S64_, or T9*4=T36_
assert not rith._valid_taking_by_multiplication(Take((4, 4), (4, 9), Triangle(25, Player.odd))) # nothing in pyramid_even / 4 = 25
rith.turn = Player.odd
assert rith._valid_taking_by_multiplication(Take((4, 9), (4, 4), Triangle(9, Player.even))) # symmetric




## marches
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
pyramid_even = Pyramid(75, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    # Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
settings = {
    'taking.multiplication.marches': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 5)] = Circle(4, Player.even)
rith._board[(6, 6)] = piece_T9 = Triangle(9, Player.even)
rith._board[(4, 6)] = pyramid_odd
rith._board[(6, 9)] = piece_S225_ = Square(225, Player.odd)
rith._board[(8, 9)] = Triangle(25, Player.even)
rith._board[(4, 4)] = pyramid_even
rith._board[(3, 3)] = Circle(3, Player.odd)
rith._board[(4, 2)] = Triangle(16, Player.odd)

# piece-piece
assert not rith._valid_taking_by_multiplication(Take(None, (6, 9), piece_S225_)) # though 9*25=225, S225_ is not within T9's marching moves
assert not rith._valid_taking_by_multiplication(Take([(6, 6), (8, 9)], (6, 9), piece_S225_)) # though 9*25=225, S225_ is not within T9's marching moves

# piece-pyramid
assert rith._valid_taking_by_multiplication(Take(None, (4, 6), Triangle(36, Player.odd))) # 4*9 = 36
assert rith._valid_taking_by_multiplication(Take([(3, 5), (6, 6)], (4, 6), Triangle(36, Player.odd))) # 4*9 = 36
assert not rith._valid_taking_by_multiplication(Take([(3, 5), (6, 6)], (4, 6), Triangle(25, Player.odd)))

# pyramid-piece
rith.turn = Player.odd
assert rith._valid_taking_by_multiplication(Take(None, (6, 6), piece_T9)) # S225_/T25_ = T9
assert rith._valid_taking_by_multiplication(Take([(6, 9), (4, 6)], (6, 6), piece_T9)) # S225_/T25_ = T9

# pyramid-pyramid
assert rith._valid_taking_by_multiplication(Take(None, (4, 4), pyramid_even)) # T25_*C3_ = P75
assert rith._valid_taking_by_multiplication(Take([(4, 6), (3, 3)], (4, 4), pyramid_even)) # T25_*C3_ = P75
assert rith._valid_taking_by_multiplication(Take([(3, 3), (4, 6)], (4, 4), pyramid_even)) # T25_*C3_ = P75 # symmetric

pyramid_even_2 = Pyramid(50, Player.even, pieces=[
    Square(36, Player.even),
    # Square(25, Player.even),
    # Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
assert not rith._valid_taking_by_multiplication(Take([(3, 3), (4, 6)], (4, 4), pyramid_even_2)) # T25_*C3_ = P75 # symmetric







settings = {
    'taking.multiplication.marches': True,
    'taking.multiplication.void_spaces': True,
}
pyramid_even = Pyramid(50, Player.even, pieces=[
    Square(36, Player.even),
    # Square(25, Player.even),
    # Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = pyramid_even
rith._board[(4, 7)] = piece_T36_ = Triangle(36, Player.odd)
rith._board[(6, 4)] = piece_C81_ = Circle(81, Player.odd)
rith._board[(6, 2)] = Triangle(9, Player.even)

# pyramid-piece
assert not rith._valid_taking_by_multiplication(Take((4, 4), (4, 7), piece_T36_)) # even though Pyramid has the components (9*4=36), and is within a move of one of those pieces, taking by multiplication requires two distinct pieces

assert rith._valid_taking_by_multiplication(Take(None, (6, 4), piece_C81_)) # it needs to look into the pyramid's component to get this correct.
assert rith._valid_taking_by_multiplication(Take([(4, 4), (6, 2)], (6, 4), piece_C81_)) # it needs to look into the pyramid's component to get this correct.






#### ================================================================
#### victory
#### ================================================================

## common victories
# a missing victory condition means it is disabled
# 0 is not a valid number for any
settings = {
    'victory.take_pyramid_first': True, # see "game 2" in do_move test section
    # 'victory.bodies': 8,
    # 'victory.goods': 100,
    # 'victory.quarrels': 9,
    # 'victory.honour': 10,
    # 'victory.standards': 4, # TODO: implement
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board.prisoners_held_by_odd = [
    Circle(2, Player.odd),
    Circle(4, Player.odd),
    Circle(6, Player.odd),
    Circle(8, Player.odd), # they should have changed sides upon taking
    Triangle(25, Player.odd),
    Circle(64, Player.odd),
]
##
rith.settings['victory.bodies'] = 8
assert not rith.terminal(Player.odd)
rith.settings['victory.bodies'] = 6
assert rith.terminal(Player.odd)
del rith.settings['victory.bodies']
##
rith.settings['victory.goods'] = True
rith.settings['victory.goods.num'] = 110
assert not rith.terminal(Player.odd)
rith.settings['victory.goods.num'] = 100
assert rith.terminal(Player.odd)
del rith.settings['victory.goods']
##
rith.settings['victory.quarrels'] = 9
assert not rith.terminal(Player.odd)
rith.settings['victory.quarrels'] = 8
assert rith.terminal(Player.odd)
del rith.settings['victory.quarrels']
##
rith.settings['victory.honour'] = 3
assert not rith.terminal(Player.odd)
rith.settings['victory.honour'] = 4
assert rith.terminal(Player.odd)

# TODO: test that pyramid is /not/ in the list of prisoners (or, don't count it, and only counts its components, but excluding itself)

## proper victories
## 3 pieces
settings = {
    'victory.take_pyramid_first': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 9)] = Square(15, Player.even)
rith._board[(5, 9)] = Triangle(30, Player.odd)
rith._board[(6, 9)] = Square(45, Player.even)
assert not rith.terminal(Player.even) # victory not declared
assert not rith._victory_declared
rith.do_move(DECLARE_VICTORY_MOVE)
assert rith.terminal(Player.even) # valid
assert rith._victory_declared # _victory_declared remains set (and will until more moves are made, but terminal() returning True should end the game)
## game over

rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 10)] = Square(15, Player.even)
rith._board[(4, 9)] = Triangle(30, Player.odd)
rith._board[(4, 8)] = Square(45, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # offside

rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 9)] = Square(15, Player.even)
rith._board[(5, 9)] = Triangle(30, Player.odd)
rith._board[(7, 9)] = Square(45, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert rith.terminal(Player.even) # valid; spacing of 1
assert not rith.terminal(Player.odd) # because the progression must be completely made on the opposing side

rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 9)] = Square(15, Player.even)
rith._board[(5, 9)] = Triangle(30, Player.odd)
rith._board[(6, 9)] = Square(45, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # unequally spaced

rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 9)] = Square(15, Player.even)
rith._board[(5, 9)] = Triangle(30, Player.odd)
rith._board[(6, 9)] = Circle(6, Player.even)
rith._board[(7, 9)] = Square(45, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # blocked by C6

rith._board = RithBoard(16, 8) # blank it
rith._board[(3, 9)] = Square(15, Player.even)
rith._board[(5, 9)] = Triangle(30, Player.odd)
rith._board[(7, 9)] = Circle(6, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # not a valid sequence


## 4 pieces
settings = {
    'victory.take_pyramid_first': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 10)] = Circle(2, Player.even)
rith._board[(5, 10)] = Circle(3, Player.odd)
rith._board[(5, 9)] = Circle(4, Player.even)
rith._board[(4, 9)] = Circle(8, Player.even)
assert not rith.terminal(Player.even) # victory undeclared
rith.do_move(DECLARE_VICTORY_MOVE)
assert rith.terminal(Player.even) # arithmetic and geometrical

rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 11)] = Circle(2, Player.even)
rith._board[(6, 11)] = Circle(3, Player.odd)
rith._board[(6, 9)] = Circle(4, Player.even)
rith._board[(4, 9)] = Circle(8, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert rith.terminal(Player.even) # arithmetic and geometrical; spacing of 1

rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 11)] = Circle(2, Player.even)
rith._board[(6, 11)] = Circle(3, Player.odd)
rith._board[(6, 9)] = Circle(4, Player.even)
rith._board[(6, 10)] = Square(66, Player.odd)
rith._board[(4, 9)] = Circle(8, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # blocked by T66_

rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 9)] = Circle(2, Player.even)
rith._board[(5, 9)] = Circle(3, Player.odd)
rith._board[(5, 8)] = Circle(4, Player.even)
rith._board[(4, 8)] = Circle(8, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # offside

rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 10)] = Circle(2, Player.even)
rith._board[(5, 10)] = Circle(4, Player.even)
rith._board[(5, 9)] = Circle(3, Player.odd)
rith._board[(4, 9)] = Circle(8, Player.even)
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.even) # out of order

#### ================================================================
#### get_moves
#### ================================================================

settings = {
    'board_setup': 'fulke_1', # starts closer together
    'taking.equality.flight': False, # flight should be for jumping only
    'taking.eruption': True, # otherwise the opening game seems slow, and might give a more "math-y" feel
    # after all, what is the equivalent of an "archer"?
    'taking.siege.block_marches': True,
    'taking.siege.surrounded': True,
    'taking.addition.marches': True,
    'taking.addition.line_adjacency': True,
    'taking.addition.any_adjacency': False,
    'taking.multiplication.marches': True,
    'taking.multiplication.void_spaces': False, # eruption better
    'victory.take_pyramid_first': True, # forces the enemy to go after it
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = Square(15, Player.even)

## move
move_counts = [
    ## move
    12, # S15
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))
rith._board[(5, 5)] = Circle(4, Player.even)
move_counts = [
    ## move
    12, # S15
    3,  # C4 (S15 blocks one move)
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

rith._board[(8, 1)] = Circle(2, Player.even)
move_counts = [
    ## move
    12, # S15
    3,  # C4 (S15 blocks one move)
    1,  # C2
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

## taking by eruption
rith._board[(5, 11)] = Square(28, Player.odd)
move_counts = [
    ## move
    12, # S15
    3,  # C4 (S15 blocks one move)
    1,  # C2
    ## take
    1, # C4 at (5, 5) takes S28_ at (5, 11)
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

## drop
rith._board.prisoners_held_by_even = [
    Square(120, Player.even)
    ]
move_counts = [
    ## move
    12, # S15
    3,  # C4 (S15 blocks one move)
    1,  # C2
    ## take
    1,  # C4 at (5, 5) takes S28_ at (5, 11)
    ## drop
    7,  # 1 prisoner, 7 available back row spaces
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

# taking by siege
rith._board[(1, 1)] = Circle(3, Player.odd)
rith._board[(2, 2)] = Triangle(81, Player.even)
move_counts = [
    ## move
    12, # S15
    3,  # C4 (S15 blocks one move)
    1,  # C2
    6,  # T81
    ## take
    1,  # eruption: C4 at (5, 5) takes S28_ at (5, 11)
    1,  # siege at (1,1)
    ## drop
    6,  # 1 prisoner, 6 available back row spaces
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

# taking by equality
rith._board[(4, 2)] = Circle(81, Player.odd)
move_counts = [
    ## move
    11, # S15 (one move blocked by C81_)
    3,  # C4 (S15 blocks one move)
    1,  # C2
    5,  # T81
    ## take
    1,  # eruption: C4 at (5, 5) takes S28_ at (5, 11)
    1,  # siege at (1,1)
    1,  # equality: (2, 2) takes (4, 2)
    ## drop
    6,  # 1 prisoner, 7 available back row spaces
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

# taking by multiplication
rith._board[(7, 2)] = Triangle(90, Player.odd)
rith._board[(7, 5)] = Square(45, Player.even)
move_counts = [
    ## move
    10, # S15 (one move blocked by C81_, one by S45)
    3,  # C4 (S15 blocks one move)
    0,  # C2
    5,  # T81
    6,  # S45
    ## take
    1,  # eruption: C4 at (5, 5) takes S28_ at (5, 11)
    1,  # siege at (1,1)
    1,  # equality: T81 at (2, 2) takes C81_ at (4, 2)
    1,  # taking by multplication: T90_ at (7,2)
    ## drop
    6,  # 1 prisoner, 6 available back row spaces
    ## done
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))



rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 9)] = Square(15, Player.even)
rith._board[(5, 9)] = Triangle(30, Player.odd)
rith._board[(6, 9)] = Square(45, Player.even)

## vict
## and taking by addition (line adjacency)
move_counts = [
    ## move
    11, # S15
    8,  # S45 (lost 1 by being blocked, and 3 from board edge)
    ## take
    1,  # eruption
    1,  # taking by addition (line adjacency)
    ## done
    1,
    ## vict
    1,
]
assert sum(move_counts) == len(rith.get_moves(Player.even))

settings['taking.eruption'] = False
settings['taking.multiplication.void_spaces'] = True
rith._board[(4, 3)] = Circle(3, Player.odd)
move_counts = [
    ## move
    11, # S15
    8,  # S45 (lost 1 by being blocked, and 3 from board edge)
    ## take
    1,  # taking by addition (line adjacency)
    1,  # taking by multiplication (void spaces)
    ## done
    1,
    ## vict
    1,
]
## taking by multiplication (void spaces)
assert sum(move_counts) == len(rith.get_moves(Player.even))

#### ================================================================
#### do_move
#### ================================================================

## game 1
pyramid_even = Pyramid(91, Player.even, pieces=[
    Square(36, Player.even),
    Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    Circle(4, Player.even),
    Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
settings = {
    'taking.multiplication.marches': True,
    'taking.eruption': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board[(4, 4)] = piece_C4 = Circle(4, Player.even)
rith._board[(6, 4)] = Triangle(9, Player.even)
rith._board[(7, 7)] = piece_C9_ = Circle(9, Player.odd)
rith._board[(4, 6)] = pyramid_odd
rith._board[(7, 4)] = Circle(16, Player.even)

# move
## even
assert rith._has_moved == False
assert rith.do_move(Move((4, 4), (3, 5)))
assert rith._has_moved == True
assert rith._board[(4, 4)] == NONE_PIECE
assert rith._board[(3, 5)] == piece_C4
assert rith.turn == Player.even
assert rith.do_move(DONE_MOVE)
assert rith.turn == Player.odd
## odd
assert rith.do_move(Move((7, 7), (6, 6)))
assert not rith.do_move(Move((6, 6), (5, 5))) # cannot move multiple times
assert rith.do_move(DONE_MOVE)
## even
assert not rith.do_move(Move((6, 4), (6, 6))) # blocked
assert len(rith._board.prisoners_held_by_odd) == 0
assert len(rith._board.prisoners_held_by_even) == 0
assert rith.do_move(Take((6, 4), (6, 6), piece_C9_))
assert len(rith._board.prisoners_held_by_odd) == 0
assert len(rith._board.prisoners_held_by_even) == 1
assert rith.do_move(Move((6, 4), (6, 6))) # now unblocked
assert len(rith._board.prisoners_held_by_odd) == 0
assert len(rith._board.prisoners_held_by_even) == 1
assert rith.do_move(Take([(3, 5), (6, 6)], (4, 6), Triangle(36, Player.odd))) # C4*T9 = T36_
assert len(rith._board.prisoners_held_by_odd) == 0
assert len(rith._board.prisoners_held_by_even) == 2
assert rith._board[(4, 6)] == Pyramid(154, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    # Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
assert not rith.do_move(Drop(1, (3, 1))) # already made a move this turn
assert rith.do_move(DONE_MOVE)
## odd
assert rith.do_move(Move((4, 6), (4, 4)))
assert rith.do_move(DONE_MOVE)
## even
assert not rith.do_move(Drop(2, (3, 1))) # not at backrow
assert rith.do_move(Drop(1, (3, 1)))
assert len(rith._board.prisoners_held_by_odd) == 0
assert len(rith._board.prisoners_held_by_even) == 1
assert rith.do_move(Take((7, 4), (4, 4), Square(64, Player.odd)))
assert len(rith._board.prisoners_held_by_odd) == 0
assert len(rith._board.prisoners_held_by_even) == 2
assert rith.do_move(DONE_MOVE)
## odd

## game 2
pyramid_even = Pyramid(61, Player.even, pieces=[
    Square(36, Player.even),
    # Square(25, Player.even),
    Triangle(16, Player.even),
    Triangle(9, Player.even),
    # Circle(4, Player.even),
    # Circle(1, Player.even),
    ])
pyramid_odd = Pyramid(190, Player.odd, pieces=[
    Square(64, Player.odd),
    Square(49, Player.odd),
    Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
settings = {
    'taking.addition.marches': True,
}
rith = Rith(settings=settings)
rith._board = RithBoard(16, 8) # blank it
rith._board.prisoners_held_by_even = [Triangle(49, Player.odd)]
rith._board[(5, 8)] = pyramid_odd
rith._board[(4, 7)] = Triangle(72, Player.even)
rith._board[(3, 6)] = Circle(8, Player.even)
rith._board[(7, 5)] = Square(28, Player.even)
rith._board[(4, 2)] = Square(121, Player.even)
rith._board[(5, 2)] = pyramid_even

## even
assert rith.do_move(Drop(0, (6, 1)))
assert rith.do_move(DONE_MOVE)
## odd
assert rith.do_move(Move((5, 8), (4, 5)))
assert rith.do_move(DONE_MOVE)
## even
# By addition/subtraction, the even player can take S64_ using T72-C8,
# S49_ using S121-T72, or T36_ using C8+S28, or some combination.
assert rith.do_move(Take([(3, 6), (4, 7)], (4, 5), Square(64, Player.odd)))
assert not rith.do_move(Take([(3, 6), (4, 7)], (4, 5), Square(64, Player.odd))) # already taken
assert rith.do_move(Take([(4, 2), (4, 7)], (4, 5), Square(49, Player.odd)))
assert rith.do_move(Take([(3, 6), (7, 5)], (4, 5), Triangle(36, Player.odd)))
assert rith._board[(4, 5)] == Pyramid(41, Player.odd, pieces=[
    # Square(64, Player.odd),
    # Square(49, Player.odd),
    # Triangle(36, Player.odd),
    Triangle(25, Player.odd),
    Circle(16, Player.odd),
    ])
assert rith.do_move(DONE_MOVE)
assert rith.turn == Player.odd
## odd
assert rith.do_move(Move((4, 5), (4, 3)))
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.odd)
assert rith.do_move(Take((4, 3), (5, 2), Triangle(16, Player.even)))
# rith.do_move(DECLARE_VICTORY_MOVE)
# assert not rith.terminal(Player.odd)

rith_2 = copy.deepcopy(rith)
assert not rith_2.terminal(Player.odd)
assert not rith_2._victory_declared
rith_2.do_move(DECLARE_VICTORY_MOVE) # TODO: have specified version
assert rith_2.terminal(Player.odd)
assert rith_2._victory_declared
## game over

rith.settings['victory.take_pyramid_first'] = True
assert not rith.terminal(Player.odd)
assert not rith._victory_declared
rith.do_move(DECLARE_VICTORY_MOVE)
assert not rith.terminal(Player.odd) # because even's pyramid not taken
assert not rith._victory_declared

assert rith.do_move(DONE_MOVE)
# even
assert rith.do_move(DONE_MOVE)
# odd


assert len(rith._board.prisoners_held_by_odd) == 1
assert len(rith._board.prisoners_held_by_even) == 3
rith._board[(8, 2)] = Square(45, Player.odd) # by capture
pyramid_even_2 = Pyramid(45, Player.even, pieces=[
    Square(36, Player.even),
    Triangle(9, Player.even),
    ])
assert rith.do_move(Take((8, 2), (5, 2), pyramid_even_2)) # take the entire thing
assert len(rith._board.prisoners_held_by_odd) == 3
assert PieceName.pyramid not in [p.name for p in rith._board.prisoners_held_by_odd]
assert len(rith._board.prisoners_held_by_even) == 3
assert rith._board[(5, 2)] == NONE_PIECE
