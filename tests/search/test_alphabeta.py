from conga import Player, Conga, Move, INVALID_MOVE, AlphaBetaAgent

# taken from test_mcts.py
## win in 1-ply
agent_ab = AlphaBetaAgent(
    Player.black,
    invalid_move=INVALID_MOVE,
    explore_depth=4,
    )
conga = Conga()
moves = [Move(src, dest) for src,dest in [
    ((1, 4), (2, 3)),
    ((4, 1), (4, 2)),
    ((3, 2), (2, 2)),
    ((4, 3), (3, 2)),
    ((2, 2), (1, 3)),
    ((4, 2), (4, 1)),
    ]]
conga.do_moves(moves)

## black (alphabeta) has a victory hole at (1, 4) with Move((1, 3), (1, 4)). It shouldn't miss it.
move = agent_ab.decision(conga)
assert move == Move((1, 3), (1, 4))
