from conga import Move, Cell, Board, Conga, Player, Agent, RandomAgent, AlphaBetaAgent


## TODO:
# _get_opponent
# alphabeta


#### ================================================================
#### Cell
#### ================================================================
coord = (3,2)
cell_1 = Cell(num=0, player=Player.none)
cell_2 = Cell(num=0, player=Player.none)
assert cell_1 == cell_2
cell_3 = Cell(num=0, player=Player.white)
assert cell_1 != cell_3

#### ================================================================
#### Player
#### ================================================================

#### ================================================================
#### Board
#### ================================================================

## __init__
nrows = 5
ncols = 3
board = Board(nrows=nrows, ncols=ncols)
coord = (3,2)
assert board[coord] == Cell(num=0, player=Player.none)
assert board[(10,10)] == Board._invalid_cell

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




board[(2, 4)] = Cell(num=2, player=Player.black)
move = Move((1, 3), (2, 4))
res = board.iter_vec(move)
assert list(res) == [
    Cell(num=0, player=Player.none),
    Cell(num=2, player=Player.black),
    Cell(num=0, player=Player.none),
    ]



## get_neighbours
assert set(board.get_neighbours((1,5))) == set([
    (1,4),
    (2,4),
    (2,5),
    ])

#### ================================================================
#### Conga
#### ================================================================

## __init__
conga = Conga()
assert conga._board[(4, 1)] == Cell(num=10, player=Player.white)
assert conga._board[(2, 2)] == Cell(num=0, player=Player.none)
assert conga._board[(-1, 1)] == Cell(num=-1, player=Player.invalid)



# cell = conga._board[(1, 4)]
# TODO: add cases for invalid items
coord = (1, 4)
assert set(conga._get_legal_moves(coord)) == set([(1, 3), (2, 3), (2, 4)])
assert not set(conga._get_legal_moves(coord)) == set([(1, 3), (2, 4)])


## get_player_legal_moves
## _iter_board
assert set(conga._get_player_legal_moves(Player.black)) == set([
    ((1, 4), (1, 3)),
    ((1, 4), (2, 3)),
    ((1, 4), (2, 4))
    ])



assert conga.is_legal_move(Move((1, 4), (1, 3)))
assert not conga.is_legal_move(Move((1, 4), (2, 2)))

# ## test the method, even though cell_2 is not a current Cell in the Board
# cell_2 = Cell(num=10, player=Player.black)
# assert not conga.is_legal_move(coord, cell_2)



## test _iter_line
move = Move((1, 4), (2, 4))
conga._iter_line(move) == [
    Cell(num=10, player=Player.black),
    Cell(num=0, player=Player.none),
    Cell(num=0, player=Player.none),
    Cell(num=0, player=Player.none),
    ]



## test move (ie. sow_seeds)
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

assert 3 == conga.area_count(Player.black)
assert 2 == conga.area_count(Player.white)



# conga_base = Conga()
# assert conga_base.player_curr == Player.black
# conga_base.do_move(Move((1, 4), (1, 3))) # down
# assert conga_base.player_curr == Player.white
# conga_base.do_move(Move((4, 1), (3, 1)))
# conga_base.do_move(Move((1, 2), (1, 1)))


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

## spanning tree
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



conga = Conga()
conga._board[(1, 4)] = Cell(num=0, player=Player.none)
conga._board[(4, 1)] = Cell(num=0, player=Player.none)
#
conga._board[(1, 1)] = Cell(num=0, player=Player.none)
conga._board[(2, 1)] = Cell(num=7, player=Player.black)
conga._board[(3, 1)] = Cell(num=0, player=Player.none)
conga._board[(4, 1)] = Cell(num=0, player=Player.none)
conga._board[(1, 2)] = Cell(num=1, player=Player.black)
conga._board[(2, 2)] = Cell(num=2, player=Player.white)
conga._board[(3, 2)] = Cell(num=2, player=Player.white)
conga._board[(4, 2)] = Cell(num=0, player=Player.none)
conga._board[(1, 3)] = Cell(num=0, player=Player.none)
conga._board[(2, 3)] = Cell(num=2, player=Player.white)
conga._board[(3, 3)] = Cell(num=0, player=Player.none)
conga._board[(4, 3)] = Cell(num=1, player=Player.white)
conga._board[(1, 4)] = Cell(num=1, player=Player.black)
conga._board[(2, 4)] = Cell(num=2, player=Player.white)
conga._board[(3, 4)] = Cell(num=1, player=Player.black)
conga._board[(4, 4)] = Cell(num=1, player=Player.white)

# TODO: tests of Agent, Arena


agent_ab = AlphaBetaAgent(Player.black)
# black -white
assert (4 -6)/10. == agent_ab._score_area_count(conga, Player.black)
sb, sc = agent_ab._score_border_concentration(conga, Player.black)
assert ((2+1+1+1) -(2+1+1))/16. == sb
assert ((3) -(0))/3. == sc
## these ought to be symmetric?
assert -(4 -6)/10. == agent_ab._score_area_count(conga, Player.white)
sb, sc = agent_ab._score_border_concentration(conga, Player.white)
assert -((2+1+1+1) -(2+1+1))/16. == sb
assert -((3) -(0))/3. == sc



agent_ab.decision(conga)









# conga = Conga()
# agent_ab = AlphaBetaAgent(Player.black)
# agent_ab.decision(conga)
