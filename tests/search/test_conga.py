from games.conga.conga import Move, Cell, Conga, Player
from games.search.conga import _score_area_count, _score_border_concentration

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

# black -white
assert (4 -6)/10. == _score_area_count(conga, Player.black)
sb, sc = _score_border_concentration(conga, Player.black)
assert ((2+1+1+1) -(2+1+1))/16. == sb
assert ((3) -(0))/3. == sc
## these ought to be symmetric?
assert -(4 -6)/10. == _score_area_count(conga, Player.white)
sb, sc = _score_border_concentration(conga, Player.white)
assert -((2+1+1+1) -(2+1+1))/16. == sb
assert -((3) -(0))/3. == sc
