"""
Define the Conga game objects, agents, logic, and state.
"""

from collections import namedtuple, defaultdict
from enum import Enum
import itertools
import random
import copy
import math
import datetime
import sys

from common.board import Board
from common.state import State

from search.conga import heuristic_1
from search.alphabeta import alphabeta
from common.agent import Agent
from common.arena import Arena

from common.agent import RandomAgent
from search.search import one_ply_lookahead_terminal

from search.mcts import UCTNode, MonteCarloTreeSearch

DATA_DIR = 'data/'

Move = namedtuple('Move', ['src', 'dest']) # should be a class to enforce that fields should be a 2-tuples
INVALID_MOVE = Move(None, None)

class Cell(object):
    def __init__(self, num, player):
        self.num = num
        self.player = player


    def __eq__(self, other):
        return (self.num == other.num) and \
          (self.player == other.player)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        return '{}{}'.format(self.num, self.player)


    def __repr__(self):
        return 'Cell(num={num}, player={player})'.format(num=self.num, player=repr(self.player))


class Player(Enum):
    """Define the allowed players as a type"""

    invalid = 0
    black = 1
    white = 2
    none = 3

    def __str__(self):
        if self.value == 0:
            return '?'
        elif self.value == 1:
            return 'B'
        elif self.value == 2:
            return 'W'
        elif self.value == 3:
            return ' '
        else:
            return '!'


    def __repr__(self):
        if self.value == 0:
            return 'Player.invalid'
        elif self.value == 1:
            return 'Player.black'
        elif self.value == 2:
            return 'Player.white'
        elif self.value == 3:
            return 'Player.none'
        else:
            return 'Player.invalid' # filler


    @staticmethod
    def opponent(player):
        if player == Player.black:
            opponent = Player.white
        elif player == Player.white:
            opponent = Player.black
        elif player == Player.invalid:
            opponent = Player.invalid
        elif player == Player.none:
            opponent = Player.none # unsure what would happen...
        else:
            raise ValueError("Unknown value: {}".format(player))
        return opponent


_invalid_cell = Cell(num=-1, player=Player.invalid)


class Conga(State):
    """Define the game logic and state.

    4x4 default. Black moves first.
    """
    ## do not modify
    _move_lines = [
        Move((1, 4), (2, 4)), # horizontal
        Move((1, 3), (2, 3)),
        Move((1, 2), (2, 2)),
        Move((1, 1), (2, 1)),
        Move((1, 4), (1, 3)), # vertical
        Move((2, 4), (2, 3)),
        Move((3, 4), (3, 3)),
        Move((4, 4), (4, 3)),
        Move((1, 4), (2, 3)), # \
        Move((1, 1), (2, 2)), # /
        ]

    def __init__(self, nrows=4, ncols=4):
        self._board = Board(nrows, ncols, lambda: Cell(num=0, player=Player.none))
        self._board[(1, 4)] = Cell(num=10, player=Player.black)
        self._board[(4, 1)] = Cell(num=10, player=Player.white)
        self.turn = Player.black


    def is_legal_move(self, move):
        """Check whether the seeds in src can be moved to the coord of dest"""
        coord_src, coord_dest = move
        if not self._board.is_valid_coord(coord_src) or \
          not self._board.is_valid_coord(coord_dest):
            return False

        if coord_src == coord_dest: # for cases of weird player input
            return False

        cell_src, cell_dest = self._board[coord_src], self._board[coord_dest]

        if cell_src.player in [Player.invalid, Player.none]:
            return False

        if cell_dest.player in [Player.invalid]:
            return False

        if cell_src.player != self.turn:
            return False # cannot move opponent's piece

        if ((cell_src.player == Player.black) and \
            (cell_dest.player == Player.white)) or \
           ((cell_src.player == Player.white) and \
            (cell_dest.player == Player.black)): # has players and is mismatched
            return False

        if cell_src.num <= 0:
            return False

        ## check if adjacent
        s_x, s_y = coord_src
        d_x, d_y = coord_dest
        return (abs(s_x -d_x) <= 1) and (abs(s_y -d_y) <= 1)


    def _get_legal_moves(self, coord):
        """Get player's legal moves starting from coord.

        A move is legal if, for the player at coord, the destination is
        on the board, and is empty or has a seed of the same colour as player.

        Output not necessarily ordered.
        """
        if not self._board.is_valid_coord(coord):
            return []

        cell = self._board[coord]

        if cell.player in [Player.invalid, Player.none]:
            return []

        if cell.num <= 0:
            return []

        ##
        acc_mov = []
        for coord_nei in self._board.keys_neighbours(coord):
            if self._board[coord_nei].player not in [cell.player, Player.none]:
                continue
            acc_mov.append(coord_nei)
        return acc_mov


    def get_moves(self, player):
        return self._get_player_legal_moves(player)


    def _get_player_legal_moves(self, player):
        """Yield all legal moves for player"""
        for coord_src, cell in self._board.items():
            if cell.player != player:
                continue
            for coord_dest in self._get_legal_moves(coord_src):
                yield Move(coord_src, coord_dest)


    def _iter_line(self, move):
        """Return the line of legal moves for player at src in direction dest"""
        if not self.is_legal_move(move):
            return

        cell_src = self._board[move.src]
        for cell_cur in self._board.values_vec(move):
            if cell_cur.player not in [cell_src.player, Player.none]:
                break
            yield cell_cur


    def do_move(self, move):
        """is destructive of board and player"""
        self.sow_seeds(move)


    def do_moves(self, moves):
        """Convenience function for testing"""
        for move in moves:
            self.sow_seeds(move)


    def sow_seeds(self, move):
        """Update the board with move from src to dest"""
        if not self.is_legal_move(move):
            return
        ## at least one hole after src is empty

        ## first hole
        _iter = self._iter_line(move)
        ## sow
        for idx_seed, cell_cur in enumerate(_iter):
            if idx_seed == 0:
                rem_seeds = cell_cur.num
                player_src = cell_cur.player
                cell_src = cell_cur
                ## clean up later, otherwise it affects the iteration, which replies on the state of the board prior to any moves
                continue
            avail_seeds = min(idx_seed, rem_seeds)
            cell_cur.num += avail_seeds
            rem_seeds -= avail_seeds
            cell_cur.player = player_src
            if rem_seeds <= 0:
                break
        else:
            ## drop the remaining seeds into the current hole
            cell_cur.num += rem_seeds
        ## clean up
        cell_src.num = 0
        cell_src.player = Player.none
        self.turn = self.opponent(self.turn)


    def opponent(self, player):
        return Player.opponent(player)


    def _is_line_formed(self):
        ## horizontal, vertical, or diagonal
        for move in self._move_lines:
            num_base = 0
            for idx, cell in enumerate(self._board.values_vec(move)):
                if cell.num == 0:
                    break
                if idx == 0:
                    num_base = cell.num
                    continue
                if cell.num != num_base:
                    break
            else: # winner
                return True
        return False


    def terminal(self, player):
        """Check if a terminal state for player. ie. did player win?"""
        ## not using self.turn because cannot assume alternating turns generally

        res = self._is_line_formed()
        if res:
            return True

        ## check if opponent has no more moves
        opponent = self.opponent(player)

        for _ in self.get_moves(opponent):
            return False # opponent has at least one, so not terminal
        return True


    def area_count(self, player):
        """Count the number of cells taken up by player"""
        area_count = 0
        for _, cell in self._board.items():
            if cell.player == player:
                area_count += 1
        return area_count


    def spanning_tree(self, coord):
        """Return a spanning tree for player at coord"""
        if not self._board.is_valid_coord(coord):
            return {}

        cell = self._board[coord]
        if cell.player not in [Player.white, Player.black]:
            return {}

        base_player = cell.player
        base_opponent = self.opponent(base_player)

        open_set = set([coord]) # coords to explore
        closed_set = set() # coords previously explored
        tree = defaultdict(list) # technically a directed tree

        while open_set:
            cur_coord = open_set.pop() # because arbitrary, neither depth nor breadth first
            cur_player = self._board[cur_coord].player
            if cur_player == base_opponent:
                continue # discard
            ## cur_player is either base_player or none

            closed_set.add(cur_coord)
            for neighbour_coord in self._board.keys_neighbours(cur_coord):
                if neighbour_coord in closed_set:
                    continue # don't revisit a coord
                if neighbour_coord in open_set:
                    continue # will be visited eventually; need not check 2+ times
                if self._board[neighbour_coord].player != base_opponent:
                    open_set.add(neighbour_coord)
                    tree[cur_coord].append(neighbour_coord)
                    if neighbour_coord not in tree:
                        tree[neighbour_coord] = [] # because leaves should have a node
        return dict(tree)


class PlayerAgent(Agent):
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        for key, value in kwargs.items():
            if key =='invalid_move':
                self.invalid_move = value


    def decision(self, conga):
        move = self.invalid_move
        while not conga.is_legal_move(move):
            try:
                src_in = input('src move (x,y): ')
                if src_in == 'exit':
                    sys.exit(0)
                dest_in = input('dest move (x,y): ')
                if dest_in == 'exit':
                    sys.exit(0)
                coord_src = eval('({})'.format(src_in))
                coord_dest = eval('({})'.format(dest_in))
                int(coord_src[0])
                int(coord_src[1])
                int(coord_dest[0])
                int(coord_dest[1])
                move = Move(coord_src, coord_dest)
            except SystemExit as se:
                raise se
            except:
                continue # try again
            if (coord_src in conga._board) and (self.colour != conga._board[coord_src].player):
                move = self.invalid_move
        return move


class AlphaBetaAgent(Agent):
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        self.explore_depth = 4
        self.seed = None
        for key, value in kwargs.items():
            if key == 'explore_depth':
                self.explore_depth = value
            elif key == 'invalid_move':
                self.invalid_move = value
            elif key == 'seed':
                self.seed = value
        self.heuristic = heuristic_1
        self.alphabeta = alphabeta
        

    def decision(self, conga):
        ## Perform a one-ply lookahead before alpha-beta proper, a necessary step because alphabeta will not necessarily select the best move for 'max' (if root) given how 'min' is supposed to decide.
        ## For instance, if Max is root, even if there exists a winning move for Max in the next ply, Min would evaluate it as -Inf. As long as other moves exist > -Inf, Max would select those other moves, because the resultant state is evaluated from Min's perspective (which is a losing state). Hence the need for a 1-ply lookahead.
        ## skips the costlier alphabeta() if successful, but a drag if not
        move_1ply = one_ply_lookahead_terminal(conga, self.colour)
        if move_1ply is not None:
            return move_1ply

        ## alphabeta proper
        neginf = float('-Inf')
        posinf = float('Inf')
        explore_depth = self.explore_depth
        ret_val, ret_move = self.alphabeta(
            conga, neginf, posinf, explore_depth, self.colour, "max", self.heuristic, self.invalid_move)
        if ret_move == self.invalid_move:
            ## because the search starts with "max", it means all eventual moves will lead to a terminal state (-inf), because "min" will choose only victory states
            ## it might also return something if using ">=" rather than ">" (see the code), but this will create needless moves
            return random.sample([m for m in conga.get_moves(self.colour)], 1)[0] # at least return something rather than invalid
        return ret_move


    def params(self):
        res = super().params()
        res.update({
            'explore_depth': self.explore_depth,
            'heuristic': self.heuristic.__name__,
            'seed': self.seed,
            })
        return res


class MonteCarloTreeSearchAgent(Agent):
    """An aheuristic and asymmetric approximation to minimax. 2 player version"""
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        self.n_iter = int(1e3)
        self.hold_tree = False
        for key, value in kwargs.items():
            if key == 'invalid_move':
                self.invalid_move = value
            elif key == 'n_iter':
                self.n_iter = value
            elif key == 'hold_tree':
                self.hold_tree = value
        self.search = MonteCarloTreeSearch(self.n_iter)


    def decision(self, root_state):
        root_node = UCTNode(parent=None, state=root_state, move=self.invalid_move, player=self.colour)

        node = root_node
        for _ in range(self.n_iter):
            ## "non-terminal" means there is at least 1 move for node.player, ...
            new_node = self.search.tree_policy(node)
            delta = self.search.default_policy(new_node)
            self.search.backup(new_node, delta)
        if self.hold_tree:
            self.root_node = root_node # hold onto the tree (for testing only)
        return self.search.best_child(root_node, 0).move


    def params(self):
        res = super().params()
        res.update({'n_iter': self.n_iter})
        return res


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--path-output', type=str, default=None)
    parser.add_argument('--pylab', default='') # remove from python-mode arguments
    parser.add_argument('--no-verbose', dest='no_verbose', action='store_true')
    parser.add_argument('--black', type=str, default='AlphaBetaAgent')
    parser.add_argument('--white', type=str, default='PlayerAgent')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    kwargs = {
        'seed': args.seed,
        'verbose': not args.no_verbose,
        }

    n_iter = 100
    for _ in range(n_iter):
        black = eval(args.black)
        white = eval(args.white)
        arena = Arena(
            Conga(),
            black(Player.black, invalid_move=INVALID_MOVE, seed=args.seed),
            white(Player.white, invalid_move=INVALID_MOVE, seed=args.seed),
            **kwargs)
        arena.play()
        if args.path_output is None:
            path_output = DATA_DIR +'out/conga/arena.' +datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        else:
            path_output = args.path_output
        arena.output_results(path_output)
