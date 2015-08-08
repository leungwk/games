"""
Define the Conga game objects, agents, logic, and state.
"""

from collections import namedtuple, defaultdict
import itertools
import random
import copy
import math
import datetime
import sys
import os

from games.common.board import Board
from games.common.state import State

from games.search.conga import heuristic_1
from games.common.agent import Agent
from games.common.arena import Arena

from games.common.agent import RandomAgent
from games.search.search import one_ply_lookahead_terminal

from games.common.agent import MonteCarloTreeSearchAgent
from games.common.agent import AlphaBetaAgent as AlphaBetaAgentCommon

from games.conga.cell import Cell, Player

DATA_DIR = 'data/'
CONGA_OUT_DIR = DATA_DIR +'out/conga/'

Move = namedtuple('Move', ['src', 'dest']) # should be a class to enforce that fields should be a 2-tuples
INVALID_MOVE = Move(None, None)

class CongaBoard(Board):
    def __str__(self):
        def _pad(s): # pad to 3
            if 2 == len(s):
                return ' {}'.format(s)
            if 1 == len(s):
                return ' {} '.format(s)
            return s

        acc_tot = ''
        heading = '\t ' +''.join([' {}  '.format(str(row)) for row in range(1, self.ncols +1)])
        acc_tot += heading +'\n' # headings
        for col in range(self.nrows, 0, -1):
            acc_row = '{}\t'.format(col)
            for row in range(1, self.ncols +1):
                coord = (row, col)
                cell = self._board[coord]
                if cell.num == 0:
                    str_cell = '|   '
                else:
                    str_cell = '|' +str(_pad(str(cell)))
                acc_row += str_cell
            acc_tot += '\t' +'+---'*self.ncols +'+\n'
            acc_tot += acc_row +'|\n'
        acc_tot += '\t' +'+---'*self.ncols +'+\n'
        acc_tot += heading +'\n' # headings
        return acc_tot


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
        self._board = CongaBoard(nrows, ncols, lambda: Cell(num=0, player=Player.none))
        self._board[(1, 4)] = Cell(num=10, player=Player.black)
        self._board[(4, 1)] = Cell(num=10, player=Player.white)
        self.turn = Player.black
        self.num_ply = 0


    def __hash__(self):
        return hash((self.turn, self._board))


    def __eq__(self, other):
        return (self._board == other._board) and (self.turn == other.turn)


    def __ne__(self, other):
        return not self.__eq__(other)


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
        self.num_ply += 1


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


class AlphaBetaAgent(AlphaBetaAgentCommon):
    def decision(self, conga):
        ## Perform a one-ply lookahead before alpha-beta proper, a necessary step because alphabeta will not necessarily select the best move for 'max' (if root) given how 'min' is supposed to decide.
        ## For instance, if Max is root, even if there exists a winning move for Max in the next ply, Min would evaluate it as -Inf. As long as other moves exist > -Inf, Max would select those other moves, because the resultant state is evaluated from Min's perspective (which is a losing state). Hence the need for a 1-ply lookahead.
        move_1ply = one_ply_lookahead_terminal(conga, self.colour)
        if move_1ply is not None:
            return move_1ply
        return super().decision(conga)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--pylab', default='') # remove from python-mode arguments
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    parser.add_argument('--no-verbose', dest='no_verbose', action='store_true')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--explore-depth', type=int, default=4)
    parser.add_argument('--black', type=str, default='PlayerAgent')
    parser.add_argument('--white', type=str, default='PlayerAgent')
    parser.add_argument('--num-games', type=int, default=100)
    parser.add_argument('--no-arena-output-results', dest='arena_output_results', action='store_true')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    if args.output_dir is None:
        if not os.path.exists(CONGA_OUT_DIR):
            os.makedirs(CONGA_OUT_DIR)
        output_dir = CONGA_OUT_DIR
    else:
        output_dir = args.output_dir

    kwargs = {
        'seed': args.seed,
        'verbose': not args.no_verbose,
        'num_games': args.num_games,
        'arena_output_results': not args.arena_output_results,
        'output_dir': output_dir,
        }

    agent_kwargs = {
        'seed': args.seed,
        'invalid_move': INVALID_MOVE,
        'heuristic': heuristic_1,
        'debug': args.debug,
        'explore_depth': args.explore_depth,
        'capacity_transposition_table': int(1e6),
        }

    black = eval(args.black)
    white = eval(args.white)
    arena = Arena(
        lambda: Conga(),
        lambda: black(Player.black, **agent_kwargs),
        lambda: white(Player.white, **agent_kwargs),
        **kwargs)
    arena.play()
