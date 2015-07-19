from conga import Player, Conga, Move, INVALID_MOVE, AlphaBetaAgent
from search.conga import heuristic_1
import copy

# taken from test_mcts.py
## win in 1-ply
base_conga = Conga()
moves = [Move(src, dest) for src,dest in [
    ((1, 4), (2, 3)),
    ((4, 1), (4, 2)),
    ((3, 2), (2, 2)),
    ((4, 3), (3, 2)),
    ((2, 2), (1, 3)),
    ((4, 2), (4, 1)),
    ]]
base_conga.do_moves(moves)



## black (alphabeta) has a victory hole at (1, 4) with Move((1, 3), (1, 4)). It shouldn't miss it.
agent_ab = AlphaBetaAgent(
    Player.black,
    invalid_move=INVALID_MOVE,
    explore_depth=4,
    )
conga = copy.deepcopy(base_conga)
move = agent_ab.decision(conga)
assert move == Move((1, 3), (1, 4))



## white (alphabeta) allows a victory hole at (1, 4), and should do any move that prevents it
agent_ab = AlphaBetaAgent(
    Player.white,
    invalid_move=INVALID_MOVE,
    explore_depth=4,
    )
conga = copy.deepcopy(base_conga)
conga.turn = Player.white

val_before = heuristic_1(conga, Player.white)
move = agent_ab.decision(conga)
conga.do_move(move)
val_after = heuristic_1(conga, Player.white)
assert val_after > val_before
