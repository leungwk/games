"""
Define the Conga game objects, agents, and logic.
"""

from collections import namedtuple, defaultdict
from enum import Enum
import itertools
import random
import copy
import math
import datetime
import json
import sys

from common.board import Board

# import os
DATA_DIR = 'data/'

# Cell = namedtuple('Cell', ['num', 'player', 'coord'])
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


_invalid_cell = Cell(num=-1, player=Player.invalid)



class Game(object):
    """abstract base class?"""

    def do_move(self, move):
        pass

    def get_moves(self, player):
        pass

    def terminal(self, player):
        pass


class Conga(object): # TODO: inherit from Game
    """

    4x4 default.
    Black moves first.
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
        # ## these should only be used internally for stats tracking
        # self.player_prev = Player.white # even though the beginning, pretend it was white
        # self.player_curr = Player.black
        # ## each cell contains the number of seeds and player, and "0" if nothing
        # ## for stats
        # self.move_hist = [] # (player,move); measured from starting position


    def is_legal_move(self, move):
        """Check whether the seeds in src can be moved to the coord of dest"""
        # if type(move) != type(Move):
        #     raise TypeError('{} is not of type Move'.format(move))
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
        on the board, and is empty or has a seed of the same player as
        player.

        Not necessarily ordered.
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

        try:
            cell_src = self._board[move.src]
        except AttributeError:
            import pdb; pdb.set_trace() # TODO: remove
        for cell_cur in self._board.values_vec(move):
            if cell_cur.player not in [cell_src.player, Player.none]:
                break
            yield cell_cur


    def do_move(self, move):
        """is destructive of board and player"""
        self.sow_seeds(move)
        ## swap players
        # self.move_hist.append( (self.player_curr, move) )
        # tmp_prev = self.player_prev
        # self.player_prev = self.player_curr
        # self.player_curr = tmp_prev


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
        ## won't work because it needs to read the generator?
        # next(_iter) # skip over the src # wrong
        # cell_src = self._board[coord_src]
        # rem_seeds = cell_src.num
        # player_src = cell_src.player
        # self._board[coord_src].num = 0
        # self._board[coord_src].player = Player.none
        # cell_cur = cell_src
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
            # cell_prev = cell_cur
            if rem_seeds <= 0:
                break
        else:
            ## drop the remaining seeds into the current hole
            cell_cur.num += rem_seeds
        ## clean up
        cell_src.num = 0
        cell_src.player = Player.none


    def _get_opponent(self, player):
        if player == Player.black:
            opponent = Player.white
        elif player == Player.white:
            opponent = Player.black
        elif player == Player.invalid:
            opponent = Player.invalid
        elif player == Player.none:
            opponent = Player.none # unsure what would happen...
        return opponent


    def terminal(self, player):
        """Check if a terminal state for player. ie. did player win?"""

        ## horizontal, vertical, or diagonal
        lines = self._move_lines
        for move in lines:
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

        ## check if opponent has no more moves
        opponent = self._get_opponent(player)

        for _ in self.get_moves(opponent):
            return False # opponent has at least one, so not terminal
        return True


    def area_count(self, player):
        """Counts number of cells taken up by player"""
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
        base_opponent = self._get_opponent(base_player)

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


class Agent(object):
    """Base class for common properties and methods of Agents"""

    def __init__(self, colour):
        self.colour = colour


    def decision(self, board):
        pass


    def _score_area_count(self, conga, player):
        ## area count (in [1,10])
        area_count_player = conga.area_count(player)
        opponent = conga._get_opponent(player)
        area_count_opponent = conga.area_count(opponent)
        score_area_count = (area_count_player -area_count_opponent)/10.
        return score_area_count


    def _score_border_concentration(self, conga, player):
        ## corner, side, center -ness
        ## concentration of stones (separate out >= 3 and \lt 3 conditions)
        ## assuming a 4x4 board
        borderness_player = borderness_opponent = 0
        concentration_player = concentration_opponent = 0
        for coord_src, cell_src in conga._board.items():
            cell_player = cell_src.player
            if cell_player not in [Player.black, Player.white]:
                continue
            cell_opponent = conga._get_opponent(player)
            ## border in [0,16]
            if coord_src in [(1, 1), (1, 4), (4, 1), (4, 4)]: # corners
                if player == cell_player:
                    borderness_player += 2
                else:
                    borderness_opponent += 2
            elif coord_src in [(2, 2), (2, 3), (3, 2), (3, 3)]: # center
                pass
            else: # side
                if player == cell_player:
                    borderness_player += 1
                else:
                    borderness_opponent += 1
            ## concentration (in [0,3])
            ## tuned when number of stones adds up to 10
            if 4 <= cell_src.num <= 5:
                if player == cell_player:
                    concentration_player += 1
                else:
                    concentration_opponent += 1
            elif cell_src.num >= 6:
                if player == cell_player:
                    concentration_player += 3
                else:
                    concentration_opponent += 3
        # borderness_player /= 16.
        # borderness_opponent /= 16.
        score_borderness = (borderness_player -borderness_opponent)/16.
        # concentration_player /= 3.
        # concentration_opponent /= 3.
        score_concentration = (concentration_player -concentration_opponent)/3.
        return score_borderness, score_concentration


    def heuristic(self, conga, player):
        """Score how 'good' the current board is for player.

        How much area does player take up?
        How much area does the opponent potentially take up?

        ====
        assuming the root player was max player? (there's something strange that it doesn't account for whether player is max or min)

        16 points per feature

        (why input player? because search requires taking opponent's view. However, it will ignore whose /turn/ it is, as set in the Game board)

        Assuming if good for player, is bad for opponent? (hence also calculate for opponent those features)
        """
        ## all heuristics variables should be within [-1,1] (or [0,1] if assuming the opponent provides the opposite half), and the weight will adjust this
        ## TODO: use [-1,1] (assuming symmetric; everything is wrt to current player)
        weight_area = 8
        weight_ratio_avail_moves = 8 # probably somewhat correlates with area
        weight_border = -8
        weight_concentration = -8
        ## shapes
        weight_victory_hole = 32*2

        ## near terminal check
        player_legal_moves = list(conga.get_moves(player))
        if not player_legal_moves:
            return float('-Inf')

        opponent = conga._get_opponent(player)
        opponent_legal_moves = list(conga.get_moves(opponent))
        if not opponent_legal_moves:
            return float('Inf')

        score_area_count = self._score_area_count(conga, player)

        tot_moves = len(player_legal_moves) +len(opponent_legal_moves)
        ratio = 1.0*len(player_legal_moves)/len(opponent_legal_moves)
        score_ratio_avail_moves = min(1, ratio/2.) if ratio >= 1 else -min(1, 1./ratio/2.)

        #### shape heuristics
        ## "victory hole": good if player's turn (also would be caught by 1-ply lookahead)
        ## check all directions
        score_victory_hole = 0
        for move in conga._move_lines: # starts at the edge, so will cover the entire line
            num_empty = num_black = num_white = 0
            seeds = 0 # check for same number
            coord_hole = None
            coord_cell_list = [c for c in conga._board.items_vec(move)]
            for coord, cell in coord_cell_list:
                if cell.player == Player.none:
                    coord_hole = coord
                    num_empty += 1
                    if num_empty >= 2:
                        break # no line
                elif cell.player == Player.black:
                    num_black += 1
                elif cell.player == Player.white:
                    num_white += 1
                ## does all holes have 0 or the same number of seeds?
                if not seeds:
                    seeds = cell.num
                elif seeds != cell.num:
                    break # no line
            else: # a line found
                ## TODO: this doesn't make sense if the seeds >= 2, since neighbours can put in at most 1, unless it is the edge
                ## num_empty should == 1, because if it were 0, then it should be game over, and it is supposed to break for >= 2
                ## ... but then again, this heuristic should work on /all/ board positions
                ## hole should be defined
                inline_coords, _ = zip(*coord_cell_list)
                if coord_hole is None:
                    return float('-inf') # because it is player's turn, the previous move was the opponent's, and the opponent's move created a line victory
                ##
                for coord_nei in conga._board.keys_neighbours(coord_hole):
                    ## skip those in the line
                    if coord_nei in inline_coords:
                        continue
                    cell_nei = conga._board[coord_nei]
                    if seeds != cell_nei.num:
                        continue

                    if conga._get_opponent(player) == cell_nei.player:
                        score_victory_hole = -1 # bad for current player
                    elif player == cell_nei.player:
                        score_victory_hole = +1
                    break # exit outermost loop, since done
                ## TODO: if there are non-neighbours of the hole

        score_borderness, score_concentration = self._score_border_concentration(conga, player)

        term_area = weight_area * score_area_count
        term_ratio_avail_moves = weight_ratio_avail_moves * score_ratio_avail_moves
        ## TODO: shouldn't it be bad for a player to be too much on the border, or too concentrated?
        term_borderness = weight_border * score_borderness
        term_concentration = weight_concentration * score_concentration
        term_victory_hole = weight_victory_hole * score_victory_hole

        return term_area +term_ratio_avail_moves +term_borderness +term_concentration +term_victory_hole


    def params(self):
        """Agent specific params that affect its behaviour"""
        return {}


class RandomAgent(Agent):
    """"""
    def decision(self, conga):
        moves = list(conga.get_moves(self.colour))
        if not moves:
            return INVALID_MOVE # TODO: error?
        return random.sample(moves, 1)[0]


class PlayerAgent(Agent):
    """"""
    def decision(self, conga):
        ## assume for now that user will input valid
        move = INVALID_MOVE
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
                move = INVALID_MOVE
        return move


class AlphaBetaAgent(Agent):
    """\alpha-\beta search is minimax with pruning, a kind of branch and bound. 2 player version"""
    def __init__(self, colour, **kwargs):
        super().__init__(colour)
        self.explore_depth = 4
        for key, value in kwargs.items():
            if key == 'explore_depth':
                self.explore_depth = value
        

    def decision(self, conga):
        """"""
        ## TODO: refactor out (put into Agent)
        ## 1-ply lookahead (the closest to being "obvious", or "common sense")
        ## also skips the costlier alphabeta()
        moves = conga.get_moves(self.colour)
        for move in moves:
            new_conga = copy.deepcopy(conga)
            new_conga.do_move(move)
            if self.heuristic(new_conga, self.colour) == float('Inf'): # ie. is winning state
                return move
            if new_conga.terminal(self.colour):
                return move

        ## alphabeta proper
        neginf = float('-Inf')
        posinf = float('Inf')
        explore_depth = self.explore_depth
        ret_val, ret_move = self.alphabeta(
            conga, neginf, posinf, explore_depth, self.colour, "max")
        if ret_move == INVALID_MOVE:
            ## because the search starts with "max", it means all eventual moves will lead to a terminal state (-inf), because "min" will choose only victory states
            ## it might also return something if using ">=" rather than ">" (see the code), but this will create needless moves
            return random.sample([m for m in conga.get_moves(self.colour)], 1)[0] # at least return something rather than invalid
        return ret_move


    def alphabeta(self, conga, alpha, beta, depth, player, mm):
        if conga.terminal(player) or \
           depth == 0:
            return (self.heuristic(conga, player), INVALID_MOVE) # invalid move

        curr_move = INVALID_MOVE
        moves = conga.get_moves(player)
        for move in moves:
            new_conga = copy.deepcopy(conga)
            new_conga.do_move(move)
            # self.explore_count += 1

            opponent = conga._get_opponent(player)
            ret_val, ret_move = self.alphabeta(
                new_conga, alpha, beta, depth -1, opponent, "max" if mm == "min" else "min")
            if mm == "max":
                if ret_val > alpha: # '>=' causes wrong move to be selected (and it should update only on improvements)
                    curr_move = move
                alpha = max(alpha, ret_val)
                if alpha >= beta: # value of adversery has now been exceeded, so no need to search further
                    # self.prune_count += len(moves) -moves.index(move)
                    return (beta, curr_move) # pruning
#                alpha = max(alpha,ret_val)

            else: # is "min"
                if ret_val < beta: # '<=' causes wrong move to be selected
                    curr_move = move
                beta = min(beta, ret_val)
                if beta <= alpha:
                    # self.prune_count += len(moves) -moves.index(move)
                    return (alpha, curr_move) # pruning
#                beta = min(beta,ret_val)

        if mm == "max":
            return (alpha, curr_move)
        else: # is "min"
            return (beta, curr_move)


    def params(self):
        return {
            'explore_depth': self.explore_depth,
            }


class Arena(object):
    """"""
    def __init__(self, agent_black, agent_white, **kwargs):
        self.conga = Conga()
        self.agent_black = agent_black(Player.black)
        # self.agent_white = AlphaBetaAgent(Player.white)
        self.agent_white = agent_white(Player.white)
        self.move_hist = []
        ##
        self.seed = None
        # self.verbose = False
        for key, value in kwargs.items():
            if key == 'seed':
                self.seed = value
            # elif key == 'verbose':
            #     self.verbose = value


    def play(self):
        print("Game start: ")
        print(self.conga._board)
        print()

        random.seed(self.seed)

        self.start_time_game = int(datetime.datetime.now().strftime('%s'))
        self.winner = Player.invalid

        while True:
            ## black
            if self.conga.terminal(self.agent_black.colour):
                winner = self.agent_black.colour
                break
            move = self.agent_black.decision(self.conga)
            self.conga.do_move(move)
            self.move_hist.append((self.agent_black.colour, move))
            print(self.conga._board)
            print()
            if self.conga.terminal(self.agent_black.colour):
                winner = self.agent_black.colour
                break

            ## white
            if self.conga.terminal(self.agent_white.colour):
                winner = self.agent_white.colour
                break
            move = self.agent_white.decision(self.conga)
            self.conga.do_move(move)
            self.move_hist.append((self.agent_white.colour, move))
            print(self.conga._board)
            print()
            if self.conga.terminal(self.agent_white.colour):
                winner = self.agent_white.colour
                break

        self.end_time_game = int(datetime.datetime.now().strftime('%s'))
        self.winner = winner
        print('winner: {}'.format(winner))

        ## collect and output stats
        self.num_moves = len(self.move_hist)
        ## params


    def output_results(self, path_output):
        out_dict = {
            'start_time_game': self.start_time_game,
            'end_time_game': self.end_time_game,
            ## TODO: use custom name for the case of the same agent
            'black': self.agent_black.__class__.__name__,
            'white': self.agent_white.__class__.__name__,
            'params_black': self.agent_black.params(),
            'params_white': self.agent_white.params(),
            'winner': str(self.winner),
            'num_moves': self.num_moves,
            'move_hist': [(str(pla), mov.src, mov.dest) for pla, mov in self.move_hist],
            'seed': self.seed,
            }
        with open(path_output, 'w') as pile:
            json.dump(out_dict, pile)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--path-output', type=str, default=None) # `date +%Y-%m-%dT%H%M%S`
    parser.add_argument('--pylab', default='') # remove from python-mode arguments
    parser.add_argument('--verbose', type=bool, default=True)
    parser.add_argument('--black', type=str, default='AlphaBetaAgent')
    parser.add_argument('--white', type=str, default='PlayerAgent')
    args = parser.parse_args()

    kwargs = {
        'seed': args.seed,
        # 'verbose': args.verbose,
        }

    n_iter = 100
    for _ in range(n_iter):
        black = eval(args.black)
        white = eval(args.white)
        arena = Arena(black, white, **kwargs)
        arena.play()
        if args.path_output is None:
            path_output = DATA_DIR +'out/conga/arena.' +datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        else:
            path_output = args.path_output
        arena.output_results(path_output)