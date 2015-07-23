from games.conga.conga import Move, Cell, Conga, Player, Agent, RandomAgent, AlphaBetaAgent, _invalid_cell
from games.common.board import Board

#### ================================================================
#### Cell
#### ================================================================
coord = (3,2)
cell_1 = Cell(num=0, player=Player.none)
cell_2 = Cell(num=0, player=Player.none)
assert cell_1 == cell_2
cell_3 = Cell(num=1, player=Player.white)
assert cell_1 != cell_3
assert str(cell_3) == '1W'

#### ================================================================
#### Player
#### ================================================================

#### ================================================================
#### Conga
#### ================================================================

## __init__
conga = Conga()
assert conga._board[(4, 1)] == Cell(num=10, player=Player.white)
assert conga._board[(2, 2)] == Cell(num=0, player=Player.none)


## is_legal_move
assert conga.is_legal_move(Move((1, 4), (1, 3)))
assert not conga.is_legal_move(Move((1, 4), (2, 2))) # not adjacent
assert not conga.is_legal_move(Move(None, (2, 2)))


## _get_legal_moves
coord = (1, 4)
assert set(conga._get_legal_moves(coord)) == set([(1, 3), (2, 3), (2, 4)])
assert not set(conga._get_legal_moves(coord)) == set([(1, 3), (2, 4)])
assert set(conga._get_legal_moves((None, None))) == set([])



## get_moves / get_player_legal_moves
assert set(conga.get_moves(Player.black)) == set([
    ((1, 4), (1, 3)),
    ((1, 4), (2, 3)),
    ((1, 4), (2, 4))
    ])
assert set(conga.get_moves(Player.invalid)) == set([])


## _iter_line
move = Move((1, 4), (2, 4))
for lhs, rhs in zip(conga._iter_line(move), (
    Cell(num=10, player=Player.black),
    Cell(num=0, player=Player.none),
    Cell(num=0, player=Player.none),
    Cell(num=0, player=Player.none),
    )):
    assert lhs == rhs
assert set(conga._iter_line(Move(None, (2, 2)))) == set([])


## do_move / sow_seeds
import copy
conga_base = copy.deepcopy(conga)
conga.do_move(Move((1, 4), (2, 4))) # LR
conga_base._board[(1, 4)] = Cell(num=0, player=Player.none)
conga_base._board[(2, 4)] = Cell(num=1, player=Player.black)
conga_base._board[(3, 4)] = Cell(num=2, player=Player.black)
conga_base._board[(4, 4)] = Cell(num=7, player=Player.black)
assert conga_base._board == conga._board

output = list(conga.get_moves(Player.black))
expected = [
    ((2, 4), (1, 4)),
    ((2, 4), (1, 3)),
    ((2, 4), (2, 3)),
    ((2, 4), (3, 3)),
    ((2, 4), (3, 4)), # can move to a hole with the same colour
    #
    ((3, 4), (2, 4)),
    ((3, 4), (2, 3)),
    ((3, 4), (3, 3)),
    ((3, 4), (4, 3)),
    ((3, 4), (4, 4)),
    #
    ((4, 4), (3, 4)),
    ((4, 4), (3, 3)),
    ((4, 4), (4, 3)),
    ]
assert len(output) == len(expected)
assert set(output) == set(expected)


conga.do_move(Move((4, 1), (4, 2))) # right
conga_base._board[(4, 1)] = Cell(num=0, player=Player.none)
conga_base._board[(4, 2)] = Cell(num=1, player=Player.white)
conga_base._board[(4, 3)] = Cell(num=9, player=Player.white)
assert conga_base._board == conga._board

## area_count
assert 3 == conga.area_count(Player.black)
assert 2 == conga.area_count(Player.white)




### terminal_state
conga = Conga()
## line formed
conga._board[(1, 4)] = Cell(num=0, player=Player.none)
conga._board[(4, 1)] = Cell(num=0, player=Player.none)
conga._board[(1, 4)] = Cell(num=4, player=Player.black)
conga._board[(2, 3)] = Cell(num=1, player=Player.white)
conga._board[(3, 3)] = Cell(num=1, player=Player.white)
conga._board[(4, 3)] = Cell(num=1, player=Player.white)
conga._board[(2, 2)] = Cell(num=2, player=Player.black)
conga._board[(3, 2)] = Cell(num=2, player=Player.black)
conga._board[(4, 2)] = Cell(num=2, player=Player.black)
conga._board[(4, 1)] = Cell(num=7, player=Player.white)
assert not conga.terminal(Player.black)
assert not conga.terminal(Player.white)
conga.do_move(Move((1, 4), (1, 3))) # down
## /both/ are true because Conga does not track whose "turn" it is
## (maybe it should)
assert conga.terminal(Player.black)
assert conga.terminal(Player.white)




## opponent has no moves
conga = Conga()
## line formed
conga._board[(1, 4)] = Cell(num=0, player=Player.none)
conga._board[(3, 1)] = Cell(num=2, player=Player.black)
conga._board[(3, 2)] = Cell(num=6, player=Player.black)
conga._board[(4, 2)] = Cell(num=2, player=Player.black)
assert conga.terminal(Player.black)
assert not conga.terminal(Player.white)
assert len(list(conga.get_moves(Player.white))) == 0



## spanning_tree
conga = Conga()
conga._board[(1, 4)] = Cell(num=0, player=Player.none)
conga._board[(4, 1)] = Cell(num=0, player=Player.none)
conga._board[(1, 3)] = Cell(num=1, player=Player.black)
conga._board[(1, 2)] = Cell(num=3, player=Player.black)
conga._board[(2, 2)] = Cell(num=4, player=Player.black)
conga._board[(2, 1)] = Cell(num=2, player=Player.black)
conga._board[(3, 4)] = Cell(num=1, player=Player.white)
conga._board[(3, 3)] = Cell(num=1, player=Player.white)
conga._board[(3, 2)] = Cell(num=1, player=Player.white)
conga._board[(3, 1)] = Cell(num=5, player=Player.white)
conga._board[(4, 1)] = Cell(num=2, player=Player.white)
assert 7+1 == len(conga.spanning_tree((2, 1)))
assert 10+1 == len(conga.spanning_tree((4, 1)))


conga = Conga()
conga._board[(1, 4)] = Cell(num=0, player=Player.none)
conga._board[(4, 1)] = Cell(num=0, player=Player.none)
conga._board[(1, 1)] = Cell(num=1, player=Player.white)
conga._board[(2, 1)] = Cell(num=1, player=Player.black)
conga._board[(3, 1)] = Cell(num=2, player=Player.white)
conga._board[(1, 2)] = Cell(num=1, player=Player.white)
conga._board[(2, 2)] = Cell(num=1, player=Player.white)
conga._board[(3, 2)] = Cell(num=1, player=Player.white)
conga._board[(1, 3)] = Cell(num=9, player=Player.black)
conga._board[(2, 3)] = Cell(num=1, player=Player.white)
conga._board[(3, 3)] = Cell(num=1, player=Player.white)
conga._board[(4, 3)] = Cell(num=1, player=Player.white)
conga._board[(3, 4)] = Cell(num=1, player=Player.white)
