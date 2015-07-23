from games.conga import Player, Conga, Move, INVALID_MOVE, MonteCarloTreeSearchAgent

n_iter = int(1e2)
conga = Conga()
agent_mcts = MonteCarloTreeSearchAgent(
    Player.black,
    invalid_move=INVALID_MOVE,
    n_iter=n_iter,
    hold_tree=True,
    )
move = agent_mcts.decision(conga)
assert conga.is_legal_move(move) # beginning of the game, so there should be at least one legal move
assert n_iter == agent_mcts.search.root_node.visits
assert n_iter == sum([node.visits for node in agent_mcts.search.root_node.child_nodes])



## win in 1-ply
n_iter = int(1e3)
agent_mcts = MonteCarloTreeSearchAgent(
    Player.black,
    invalid_move=INVALID_MOVE,
    n_iter=n_iter,
    hold_tree=True,
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

## black (MCTS) has a victory hole at (1, 4) with Move((1, 3), (1, 4)). It shouldn't miss it.
move = agent_mcts.decision(conga)
assert move == Move((1, 3), (1, 4)) # TODO: set rng
