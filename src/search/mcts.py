import math
import random
import copy

class UCTNode(object):
    def __init__(self, parent, state, move, player):
        ## tree
        self.visits = 0
        self.payout = 0
        ## as moves are tried they should move into child_nodes
        ## untried_moves unioned with the move of each child_node should equal the space of all possible (legal) moves
        self.child_nodes = [] # leaf/inner in the sense of mcts, not end of game
        self.untried_moves = [x for x in state.get_moves(player)] # all moves # TODO: randomize this
        self.parent = parent # None for root
        ## game
        self.move = move # "incoming action a(v)" (None for root)
        self.state = state # s(v)
        ##
        ## these need to be frozen for this configuration to work
        self.player = player # whose turn is it for this state?
        self.terminal = state.terminal(player)
        ## a game terminal state is a uctnode (search-tree) leaf, but not all leafs are necessarily a game terminal state (ie. if there are untried_moves, and no child_nodes)


    def __str__(self):
        src, dest = self.move if self.move else (None, None)
        return '{},{},{},({},{})'.format(self.visits, self.payout, self.player, src, dest)


    @staticmethod
    def walk_tree(root):
        def _walk(node):
            cur = str(node)
            if not node.child_nodes:
                return [cur, []]
            acc = []
            for child in node.child_nodes:
                acc.append(_walk(child))
            return [cur, acc]
        return _walk(root)


    @staticmethod
    def best_path(root):
        ## TODO: would this make sense given that it only accounts for payout? It also, in the limit, assumes perfect play by the opponent
        acc = [root]
        if not root.child_nodes:
            return acc
        #
        arg, val = None, float('-inf')
        for child in root.child_nodes:
            if child.payout >= val:
                arg = child
                val = child.payout
        acc.extend(UCTNode.best_path(arg))
        return acc


class MonteCarloTreeSearch(object):
    """Implementation of MCTS.

    From algo 2 in /A survey of monte carlo tree search methods/ (2012), Browne et al.
    """

    def __init__(self, n_iter, invalid_move, **kwargs):
        self.n_iter = n_iter
        self.invalid_move = invalid_move
        self.seed = kwargs.get('seed', None)
        self.hold_tree = kwargs.get('hold_tree', False)
    ## assuming only two players, and that one turn is one ply


    def expand(self, node):
        move = node.untried_moves.pop()
        new_state = copy.deepcopy(node.state)
        new_state.do_move(move) # now new player should be indicated in player_curr
        new_player = new_state.turn
        new_node = UCTNode(parent=node, state=new_state, move=move, player=new_player)
        node.child_nodes.append(new_node)
        return new_node


    def best_child(self, node, const=1./math.sqrt(2)):
        arg, val = None, float('-inf')
        ## node should always have at least one child_node, due to tree_policy::while not node.terminal
        #
        for nc in node.child_nodes:
            term_1 = 1.0*nc.payout/nc.visits if nc.visits > 0 else float('inf')
            ## in a sense, n dominates log n, so the denom should have priority
            if nc.visits > 0:
                if node.visits > 0:
                    term_2 = const*math.sqrt(2.0 * math.log(node.visits) / nc.visits)
                else:
                    term_2 = float('-inf')
            else:
                term_2 = float('inf')
            tot = term_1 +term_2
            if tot >= val: # '=' because it should select /a/ node (even if all are -inf)
                arg = nc
                val = tot
        return arg


    def tree_policy(self, node):
        while not node.terminal:
            if node.untried_moves:
                return self.expand(node)
            else:
                new_node = self.best_child(node)
                if new_node is None:
                    return node
                else:
                    node = new_node
                ## will return None if node.child_nodes is empty, which can only occur if (1) expand(node) is never called, or (2) tree_policy(None) is called, or (3) if untried_moves is [], which can occur if player is trapped. For the cases where self.player has no more moves, yet has no untried_moves, though one cannot say if this is a game terminal, it is the end of the search-tree search
        return node


    def default_policy(self, node):
        orig_player = node.parent.player # who played move to get to this node? It is not the node.player because, for instance, if from the root there is a winning move, because in a one turn one ply game, the root would take such a move, but the child node would have the opposing player, in this function one counts whether the original mover (ie. root) reached a terminal, or ...
        ## consider the opposite case, where root makes a blunder move. The opponent should then make the winning move. The score for the /opponent/ should be ... # TODO: what should it be?
        ## as well, in a game with no draws (and one turn = one ply), on the first iteration, if not terminal(cur_player), but cur_player has no moves, then ... # TODO: default_policy might be more game specific than I realize
        cur_player = orig_player
        new_state = copy.deepcopy(node.state) # TODO: move deepcopy into state objects
        while not new_state.terminal(cur_player): # if false, then cur_player lost because of previous move ... but is this only for turn-by-turn games?
            cur_player = new_state.turn
            moves = [x for x in new_state.get_moves(cur_player)]
            if not moves:
                return -1 if cur_player == orig_player else +1 # TODO: is this correct?
            move = random.sample(moves, 1)[0]
            new_state.do_move(move)
        return +1 if cur_player == orig_player else -1 # TODO: is this correct?


    def backup(self, node, delta):
        while node is not None:
            node.visits += 1
            node.payout += delta
            node = node.parent


    def uct_search(self, root_state, player):
        root_node = UCTNode(parent=None, state=root_state, move=self.invalid_move, player=player)

        node = root_node
        for _ in range(self.n_iter):
            ## "non-terminal" means there is at least 1 move for node.player, ...
            new_node = self.tree_policy(node)
            delta = self.default_policy(new_node)
            self.backup(new_node, delta)
        if self.hold_tree:
            self.root_node = root_node # hold onto the tree (for testing only)
        return self.best_child(root_node, 0).move
