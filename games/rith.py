"""
Define the rithmomachia game objects, agents, logic, and state.
"""

from enum import Enum
from common.board import Board
from common.state import State
from functools import partial
import sys

import itertools
from itertools import islice, combinations, zip_longest
from collections import defaultdict

from common.agent import Agent, RandomAgent
from common.arena import Arena

from settings.rith import settings_fulke_1, settings_custom_1# , _setup_fulke_1, _setup_fulke_3

from common.agent import MonteCarloTreeSearchAgent

import datetime
import os

DATA_DIR = 'data/'
RITH_OUT_DIR = DATA_DIR +'out/rith/'

class Action(object):
    """Object for one of the kinds of allowed actions in rithmomachia.

    move: move piece from src to dest
    take: src takes piece at dest
    drop: place piece num from player's prisoners onto dest
    vict: declare victory
    done: declare turn over
    """
    def __init__(self, src, dest, **kwargs):
        self.src = src
        self.dest = dest
        for key, value in kwargs.items():
            if key == 'type':
                self.type = value

    def __repr__(self):
        return "Action({src}, {dest}, type='{type}')".format(src=self.src, dest=self.dest, type=self.type)


    def __eq__(self, other):
        return (self.src == other.src) and \
          (self.dest == other.dest) and \
          (self.type == other.type)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return hash((self.src, self.dest, self.type))


class Move(Action):
    def __init__(self, src, dest):
        super().__init__(src, dest, type='move')


    def __repr__(self):
        return 'Move({src}, {dest})'.format(src=self.src, dest=self.dest)


class Take(Action):
    """Similar to Move, but specify what piece to take.

    If multiple takes at the same dest are required (ex. pyramid),
    specify multiple Take objects instead.
    """
    def __init__(self, src, dest, piece):
        super().__init__(src, dest, type='take')
        self.piece = piece


    def __repr__(self):
        return 'Take({src}, {dest}, {piece})'.format(src=self.src, dest=self.dest, piece=repr(self.piece))


    def __hash__(self):
        res = super().__hash__()
        return hash((res, self.piece))


    def __eq__(self, other):
        res = super().__eq__(other)
        if not res:
            return res
        return self.piece == other.piece


class Drop(Action):
    def __init__(self, src, dest):
        super().__init__(src, dest, type='drop')


    def __repr__(self):
        return 'Drop({src}, {dest})'.format(src=self.src, dest=self.dest)



DECLARE_VICTORY_MOVE = Action(None, None, type='vict')
DONE_MOVE = Action(None, None, type='done')

INVALID_MOVE = Action(None, None, type=None)
INVALID_COORD = (None, None)

# TODO: upper case as these are constants
# not actually used by piece; for checking taking by siege
deltas_cross = set([
    # orthogonal ('+')
    (+1, 0),
    (0, +1),
    (-1, 0),
    (0, -1),
])
deltas_xshape = set([
    # diagonal ('x')
    (+1, +1),
    (-1, +1),
    (-1, -1),
    (+1, -1),
])


## for checking taking by line adjacency (addition/subtraction)
deltas_line_adjacency = [
    [(-1, 0), (+1, 0)],
    [(-1, -1), (+1, +1)],
    [(0, -1), (0, +1)],
    [(-1, +1), (+1, -1)],
]


## for checking victory progressions
delta_right_angle = [
    [(+1, 0), (0, +1)], # ^-
    [(-1, 0), (0, +1)], # -^
    [(-1, 0), (0, -1)], # -v
    [(+1, 0), (0, -1)], # v-
]

delta_squares = [
    ## these need to be consecutive to simplify the code
    [(+1, 0), (+1, +1), (0, +1)], # <|
    [(0, +1), (-1, +1), (-1, 0)], # v-
    [(-1, 0), (-1, -1), (0, -1)], # |>
    [(0, -1), (+1, -1), (+1, 0)], # >|

]




## marching, aka. motion, regular movement,
marches_circle = deltas_xshape

marches_triangle = set([
    # orthogonal
    (+2, 0),
    (0, +2),
    (-2, 0),
    (0, -2),
])

marches_square = set([
    # orthogonal
    (+3, 0),
    (0, +3),
    (-3, 0),
    (0, -3),
])

## flying, aka. irregular movement
flying_circle = set([])
flying_triangle = set([
    (+2, -1),
    (+2, +1),
    (+1, +2),
    (-1, +2),
    (-2, +1),
    (-2, -1),
    (-1, -2),
    (+1, -2),
])
flying_square = set([
    (+3, -1),
    (+3, +1),
    (+1, +3),
    (-1, +3),
    (-3, +1),
    (-3, -1),
    (-1, -3),
    (+1, -3),
])



class Player(Enum):
    """Define the allowed players as a type"""

    invalid = -1
    none = 0
    even = 1 # white
    odd = 2 # black

    def __str__(self):
        if self.value == -1:
            return '?'
        elif self.value == 0:
            return '_'
        elif self.value == 1:
            return 'E'
        elif self.value == 2:
            return 'O'
        else:
            return '!'


    def __repr__(self):
        if self.value == -1:
            return 'Player.invalid'
        elif self.value == 0:
            return 'Player.none'
        elif self.value == 1:
            return 'Player.even'
        elif self.value == 2:
            return 'Player.odd'
        else:
            return 'Player.error'


    @staticmethod
    def opponent(player):
        if player == Player.even:
            opponent = Player.odd
        elif player == Player.odd:
            opponent = Player.even
        elif player == Player.invalid:
            opponent = Player.invalid
        elif player == Player.none:
            opponent = Player.none
        else:
            raise ValueError("Unknown value: {}".format(player))
        return opponent


class PieceName(Enum):
    """Define the allowed pieces as a type"""

    invalid = -1
    none = 0
    circle = 1
    triangle = 2
    square = 3
    pyramid = 4

    def __str__(self):
        if self.value == -1:
            return '?'
        elif self.value == 0:
            return '_'
        elif self.value == 1:
            return 'C'
        elif self.value == 2:
            return 'T'
        elif self.value == 3:
            return 'S'
        elif self.value == 4:
            return 'P'
        else:
            return '!'


    def __repr__(self):
        if self.value == -1:
            return 'PieceName.invalid'
        elif self.value == 0:
            return 'PieceName.none'
        elif self.value == 1:
            return 'PieceName.circle'
        elif self.value == 2:
            return 'PieceName.triangle'
        elif self.value == 3:
            return 'PieceName.square'
        elif self.value == 4:
            return 'PieceName.pyramid'
        else:
            return 'PieceName.error'


class ContainerPieces(object):
    def __init__(self, pieces):
        self.pieces = pieces


class Piece(object):
    """Define the cell of a rithmomachia board"""

    def __init__(self, num, name, colour, marches, flights):
        self.num = num # int
        self.name = name
        self.colour = colour # {Player.even, Player.odd}
        ## how the piece moves relative to a starting coordinate
        self._marches = marches
        self._flights = flights


    def __str__(self):
        return '{}{}{}'.format(self.name, self.num, '' if self.colour == Player.even else '_') # because letters for colour are too distracting


    def __eq__(self, other):
        return (self.num == other.num) and \
          (self.name == other.name) and \
          (self.colour == other.colour)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.num, repr(self.colour))


    def __hash__(self):
        return hash((self.num, self.name, self.colour))


    @property
    def marches(self):
        return self._marches


    @property
    def flights(self):
        return self._flights


    @property
    def pieces(self):
        """Convenience function to avoid separate checks for the pyramid"""
        return [self]


class Circle(Piece):
    def __init__(self, num, colour):
        super().__init__(num, PieceName.circle, colour, marches_circle, flying_circle)


class Triangle(Piece):
    def __init__(self, num, colour):
        super().__init__(num, PieceName.triangle, colour, marches_triangle, flying_triangle)


class Square(Piece):
    def __init__(self, num, colour):
        super().__init__(num, PieceName.square, colour, marches_square, flying_square)


class Pyramid(Piece):
    def __init__(self, num, colour, **kwargs):
        super().__init__(num, PieceName.pyramid, colour, set([]), set([]))
        for key, value in kwargs.items():
            if key == 'pieces':
                self._pieces = value


    def __eq__(self, other):
        res = super().__eq__(other)
        if not res:
            return res
        ## is at least a pyramid
        for p_self, p_other in zip_longest(self._pieces, other._pieces, fillvalue=[NONE_PIECE]):
            if (p_self == NONE_PIECE) or (p_other == NONE_PIECE):
                return False # unequal length since a pyramid should not contain NONE_PIECE
            res = super().__eq__(other)
            if not res:
                return False
        return True


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        res = super().__hash__()
        return hash((res, tuple(self._pieces)))


    ## override marches and flights to return all its components
    @property
    def pieces(self):
        """Convenience function to avoid separate checks for the pyramid"""
        return [self] +self._pieces # [self] because one wants to check the pyramid as a whole, in addition to its components


    ## a pyramid's marches and flights are the union of all components
    @property
    def marches(self):
        acc = set()
        for piece in self.pieces:
            acc.update(piece._marches)
        return acc


    @property
    def flights(self):
        acc = set()
        for piece in self.pieces:
            acc.update(piece._flights)
        return acc


    @staticmethod
    def remove_component(pyramid, piece):
        """Remove component piece from pyramid and return a new, updated pyramid"""
        if pyramid.name != PieceName.pyramid:
            return NONE_PIECE

        acc = []
        removed_component = None
        for comp in pyramid.pieces:
            if comp.name == PieceName.pyramid:
                continue # ignore

            if comp != piece:
                acc.append(comp)
            else:
                ## remove only one piece in case pyramid contains multiple, equal pieces
                if removed_component is None:
                    removed_component = comp
                else:
                    acc.append(comp)
        if not acc:
            return NONE_PIECE
        tot = sum([p.num for p in acc])
        return Pyramid(tot, pyramid.colour, pieces=acc)


class NonePiece(Piece):
    def __init__(self):
        super().__init__(None, '_', Player.none, set([]), set([]))

    def __str__(self):
        return '  '

NONE_PIECE = NonePiece()



class RithBoard(Board):
    def __init__(self, nrows, ncols, constructor=lambda: NONE_PIECE):
        super().__init__(nrows, ncols, constructor)
        self.prisoners_held_by_even = []
        self.prisoners_held_by_odd = []


    def __str__(self):
        def _pad(s): # pad to 5
            if 4 == len(s):
                return ' {}'.format(s)
            if 3 == len(s):
                return ' {} '.format(s)
            if 2 == len(s):
                return ' {}  '.format(s)
            return s

        acc_tot = ''
        pyramid_even = []
        pyramid_even_tot = -1
        pyramid_odd = []
        pyramid_odd_tot = -1
        heading = '\t ' +''.join(['  {}   '.format(str(row)) for row in range(1, self.ncols +1)])
        acc_tot += heading +'\n' # headings
        for col in range(self.nrows, 0, -1):
            acc_row = '{}\t'.format(col)
            for row in range(1, self.ncols +1):
                coord = (row, col)
                piece = self._board[coord]
                if piece.name == PieceName.pyramid:
                    if piece.colour == Player.even:
                        str_cell = '|  P  '
                        acc_str = pyramid_even
                        pyramid_even_tot = piece.num
                    elif piece.colour == Player.odd:
                        str_cell = '|  b  ' # inverse of 'P'
                        acc_str = pyramid_odd
                        pyramid_odd_tot = piece.num
                    for p_it in piece.pieces:
                        if p_it.name != PieceName.pyramid:
                            acc_str.append(str(p_it))
                elif piece == NONE_PIECE:
                    str_cell = '|     '
                else:
                    str_cell = '|' +str(_pad(str(piece)))
                acc_row += str_cell
            acc_tot += '\t' +'+-----'*8 +'+\n'
            acc_tot += acc_row +'|\n'
        acc_tot += '\t' +'+-----'*8 +'+\n'
        acc_tot += heading +'\n\n' # headings
        acc_tot += 'P (tot {}) = '.format(pyramid_even_tot) +' '.join(pyramid_even) +'\n'
        acc_tot += 'b (tot {}) = '.format(pyramid_odd_tot) +' '.join(pyramid_odd) +'\n'
        acc_tot += 'Even\'s prisoners: ' +' '.join([str(piece) for piece in self.prisoners_held_by_even]) +'\n'
        acc_tot += 'Odd\'s prisoners: ' +' '.join([str(piece) for piece in self.prisoners_held_by_odd]) +'\n'
        return acc_tot


    # def __str_2__(self):
    #     acc_tot = ''
    #     pyramid_white = ''
    #     pyramid_black = ''
    #     heading = '\t' +'\t'.join([str(row) for row in range(1, self.ncols +1)])
    #     acc_tot += heading +'\n' # headings
    #     for col in range(self.nrows, 0, -1):
    #         acc_row = '{}\t'.format(col)
    #         for row in range(1, self.ncols +1):
    #             coord = (row, col)
    #             piece = self._board[coord]
    #             if piece.name == PieceName.pyramid:
    #                 if piece.colour == Player.even:
    #                     str_cell = 'P '
    #                     for piece in piece.pieces:
    #                         pyramid_white += str(piece) +' '
    #                     pyramid_white += '(tot {})'.format(piece.num)
    #                 elif piece.colour == Player.odd:
    #                     str_cell = 'b ' # inverse of 'P'
    #                     for piece in piece.pieces:
    #                         pyramid_black += str(piece) +' '
    #                     pyramid_black += '(tot {})'.format(piece.num)
    #             else:
    #                 str_cell = str(piece)
    #             acc_row += str_cell +'\t' ##
    #         acc_tot += acc_row +'\n'
    #     acc_tot += heading +'\n\n' # headings
    #     acc_tot += 'P = ' +pyramid_white +'\n'
    #     acc_tot += 'b = ' +pyramid_black +'\n'
    #     acc_tot += 'White\'s prisoners: ' +' '.join([str(piece) for piece in self.white_prisoners]) +'\n'
    #     acc_tot += 'Black\'s prisoners: ' +' '.join([str(piece) for piece in self.black_prisoners]) +'\n'
    #     return acc_tot



class Rith(State):
    """Define the game logic and state.

    Even moves first.

    Disable all optional rule settings by default.
    """
    def __init__(self, **kwargs):
        self.settings = {}
        for key, value in kwargs.items():
            if key == 'settings': # game settings, to determine what rules are being used
                self.settings = value

        self._board = RithBoard(16, 8) # blank board
        if self.settings.get('board_setup', 'fulke_1') == 'fulke_1':
            self._setup_fulke_1()
        elif self.settings.get('board_setup', 'fulke_1') == 'fulke_3':
            self._setup_fulke_3()
        else:
            raise ValueError('no other initial setups supported (yet)')

        ## turn tracking
        self.turn = Player.even # to answer, "whose turn is it?"
        self._has_moved = False # marching or flying or dropping (allow only one per turn)
        self._victory_declared = False # should only be changed in do_move


    ## TODO: these should be moved to some data path
    def _setup_fulke_1(self):
        """Following /Fulke/ (1563), first kind of play (and board layout)"""
        ## white
        ## row 3
        self._board[(1, 3)] = Square(289, Player.even)
        self._board[(2, 3)] = Square(169, Player.even)
        self._board[(7, 3)] = Square(81, Player.even)
        self._board[(8, 3)] = Square(25, Player.even)
        ## row 4
        self._board[(1, 4)] = Square(153, Player.even)
        self._board[(2, 4)] = Pyramid(91, Player.even, pieces=[
            Square(36, Player.even),
            Square(25, Player.even),
            Triangle(16, Player.even),
            Triangle(9, Player.even),
            Circle(4, Player.even),
            Circle(1, Player.even),
            ])
        self._board[(3, 4)] = Triangle(49, Player.even)
        self._board[(4, 4)] = Triangle(42, Player.even)
        self._board[(5, 4)] = Triangle(20, Player.even)
        self._board[(6, 4)] = Triangle(25, Player.even)
        self._board[(7, 4)] = Square(45, Player.even)
        self._board[(8, 4)] = Square(15, Player.even)
        ## row 5
        self._board[(1, 5)] = Triangle(81, Player.even)
        self._board[(2, 5)] = Triangle(72, Player.even)
        self._board[(3, 5)] = Circle(64, Player.even)
        self._board[(4, 5)] = Circle(36, Player.even)
        self._board[(5, 5)] = Circle(16, Player.even)
        self._board[(6, 5)] = Circle(4, Player.even)
        self._board[(7, 5)] = Triangle(6, Player.even)
        self._board[(8, 5)] = Triangle(9, Player.even)
        ## row 6
        self._board[(3, 6)] = Circle(8, Player.even)
        self._board[(4, 6)] = Circle(6, Player.even)
        self._board[(5, 6)] = Circle(4, Player.even)
        self._board[(6, 6)] = Circle(2, Player.even)
        ## black
        ## row 14
        self._board[(1, 14)] = Square(49, Player.odd)
        self._board[(2, 14)] = Square(121, Player.odd)
        self._board[(7, 14)] = Square(225, Player.odd)
        self._board[(8, 14)] = Square(361, Player.odd)
        ## row 13
        self._board[(1, 13)] = Square(28, Player.odd)
        self._board[(2, 13)] = Square(66, Player.odd)
        self._board[(3, 13)] = Triangle(30, Player.odd)
        self._board[(4, 13)] = Triangle(36, Player.odd)
        self._board[(5, 13)] = Triangle(56, Player.odd)
        self._board[(6, 13)] = Triangle(64, Player.odd)
        self._board[(7, 13)] = Square(120, Player.odd)
        self._board[(8, 13)] = Pyramid(190, Player.odd, pieces=[
            Square(64, Player.odd),
            Square(49, Player.odd),
            Triangle(36, Player.odd),
            Triangle(25, Player.odd),
            Circle(16, Player.odd),
            ])
        ## row 12
        self._board[(1, 12)] = Triangle(16, Player.odd)
        self._board[(2, 12)] = Triangle(12, Player.odd)
        self._board[(3, 12)] = Circle(9, Player.odd)
        self._board[(4, 12)] = Circle(25, Player.odd)
        self._board[(5, 12)] = Circle(49, Player.odd)
        self._board[(6, 12)] = Circle(81, Player.odd)
        self._board[(7, 12)] = Triangle(90, Player.odd)
        self._board[(8, 12)] = Triangle(100, Player.odd)
        ## row 11
        self._board[(3, 11)] = Circle(3, Player.odd)
        self._board[(4, 11)] = Circle(5, Player.odd)
        self._board[(5, 11)] = Circle(7, Player.odd)
        self._board[(6, 11)] = Circle(9, Player.odd)


    def _setup_fulke_3(self):
        """Following /Fulke/ (1563), third kind of play (and board layout). Is Fulke 1 but shifted back by 2 rows"""
        ## white
        ## row 1
        self._board[(1, 1)] = Square(289, Player.even)
        self._board[(2, 1)] = Square(169, Player.even)
        self._board[(7, 1)] = Square(81, Player.even)
        self._board[(8, 1)] = Square(25, Player.even)
        ## row 2
        self._board[(1, 2)] = Square(153, Player.even)
        self._board[(2, 2)] = Pyramid(91, Player.even, pieces=[
            Square(36, Player.even),
            Square(25, Player.even),
            Triangle(16, Player.even),
            Triangle(9, Player.even),
            Circle(4, Player.even),
            Circle(1, Player.even),
            ])
        self._board[(3, 2)] = Triangle(49, Player.even)
        self._board[(4, 2)] = Triangle(42, Player.even)
        self._board[(5, 2)] = Triangle(20, Player.even)
        self._board[(6, 2)] = Triangle(25, Player.even)
        self._board[(7, 2)] = Square(45, Player.even)
        self._board[(8, 2)] = Square(15, Player.even)
        ## row 3
        self._board[(1, 3)] = Triangle(81, Player.even)
        self._board[(2, 3)] = Triangle(72, Player.even)
        self._board[(3, 3)] = Circle(64, Player.even)
        self._board[(4, 3)] = Circle(36, Player.even)
        self._board[(5, 3)] = Circle(16, Player.even)
        self._board[(6, 3)] = Circle(4, Player.even)
        self._board[(7, 3)] = Triangle(6, Player.even)
        self._board[(8, 3)] = Triangle(9, Player.even)
        ## row 4
        self._board[(3, 4)] = Circle(8, Player.even)
        self._board[(4, 4)] = Circle(6, Player.even)
        self._board[(5, 4)] = Circle(4, Player.even)
        self._board[(6, 4)] = Circle(2, Player.even)
        ## black
        ## row 16
        self._board[(1, 16)] = Square(49, Player.odd)
        self._board[(2, 16)] = Square(121, Player.odd)
        self._board[(7, 16)] = Square(225, Player.odd)
        self._board[(8, 16)] = Square(361, Player.odd)
        ## row 15
        self._board[(1, 15)] = Square(28, Player.odd)
        self._board[(2, 15)] = Square(66, Player.odd)
        self._board[(3, 15)] = Triangle(30, Player.odd)
        self._board[(4, 15)] = Triangle(36, Player.odd)
        self._board[(5, 15)] = Triangle(56, Player.odd)
        self._board[(6, 15)] = Triangle(64, Player.odd)
        self._board[(7, 15)] = Square(120, Player.odd)
        self._board[(8, 15)] = Pyramid(190, Player.odd, pieces=[
            Square(64, Player.odd),
            Square(49, Player.odd),
            Triangle(36, Player.odd),
            Triangle(25, Player.odd),
            Circle(16, Player.odd),
            ])
        ## row 14
        self._board[(1, 14)] = Triangle(16, Player.odd)
        self._board[(2, 14)] = Triangle(12, Player.odd)
        self._board[(3, 14)] = Circle(9, Player.odd)
        self._board[(4, 14)] = Circle(25, Player.odd)
        self._board[(5, 14)] = Circle(49, Player.odd)
        self._board[(6, 14)] = Circle(81, Player.odd)
        self._board[(7, 14)] = Triangle(90, Player.odd)
        self._board[(8, 14)] = Triangle(100, Player.odd)
        ## row 13
        self._board[(3, 13)] = Circle(3, Player.odd)
        self._board[(4, 13)] = Circle(5, Player.odd)
        self._board[(5, 13)] = Circle(7, Player.odd)
        self._board[(6, 13)] = Circle(9, Player.odd)


    def is_legal_move(self, move):
        """Dispatch to appropriate handler"""
        if move.type == 'move':
            return (not self._has_moved) and self._is_legal_move(move)
        elif move.type == 'take':
            return self._is_legal_take(move)
        elif move.type == 'drop':
            return (not self._has_moved) and self._is_legal_drop(move)
        elif move.type == 'vict':
            return True # it is always legal to /declare/ victory, but one might be incorrect about the state of the board
        # elif move.type == 'vict':
        #     return self.terminal(self.turn)
        elif move.type == 'done':
            return True
        # raise ValueError('Unrecognized move type: {}'.format(move.type))
        return False


    def _is_legal_drop(self, move):
        if move.type != 'drop':
            return False
        if self._has_moved:
            return False
        # if move.src is not None: # catch improperly constructed move objects
        #     return False

        # if not self._valid_move_obj(move, allow_empty_src=True):
        #     return False

        coord_dest = move.dest
        piece_dest = self._board[coord_dest]
        if piece_dest != NONE_PIECE:
            return False

        prisoners = []
        if self.turn == Player.even:
            if (coord_dest[1] == 1) and (self._board.prisoners_held_by_even):
                prisoners = self._board.prisoners_held_by_even
        elif self.turn == Player.odd:
            if (coord_dest[1] == 16) and (self._board.prisoners_held_by_odd):
                prisoners = self._board.prisoners_held_by_odd
        try:
            prisoners[move.src] # idx-0
        except IndexError:
            return False
        return True


    def _is_legal_take(self, move):
        """

        == Known rules ==

        Taking by equality/encountering: The player's and opponent's piece have the same number, and the player can reach the opponent in a regular (ie. marching) move.



        Taking by eruption (Fulke, third kind): Between the player's and opponent's piece, orthogonally or diagonally in a straight line, the number of squares k between piece and opponent inclusive, is both unoccupied, and the smaller number n times the large number m is such that nk=m.



        Taking by obsidion/oblivion/siege: A piece is blocked (at least one of these variants must be selected):

        variants:
        - all regular (ie. marching) moves of a piece are blocked by board edge or opponent pieces (Fulke, first and second kind)
        - a piece is surrounded on all orthogonal directions, or all corners (and not some mix), by board edge or opponent pieces (Fulke, third kind)



        Taking by addition/subtraction: Two of the player's pieces are, as arranged below, such that when their numbers add or subtract, the result equals the opponent's piece.

        variants:
        - piece's regular (ie. marching) movement (Fulke, first kind)
        - adjacent ("next spaces") and in a line (Fulke, second kind)
        - taking by deceit or lying wait (Fulke, third kind): any adjacency



        Taking by multiplication/division:
        - For the first kind, same as the first kind of addition/subtraction's form
        - "void spaces": number of squares between piece and opponent (exclusive) (Fulke, second kind) (assuming a clean line of sight)



        == Potential adaptations ==

        Taking by power/root:
        - (adaption of "taking by cossical signs" (Fulke, second kind))
        - Same as the first kind of addition/subtraction's form

        others
        - "void spaces" can be extended to be inclusive, and thus similar to taking by eruption.
        - "void spaces", inclusive or exclusive, can also be extended to power/root
        - power/root also uses void_spaces


        == Notes ==

        Fulke's first kind: flying moves may not take any piece

        Regarding multiple captures: If allowed and unless indicated otherwise, before a player's move the player may take the opponent either with or without removing into the opponent's place. After a player's move, the player make take only without removing into the opponent's place.
        """
        ## the use of type checks is in lieu of making src and dest a collection in all cases. For src, None corresponds to asking for a search, while a tuple is a single coord, and a list should hold 2 coord. This is how the moves are encoded.
        if (type(move.src) == tuple) and self._valid_taking_by_equality(move):
            return True
        if (type(move.src) == tuple) and self._valid_taking_by_eruption(move):
            return True
        if (move.src is None) and self._valid_taking_by_siege(move):
            return True
        if ((move.src is None) or (type(move.src) == list)) and self._valid_taking_by_addition(move):
            return True
        if ((move.src is None) or (type(move.src) == list) or self.__valid_coord_obj(move.src)) and self._valid_taking_by_multiplication(move):
            return True
        return False


    def __valid_coord_obj(self, coord):
        return (type(coord) == tuple) and \
            (len(coord) == 2) and \
            (type(coord[0]) == int) and \
            (type(coord[1]) == int)


    def _valid_move_obj(self, move, allow_empty_src=False, allow_empty_dest=False):
        coord_src, coord_dest = move.src, move.dest
        if not (allow_empty_src or self._board.is_valid_coord(coord_src)):
            return False

        if not (allow_empty_dest or self._board.is_valid_coord(coord_dest)):
            return False

        if coord_src == coord_dest: # for cases of weird player input
            return False

        if not allow_empty_src:
            piece_src = self._board[coord_src]
            if piece_src == NONE_PIECE:
                return False

        if not allow_empty_dest:
            piece_dest = self._board[coord_dest]
            if piece_dest == NONE_PIECE:
                return False

        return True


    def _valid_taking_by_equality(self, move):
        if move.type != 'take':
            return False
        if not self._valid_move_obj(move):
            return False
        if getattr(move, 'piece', None) is None:
            return False

        coord_src, coord_dest = move.src, move.dest
        piece_src, piece_dest = self._board[coord_src], self._board[coord_dest]

        coord_delta = (coord_dest[0] -coord_src[0], coord_dest[1] -coord_src[1])

        if piece_src.colour != self.turn:
            return False # cannot use opponent's piece

        if Player.opponent(piece_src.colour) != piece_dest.colour:
            return False # cannot take own piece

        for p_src in piece_src.pieces:
            allow_jump = False
            if coord_delta in p_src.flights:
                if not self.settings.get('taking.equality.flight', False):
                    continue
                allow_jump = True
                ## is a flight and such taking is enabled
            elif coord_delta in p_src.marches:
                pass
            else: # not a valid take
                continue

            ## check for a clear line of sight for marches
            if (not allow_jump) and (not self._is_empty_check(piece_src, coord_src, coord_delta, inclusive=False)):
                continue
            ## check that any number(s) match
            for p_dest in piece_dest.pieces:
                if (p_src.num == p_dest.num != None) and (move.piece == p_dest):
                    return True
        return False


    def _valid_taking_by_eruption(self, move, void_spaces=False):
        if not self.settings.get('taking.eruption', False):
            return False
        if move.type != 'take':
            return False
        if not self._valid_move_obj(move):
            return False
        if getattr(move, 'piece', None) is None:
            return False

        coord_src, coord_dest = move.src, move.dest
        piece_src, piece_dest = self._board[coord_src], self._board[coord_dest]

        if piece_src.colour != self.turn:
            return False # cannot use opponent's piece

        coord_delta = (coord_dest[0] -coord_src[0], coord_dest[1] -coord_src[1])

        it_xy = self._make_it_xy(coord_delta)
        ## check that it is orthogonal or diagonal
        dx, dy = coord_delta
        dlarge = max(abs(dx), abs(dy))
        if (0 == coord_delta[0]) or (0 == coord_delta[1]) or (abs(coord_delta[0]) == abs(coord_delta[1])):
            ## ex. if there are three spaces inclusive between player and opponent, then _cond_steps will count starting from the next space from coord_src. The delta, if valid, should give dlarge equal 2, thus it should check if there are 2 -1 = 1 spaces empty between them
            if all(self._cond_steps(dlarge -1, coord_src, it_xy)): # None is handled because it indicates it went OOB
                for p_src in piece_src.pieces:
                    ## check that it is the opponent, and that any number(s) match
                    for p_dest in piece_dest.pieces:
                        mult = dlarge +1 if not void_spaces else dlarge -1 # because counting inclusive (at both ends of the interval)
                        if ((p_src.num * mult == p_dest.num) or (p_src.num == p_dest.num * mult)) and (Player.opponent(p_src.colour) == p_dest.colour) and (p_dest == move.piece):
                            return True


    def _valid_taking_by_siege(self, move):
        if move.type != 'take':
            return False
        if move.src is not None: # catch improperly constructed move objects
            return False
        if getattr(move, 'piece', None) is None:
            return False

        if not self._valid_move_obj(move, allow_empty_src=True):
            return False

        coord_dest = move.dest # ie. piece to be taken
        piece_dest = self._board[coord_dest]

        colour_opponent = Player.opponent(piece_dest.colour)

        if piece_dest.colour == self.turn:
            return False # cannot siege one's own piece

        if self.settings.get('taking.siege.block_marches', False):
            for p_dest in piece_dest.pieces:
                if p_dest != move.piece:
                    continue
                for coord_delta in p_dest.marches:
                    dx, dy = coord_delta
                    coord_new = (coord_dest[0] +dx, coord_dest[0] +dy)
                    if not self._board.is_valid_coord(coord_new): # ie. blocked by edge of board
                        continue

                    dlarge = max(abs(dx), abs(dy))
                    it_xy = self._make_it_xy(coord_delta)
                    cond = all(self._cond_steps(dlarge, coord_dest, it_xy, cond=lambda piece: piece.colour != colour_opponent)) # False means it was the opponent, and None indicates march would have gone OOB. If cond is True, then candidate piece under siege has an out
                    if cond: # all cells not occupied by the opponent, nor blocked by board edge
                        ## therefore p_dest has at least one "out"
                        break
                else:
                    return True # at least one cell, within or at the end of each marching moves of p_dest, was blocked by the opponent or board edge, and p_dest was the piece to be taken


        if self.settings.get('taking.siege.surrounded', False):
            ### '+' and '-'
            for deltas_set in [deltas_cross, deltas_xshape]:
                for piece in self._board.values_fan(coord_dest, deltas_set): # will not return objects if OOB
                    if piece.colour != colour_opponent:
                        break
                else:
                    return True # all such surrounding pieces were the opponent or board edge

        return False


    def _is_sum_diff(self, piece_1, piece_2, piece_dest):
        return (piece_dest.num == piece_1.num +piece_2.num) or \
          (piece_dest.num == piece_1.num -piece_2.num) or \
          (piece_dest.num == -piece_1.num +piece_2.num)

    def _is_prod_quot(self, piece_1, piece_2, piece_dest):
        return (piece_dest.num == piece_1.num * piece_2.num) or \
          (piece_dest.num == piece_1.num / piece_2.num) or \
          (piece_dest.num == piece_2.num / piece_1.num)

    def _is_pow_root(self, piece_1, piece_2, piece_dest):
        return (piece_dest.num == pow(piece_1.num, piece_2.num)) or \
          (piece_dest.num == pow(piece_2.num, piece_1.num)) or \
          (piece_dest.num == pow(piece_1.num, 1/piece_2.num)) or \
          (piece_dest.num == pow(piece_2.num, 1/piece_1.num)) # all is float division


    def __taking_cond_marches(self, coord_dest, piece_dest, colour_opponent, cond, pre_found_pieces=None):
        ## find two pieces (if any) such that, if both could march into the opponent's place (piece_dest), their sum or difference equals that of the opponent (if taking by addition/subtraction), or product/quotient, or power/root (the condition cond)
        ## this code does /not/ assume all marches are limited to at most 4; it could probably do so for the rulesets that will be used. Eventually replace this with an index, or something
        ## this code does assume that only one piece per space may count towards the total two pieces.
        ## without ... specified, it will look for /any/ match in .pieces (so it will match any within pyramid)
        if (pre_found_pieces is not None) and len(pre_found_pieces) != 2:
            return False

        found_pieces = []
        for coord_cur, piece_cur_top in self._board.items():
            if piece_cur_top.colour != colour_opponent:
                continue
            ## check if piece could march unto piece_dest
            coord_cur_x, coord_cur_y = coord_cur

            acc = ContainerPieces([]) # rather than appending pieces (whether alone or in a pyramid) as they occur, defer until the end of all .pieces, so to catch the case where the pyramid can march onto piece_dest, but the whole does not form any valid taking by elementary operation, and where a component part does (and would cause bugs if .pieces for a pyramid iterates with the pyramid first (as it currently does))
            ## a property object is need for itertools.product()
            for piece_cur in piece_cur_top.pieces: # needed because, if piece_cur is a pyramid, and the total marches of pyramid do reach a given opponent piece (ex. T move), but only a S has the right value (ex. S66 -S36 = T30_), then this will not select that component of a pyramid, rather the whole pyramid
                for delta in piece_cur.marches: # note that this assumes .marches gives the marches the pieces, and all its components. It might not be a good idea to have this separate from the logic it will be used in
                    delta_x, delta_y = delta
                    coord = (coord_cur_x +delta_x, coord_cur_y +delta_y)
                    if coord != coord_dest:
                        continue
                    ## now check for a clear line of sight (more expensive) from the piece under consideration
                    if self._is_empty_check(piece_cur, coord_cur, delta, inclusive=False):
                        # found_pieces.append((coord_cur, piece_cur))
                        acc.pieces.append(piece_cur)
                        break
            if acc.pieces:
                found_pieces.append((coord_cur, acc)) # treat all pieces found here as one unit, because of only one piece per space (even if, for instance, a pyramid could contribute two valid pieces (ex. T9*C4=_36))
        if len(found_pieces) >= 2:
            ## now check the condition for any pair
            for (coord_1, piece_1), (coord_2, piece_2) in combinations(found_pieces, 2):
                for p_1, p_2, p_d in itertools.product(piece_1.pieces, piece_2.pieces, piece_dest.pieces):
                    ## check again, because the previous block of code will not handle the case where the pyramid has a delta onto the opponent's space, but the component piece (that would satisfiy cond) cannot. The above could not handle it because it would not know if all pieces have been found
                    for delta in p_1.marches:
                        delta_x, delta_y = delta
                        c_1_x, c_1_y = coord_1
                        coord = (c_1_x +delta_x, c_1_y +delta_y)
                        if coord == coord_dest:
                            can_march = True
                    if not can_march:
                        continue
                    #
                    can_march = False
                    for delta in p_2.marches:
                        delta_x, delta_y = delta
                        c_2_x, c_2_y = coord_2
                        coord = (c_2_x +delta_x, c_2_y +delta_y)
                        if coord == coord_dest:
                            can_march = True
                    if not can_march:
                        continue
                    ## now it is known that p_1 and p_2 can both march onto p_d's space
                    if pre_found_pieces is None:
                        if cond(p_1, p_2, p_d) or cond(p_2, p_1, p_d): # product() only creates all combinations in order of each collection. If cond is not commutative, it will fail
                            return True
                    else:
                        ## expecting a two element list of (coord,piece). Checking for a valid marching has already been done
                        (pre_coord_1, pre_p_1), (pre_coord_2, pre_p_2) = pre_found_pieces
                        # take permutations rather than combinations
                        if not (((coord_1 == pre_coord_1) and (coord_2 == pre_coord_2)) or \
                          ((coord_2 == pre_coord_1) and (coord_1 == pre_coord_2))):
                            continue # not at the locations specified
                        for pp1, pp2 in itertools.product(pre_p_1.pieces, pre_p_2.pieces):
                            if not (((pp1 == p_1) and (pp2 == p_2)) or \
                                    ((pp2 == p_1) and (pp1 == p_2))):
                                continue # does not match up
                            if cond(pp1, pp2, p_d) or cond(pp2, pp1, p_d): # somewhat redundant if cond is commutative
                                return True

        return False


    def _valid_taking_by_addition(self, move):
        if move.src is None:
            return self._valid_taking_by_addition_search(move)
        else:
            return self._valid_taking_by_addition_specified(move)


    def __valid_sources(self, move):
        ## for use in taking by marches with elmentary operations
        coord_dest = move.dest

        pieces_src = []
        seen_coords = set([coord_dest])
        for coord_src in move.src:
            if not self._board.is_valid_coord(coord_src):
                return []
            if coord_src in seen_coords: # all of them should be distinct
                return []
            else:
                seen_coords.add(coord_src)

            piece_src = self._board[coord_src]
            if piece_src == NONE_PIECE: # none of them should be NONE_PIECE
                return []

            pieces_src.append((coord_src, piece_src))
        if (len(pieces_src) != 2) or (len(seen_coords) != 3):
            return []
        return pieces_src


    def _valid_taking_by_addition_specified(self, move):
        pieces_src = self.__valid_sources(move)
        if not pieces_src:
            return False
        if getattr(move, 'piece', None) is None:
            return False

        coord_dest = move.dest
        piece_dest = self._board[coord_dest]
        if move.piece not in piece_dest.pieces:
            return False

        if piece_dest.colour == self.turn:
            return False # cannot take one's own piece

        colour_opponent = Player.opponent(piece_dest.colour)

        if self.settings.get('taking.addition.marches', False):
            ## need to do a similar thing to __taking_cond_marches, except without discovering pieces
            piece_dest_in = piece_dest
            if piece_dest.name == PieceName.pyramid:
                piece_dest_in = ContainerPieces([p for p in piece_dest.pieces if p == move.piece]) # pick out the exact item
            cond = self.__taking_cond_marches(coord_dest, piece_dest_in, colour_opponent, cond=self._is_sum_diff, pre_found_pieces=pieces_src)
            if cond:
                return True

        coord_dest_x, coord_dest_y = coord_dest
        if self.settings.get('taking.addition.line_adjacency', False):
            for ((d_1_x, d_1_y), (d_2_x, d_2_y)) in deltas_line_adjacency:
                new_coord_1 = (coord_dest_x +d_1_x, coord_dest_y +d_1_y)
                new_coord_2 = (coord_dest_x +d_2_x, coord_dest_y +d_2_y)
                if not ((new_coord_1 in move.src) and (new_coord_2 in move.src)): # is it one of the specified dest?
                    continue
                ## should be commutative

                piece_adj_1 = self._board.get(new_coord_1, NONE_PIECE)
                piece_adj_2 = self._board.get(new_coord_2, NONE_PIECE)
                if NONE_PIECE in [piece_adj_1, piece_adj_2]:
                    continue

                ps_list = [p for c,p in pieces_src]
                if not ((piece_adj_1 in ps_list) and (piece_adj_2 in ps_list)):
                    continue

                for p_a_1, p_a_2, p_d in itertools.product(piece_adj_1.pieces, piece_adj_2.pieces, piece_dest.pieces):
                    if self._is_sum_diff(p_a_1, p_a_2, p_d):
                        return True

        if self.settings.get('taking.addition.any_adjacency', False):
            found_pieces = [(c,p) for c,p in self._board.items_neighbours(coord_dest) if p.colour == colour_opponent]
            if len(found_pieces) >= 2:
                for (coord_1, piece_1), (coord_2, piece_2) in combinations(found_pieces, 2):
                    for p_1, p_2, p_d in itertools.product(piece_1.pieces, piece_2.pieces, piece_dest.pieces):
                        if not ((coord_1 in move.src) and (coord_2 in move.src)):
                            continue
                        ps_list = [p for c,p in pieces_src]
                        if not ((p_1 in ps_list) and (p_2 in ps_list)):
                            continue
                        if self._is_sum_diff(p_1, p_2, p_d):
                            return True
        return False


    def _valid_taking_by_addition_search(self, move):
        if move.type != 'take':
            return False
        if move.src is not None: # catch improperly constructed move objects
            return False
        if getattr(move, 'piece', None) is None:
            return False

        if not self._valid_move_obj(move, allow_empty_src=True):
            return False

        coord_dest = move.dest
        coord_dest_x, coord_dest_y = coord_dest

        piece_dest = self._board[coord_dest]

        if move.piece not in piece_dest.pieces:
            return False

        if piece_dest.colour == self.turn:
            return False # cannot take one's own piece

        colour_opponent = Player.opponent(piece_dest.colour)

        if self.settings.get('taking.addition.marches', False):
            piece_dest_in = piece_dest
            if piece_dest.name == PieceName.pyramid:
                piece_dest_in = ContainerPieces([p for p in piece_dest.pieces if p == move.piece]) # pick out the exact item
            cond = self.__taking_cond_marches(coord_dest, piece_dest_in, colour_opponent, cond=self._is_sum_diff)
            if cond:
                return True

        if self.settings.get('taking.addition.line_adjacency', False):
            ## TODO: move this type of iteration into the board
            for ((d_1_x, d_1_y), (d_2_x, d_2_y)) in deltas_line_adjacency:
                piece_adj_1 = self._board.get((coord_dest_x +d_1_x, coord_dest_y +d_1_y), NONE_PIECE)
                if (piece_adj_1 == NONE_PIECE) or (piece_adj_1.colour != colour_opponent):
                    continue
                piece_adj_2 = self._board.get((coord_dest_x +d_2_x, coord_dest_y +d_2_y), NONE_PIECE)
                if (piece_adj_2 == NONE_PIECE) or (piece_adj_2.colour != colour_opponent):
                    continue
                for p_a_1, p_a_2, p_d in itertools.product(piece_adj_1.pieces, piece_adj_2.pieces, piece_dest.pieces):
                    if self._is_sum_diff(p_a_1, p_a_2, p_d):
                        return True

        if self.settings.get('taking.addition.any_adjacency', False):
            found_pieces = [p for p in self._board.values_neighbours(coord_dest) if p.colour == colour_opponent]
            if len(found_pieces) >= 2:
                for piece_1, piece_2 in combinations(found_pieces, 2):
                    for p_1, p_2, p_d in itertools.product(piece_1.pieces, piece_2.pieces, piece_dest.pieces):
                        if self._is_sum_diff(p_1, p_2, p_d):
                            return True
        return False


    def _valid_taking_by_multiplication(self, move):
        if move.type != 'take':
            return False
        if getattr(move, 'piece', None) is None:
            return False

        ## TODO: push this into each condition, as currently src may or may not be required to be defined for each to work
        coord_dest = move.dest
        if not self._board.is_valid_coord(coord_dest):
            return False

        piece_dest = self._board[coord_dest]
        if (piece_dest == NONE_PIECE):
            return False

        if piece_dest.colour == self.turn:
            return False # cannot take one's own piece

        colour_opponent = Player.opponent(piece_dest.colour)

        if move.piece not in piece_dest.pieces:
            return False

        if self.settings.get('taking.multiplication.marches', False):
            piece_dest_in = piece_dest
            if piece_dest.name == PieceName.pyramid:
                piece_dest_in = ContainerPieces([p for p in piece_dest.pieces if p == move.piece]) # pick out the exact item
            cond = self.__taking_cond_marches(coord_dest, piece_dest_in, colour_opponent, cond=self._is_prod_quot, pre_found_pieces=None if move.src is None else self.__valid_sources(move))
            if cond:
                return True

        if self.settings.get('taking.multiplication.void_spaces', False):
            if not self.__valid_coord_obj(move.src):
                return False # catch improperly constructed move objects; tuple is intended for this, while src=None or src is a list is intended for 'taking.multiplication.marches'
                return False
            if getattr(move, 'piece', None) is None:
                return False

            # TODO: fix this hack
            was_set = True
            try:
                prev_value = self.settings['taking.eruption']
            except KeyError:
                was_set = False
            finally:
                self.settings['taking.eruption'] = True
            cond = self._valid_taking_by_eruption(move, void_spaces=True)
            if was_set:
                self.settings['taking.eruption'] = prev_value
            else:
                del self.settings['taking.eruption']
            if cond:
                return True

        return False


    def _cond_steps(self, n_steps, coord_src, delta_xy, cond=lambda piece: piece.colour == Player.none):
        """Yield, from src (exclusive) in step (delta_x, delta_y), for the next n_steps, whether the cell satisfies cond. By default check if empty. Yield None if OOB (off of board).
        """
        for idx, piece in enumerate(self._board.values_delta_xy(coord_src, delta_xy)):
            if idx > n_steps:
                break
            if idx == 0:
                continue
            yield cond(piece)
        for _ in range(n_steps -idx):
            yield None


    def _make_it_xy(self, coord_delta):
        delta_x, delta_y = coord_delta
        it_x = 1 if delta_x > 0 else (-1 if delta_x < 0 else 0)
        it_y = 1 if delta_y > 0 else (-1 if delta_y < 0 else 0)
        it_xy = (it_x, it_y)
        return it_xy


    def _is_empty_check(self, piece, coord_src, delta, inclusive=True):
        """Check if spaces from coord_src in direction it_xy are empty for n_steps (inclusive or not of the end point)"""
        it_xy = self._make_it_xy(delta)
        def __inner(piece):
            if piece.name == PieceName.circle:
                n_steps = 2 -1 if inclusive else 0
            elif piece.name == PieceName.triangle:
                n_steps = 3 -1 if inclusive else 1
            elif piece.name == PieceName.square:
                n_steps = 4 -1 if inclusive else 2
            else:
                raise ValueError("Unknown piece {}".format(piece.name))
            is_empty = all(self._cond_steps(n_steps, coord_src, it_xy)) # None would indicate it is being asked to move OOB
            return is_empty

        if piece.name == PieceName.pyramid:
            is_empty = False
            for piece in piece.pieces:
                if piece.name == PieceName.pyramid:
                    continue # because (under current rules implemented) a pyramid only moves according to its components
                if delta not in piece.marches: # (it_x, it_y) would otherwise be wrong because it doesn't match some components of the pyramid
                    continue

                if __inner(piece):
                    is_empty = True
                    break
        else:
            is_empty = __inner(piece)

        return is_empty


    def _is_legal_move(self, move):
        coord_src, coord_dest = move.src, move.dest
        if not self._board.is_valid_coord(coord_src) or \
          not self._board.is_valid_coord(coord_dest):
            return False

        if coord_src == coord_dest: # for cases of weird player input
            return False

        piece_src, piece_dest = self._board[coord_src], self._board[coord_dest]

        if piece_src.colour in [Player.invalid, Player.none]: # nothing to move
            return False

        if piece_dest != NONE_PIECE:
            return False # stronger check

        if piece_src.colour != self.turn:
            return False # cannot move opponent's piece

        # if piece_dest.colour != Player.none:
        #     ## "move and take" has been disallowed, so only empty spaces may be moved into
        #     return False

        src_x, src_y = coord_src
        dest_x, dest_y = coord_dest
        delta_x, delta_y = dest_x -src_x, dest_y -src_y
        delta = (delta_x, delta_y)

        ## check if a valid pattern under current rules
        if delta in piece_src.flights:
            move_type = 'flight'
        elif delta in piece_src.marches:
            move_type = 'march'
        else:
            return False # unrecognized

        #### flying

        if move_type == 'flight':
            ## empty at dest
            if piece_dest == NONE_PIECE:
                return True # stronger check
            ## ie. do not allow for taking by flight, not because the relevant setting has not been enabled, but rather, each Move object may only specify one ply. Thus a player (and the code) must separately specify a movement, and a taking (if any)
            return False

        #### marches

        ## if it won't change on that axis, then that coord need not be changed
        ## check if blocked (for marches), by iterating in its direction
        is_empty = self._is_empty_check(piece_src, coord_src, delta)
        return is_empty


    def terminal(self, player):
        """

        Victory conditions for Fulke's first kind:
        - The entire pyramid must be taken first (also required in his second and third kind)
        - The players pieces used in a triumph must be brought in by marches, not flights
        - Proper victories must occur in the opponent's 'half'
        - Ordering is important
        - The pieces must be arranged, with no spaces, or equidistant spaces (if spaces enabled), in a line, or a right angle
        - At least one piece in the progression must be the player's

        Variants (that are implemented):
        - any number of equi-spaces between pieces are allowed for their formation, and there must be a clear line of sight between the pieces
        - Pieces do not have to be brought it in only by marches

        Proper victories: Form arithmetic, geometrical, or harmonic ("musical") progression, or some combination
        - harmonic: a, b, c is a harmonic progression if c/a = (c-b)/(b-a)
        - note: capturing the pyramid first is required only for these kinds of victories


        Common victories, as agreed upon by the player's at the beginning of a game:
        - bodies: greater than or equal to the number of rith pieces taken by a player (irregardless of the value written)
        - goods: greater than or equal to the total sum of the value written on each piece (TODO: can this be asymmetric?)
        - quarrels: victory by goods, and that the number of digits ("characters") in all digits equal or exceeds a threshold (ex. "2" is one digit, while "49" is two digits)
        - honour: victory by goods, and the number of pieces used to make such a victory (ie. sum) is less than or equal to some threshold
        - quarrels and honour
        - (TODO: implement) standards: one standard of even is 130, and one standard of odd is 174. The victor is one who captures k of the opponent's standards, that is, the even player must capture pieces totalling 174*k, and likewise 130*k for the odd player.
        """
        ## find some kind of victory for player;
        ## different from the code where the player must declare what pieces are involved in a victory

        ## assuming the pyramid is deconstructed when taken, whether partially or fully
        ## TODO: check the code for this
        ## also assuming common victories do not require the pyramid to be taken first
        #### ================================================================
        #### common victories
        #### ================================================================

        cnt_pieces = self.settings.get('victory.bodies', 0)
        if cnt_pieces > 0:
            if player == Player.odd:
                if len(self._board.prisoners_held_by_odd) >= cnt_pieces:
                    return True
            elif player == Player.even:
                if len(self._board.prisoners_held_by_even) >= cnt_pieces:
                    return True

        def _victory_by_goods(sum_pieces, pieces):
            return sum([p.num for p in pieces]) >= sum_pieces
        sum_pieces = self.settings.get('victory.goods.num', 0)
        if sum_pieces > 0 and self.settings.get('victory.goods', False):
            if player == Player.odd:
                cond = _victory_by_goods(sum_pieces, self._board.prisoners_held_by_odd)
            elif player == Player.even:
                cond = _victory_by_goods(sum_pieces, self._board.prisoners_held_by_even)
            if cond:
                return True

        def _digitize(pieces):
            ## TODO: filter out NONE_PIECE just in case?
            return ''.join([str(p.num) for p in pieces])

        digits_pieces = self.settings.get('victory.quarrels', 0)
        if digits_pieces > 0:
            if player == Player.odd:
                pieces = self._board.prisoners_held_by_odd
            elif player == Player.even:
                pieces = self._board.prisoners_held_by_even
            if _victory_by_goods(sum_pieces, pieces):
                if len(_digitize(pieces)) >= digits_pieces:
                    return True

        cnt_pieces_victory_honour = self.settings.get('victory.honour', 0)
        if cnt_pieces_victory_honour > 0:
            for n_combo in range(1, cnt_pieces_victory_honour+1):
                if player == Player.odd:
                    prisoners = self._board.prisoners_held_by_odd
                elif player == Player.even:
                    prisoners = self._board.prisoners_held_by_even
                for piece_list in combinations(prisoners, n_combo):
                    if _victory_by_goods(sum_pieces, piece_list):
                        return True


        if self.settings.get('victory.take_pyramid_first', False):
            for piece_cur in self._board.values():
                if piece_cur.name != PieceName.pyramid:
                    continue
                if piece_cur.colour == Player.opponent(player):
                    ## opponent's pyramid still exists
                    ## (note, if the entire pyramid is taken, it cannot be dropped even if all its components can)
                    opponent_pyramid_captured = False
                    return False
            ## no opponent pyramid found

        #### ================================================================
        #### proper victories
        #### ================================================================
        if not self._victory_declared:
            return False

        def _progressions(piece_1, piece_2, piece_cur):
            for p_1, p_2, p_c in itertools.product(piece_1.pieces, piece_2.pieces, piece_cur.pieces):
                ## arithmetic
                if (p_2.num -p_c.num == p_c.num -p_1.num):
                    return True
                ## geometric
                if (p_2.num / p_c.num == p_c.num / p_1.num):
                    return True
                ## harmonic
                ## TODO: should use integer math only to avoid rounding problems
                if ((p_2.num / p_1.num)*(p_c.num -p_1.num)) == (p_2.num -p_c.num): # second term a mult to avoid any division
                    return True
            return False

        ## for each of the player's piece that is on the opponent's side of the board,
        # found_pieces = []
        for coord_cur, piece_cur in self._board.items():
            if piece_cur == NONE_PIECE:
                continue
            # if piece_cur.colour != player:
            #     continue
            ## by fulke 1,
            ## TODO: this should probably be set along with the _setup*() so to avoid any problems
            def _offside(coord):
                if player == Player.even:
                    if not coord[1] >= 9: # TODO: this might be a case to replace coord with a Coord object (use coord.y instead); it would also help with addition
                        return True
                elif player == Player.odd:
                    if not coord[1] <= 8:
                        return True
                return False
            if _offside(coord_cur):
                continue
            # found_pieces.append((coord_cur, piece_cur))
            ## find sequences of length 3
            for deltas_list in [deltas_line_adjacency, delta_right_angle]:
                for (delta_1, delta_2) in deltas_list:
                    for idx, ((coord_d1, piece_d1), (coord_d2, piece_d2)) \
                      in enumerate(zip_longest(
                          self._board.items_delta_xy(coord_cur, delta_1),
                          self._board.items_delta_xy(coord_cur, delta_2),
                          fillvalue=[INVALID_COORD, NONE_PIECE])):
                        if idx == 0:
                            continue
                        if INVALID_COORD in [coord_d1, coord_d2]:
                            break # at end of one of the lists, ie. at end of board
                        if _offside(coord_d1) or _offside(coord_d2):
                            break
                        if piece_d1 == NONE_PIECE and piece_d2 == NONE_PIECE:
                            continue # empty pieces found; there might still be some
                        ## check progression upon the first non-empty piece
                        if piece_d1 == NONE_PIECE or piece_d2 == NONE_PIECE:
                            break # not equidistant
                        ## pieces should be equidistant, in proper shape, and onside
                        if _progressions(piece_d1, piece_d2, piece_cur) and any([p.colour == player for p in [piece_d1, piece_d2, piece_cur]]):
                            return True
                        else:
                            break # do not search beyond first non-empty piece

            ## find sequences of length 4
            ## TODO: somehow merge with above
            # coord_cur_x, coord_cur_y = coord_cur
            for deltas_list in [delta_squares]:
                for (delta_1, delta_2, delta_3) in deltas_list:
                    for idx, ((coord_d1, piece_d1), (coord_d2, piece_d2), (coord_d3, piece_d3)) \
                      in enumerate(zip_longest(
                          self._board.items_delta_xy(coord_cur, delta_1),
                          self._board.items_delta_xy(coord_cur, delta_2),
                          self._board.items_delta_xy(coord_cur, delta_3),
                          fillvalue=[INVALID_COORD, NONE_PIECE])):
                        if idx == 0:
                            continue
                        if INVALID_COORD in [coord_d1, coord_d2, coord_d2]:
                            break # at end of one of the lists, ie. at end of board

                        if _offside(coord_d1) or _offside(coord_d2) or _offside(coord_d3):
                            continue
                        if piece_d1 == NONE_PIECE and piece_d2 == NONE_PIECE and piece_d3 == NONE_PIECE:
                            continue
                        if NONE_PIECE in [piece_d1, piece_d2, piece_d3]:
                            break # not equidistant
                        for p_1, p_2, p_3 in itertools.product(piece_d1.pieces, piece_d2.pieces, piece_d3.pieces):
                            ## check if some subsequence of length 3 (of p_{1,2,3,cur}, and all its circular rotations) is a recognized progression
                            ## TODO: there's probably a more compact way to do this
                            for seq in [
                                    ## 1 2 3 c
                                    [p_1, p_2, p_3],
                                    [p_1, p_2, piece_cur],
                                    [p_1, p_3, piece_cur],
                                    [p_2, p_3, piece_cur],
                                    ## 2 3 c 1
                                    [p_2, p_3, p_1],
                                    [p_2, piece_cur, p_1],
                                    [p_3, piece_cur, p_1],
                                    ## 3 c 1 2
                                    [p_3, piece_cur, p_2],
                                    [p_3, p_1, p_2],
                                    [piece_cur, p_1, p_2],
                                    ## c 1 2 3
                                    [piece_cur, p_1, p_3],
                                    [piece_cur, p_2, p_3],
                                    ]:
                                if _progressions(seq[0], seq[1], seq[2]) and any([p.colour == player for p in seq]):
                                    return True
                                else:
                                    break
        return False


    def do_move(self, move):
        ## return True if successful, False if an error, and None if unimplemented
        if not self.is_legal_move(move):
            return False

        if move.type == 'done':
            self.turn = Player.opponent(self.turn)
            self._has_moved = False
            return True

        ## assuming move was issued by self.turn

        coord_src, coord_dest = move.src, move.dest
        if move.type == 'move':
            if self._has_moved:
                return False
            ## validated assumptions
            ## - there exists a non-empty piece at src
            ## - there exists an empty piece or opponent piece at dest
            piece_src, piece_dest = self._board[coord_src], self._board[coord_dest]
            self._board[coord_src] = piece_dest # swap
            self._board[coord_dest] = piece_src
            # if piece_dest != NONE_PIECE:
            #     raise Exception("move input mis-specified but is_legal_move(move) did not catch it. This is a bug") # TODO: remove?
            self._has_moved = True
            return True

        if move.type == 'take':
            piece_dest = self._board[coord_dest]
            ## assuming the piece to be taken is specified by dest, and that there are no "move and take" moves allowed (ie. everything is made into the smallest atom possible)
            prisoners = []
            if self.turn == Player.odd:
                prisoners = self._board.prisoners_held_by_odd
            elif self.turn == Player.even:
                prisoners = self._board.prisoners_held_by_even

            if piece_dest.name == PieceName.pyramid:
                if move.piece.name == PieceName.pyramid:
                    ## empty the pyramid
                    for p_cur in move.piece.pieces:
                        if p_cur.name == PieceName.pyramid:
                            continue # don't include self
                        p_cur.colour = self.turn # change sides
                        prisoners.append(p_cur)
                    self._board[coord_dest] = NONE_PIECE
                else: # remove a particular component
                    p_rm = move.piece
                    new_pyramid = Pyramid.remove_component(piece_dest, move.piece)
                    p_rm.colour = self.turn # change sides
                    prisoners.append(p_rm)
                    self._board[coord_dest] = new_pyramid # will be NONE_PIECE if all components removed
            else:
                piece_dest.colour = self.turn
                prisoners.append(piece_dest)
                self._board[coord_dest] = NONE_PIECE
            return True

        if move.type == 'drop':
            if self._has_moved:
                return False

            prisoners = []
            if self.turn == Player.odd:
                prisoners = self._board.prisoners_held_by_odd
            elif self.turn == Player.even:
                prisoners = self._board.prisoners_held_by_even
            idx = move.src
            piece = prisoners[idx]
            piece.colour = self.turn # just in case
            self._board[move.dest] = piece
            del prisoners[idx]
            return True

        if move.type == 'vict':
            self._victory_declared = True
            res = self.terminal(self.turn)
            if not res:
                self._victory_declared = False
            return True

        return None # unrecognized


    def get_moves(self, player):
        ## as currently coded, it might be highly redundant and unoptimized
        if self.turn != player:
            return set() # wrong turn

        acc_moves = set()
        for coord_cur, piece_cur in self._board.items():
            if piece_cur == NONE_PIECE:
                continue

            colour_opponent = Player.opponent(player)
            if piece_cur.colour == colour_opponent:
                ## taking by siege
                ## taking by addition/subtraction
                ## taking by multiplication/division, first kind
                for piece in piece_cur.pieces:
                    move_obj = Take(None, coord_cur, piece)
                    if self.is_legal_move(move_obj):
                        acc_moves.add(move_obj)

            if piece_cur.colour == player:
                for deltas in [piece_cur.marches, piece_cur.flights]:
                    for coord_dest, piece_dest in self._board.items_fan(coord_cur, deltas):
                        move_obj = Move(coord_cur, coord_dest)
                        if self.is_legal_move(move_obj):
                            acc_moves.add(move_obj)

                        ## taking by equality
                        for piece in piece_dest.pieces:
                            move_obj = Take(coord_cur, coord_dest, piece)
                            if self.is_legal_move(move_obj):
                                acc_moves.add(move_obj)

                for deltas_set in [deltas_cross, deltas_xshape]:
                    for delta_xy in deltas_set:
                        for idx, (coord, piece) in enumerate(self._board.items_delta_xy(coord_cur, delta_xy)):
                            if idx == 0:
                                continue
                            ## taking by eruption
                            ## taking by multiplication/division, void spaces
                            if piece == NONE_PIECE:
                                continue
                            if piece.colour == player:
                                break
                            for p_in in piece.pieces:
                                move_obj = Take(coord_cur, coord, p_in)
                                if self.is_legal_move(move_obj):
                                    acc_moves.add(move_obj)

        ## drop
        prisoners = []
        if self.turn == Player.odd:
            prisoners = self._board.prisoners_held_by_odd
            drop_row = 16
        elif self.turn == Player.even:
            prisoners = self._board.prisoners_held_by_even
            drop_row = 1
        for idx_p, _ in enumerate(prisoners):
            for col in range(1, self._board.ncols +1):
                coord = (col, drop_row)
                move_obj = Drop(idx_p, coord)
                if self.is_legal_move(move_obj):
                    acc_moves.add(move_obj)

        ## vict
        ## TODO: seems like a hack
        self._victory_declared = True
        res = self.terminal(player)
        self._victory_declared = False
        if res:
            acc_moves.add(DECLARE_VICTORY_MOVE)

        ## done
        acc_moves.add(DONE_MOVE)

        return acc_moves


class PlayerAgent(Agent):
    """"""
    help_prompt = """Examples of valid input:
move (8, 13) (7, 10)
take (7, 5) (7, 10) Triangle(36, Player.odd)
take (7, 5) (7, 10) T36_
drop 1 (1, 1)
vict
done
"""

    def _parse_cmd(self, cmd):
        cmd_split = cmd.split(' ')
        if len(cmd_split) == 1:
            return cmd_split

        acc = []
        left, right = 0, 0
        state = 0
        while right < len(cmd):
            char = cmd[right]
            if char == ' ' and state == 0:
                acc.append(cmd[left:right].strip())
                right += 1
                left = right
                state = 1
                continue
            if char == ')' and state in [1, 2]:
                right += 1
                acc.append(cmd[left:right].strip())
                left = right
                state += 1
                continue
            if state >= 3:
                res = cmd[left:].strip()
                if not res:
                    break # nothing was specified

                if any([res.startswith(pre) for pre in ['Circle', 'Triangle', 'Square', 'Pyramid']]):
                    acc.append(res) # is a long form
                else:
                    import re
                    match = re.match('([A-Z])([0-9]+)', res)
                    if not match:
                        break
                    try:
                        piece_type_char = match.group(1)
                        piece_num = match.group(2)
                    except IndexError:
                        break

                    piece_colour = 'Player.odd' if res.endswith('_') else 'Player.even'
                    char_piece_map = {
                        'C': 'Circle',
                        'T': 'Triangle',
                        'S': 'Square',
                        'P': 'Pyramid',
                        }
                    if piece_type_char not in char_piece_map:
                        break
                    res_2 = '{}({}, {})'.format(
                        char_piece_map[piece_type_char],
                        piece_num,
                        piece_colour,
                    )
                    acc.append(res_2)
                break
            right += 1
        return acc


    def decision(self, rith):
        move = None
        while True:
            try:
                cmd = input('> ').strip()
                if cmd in ['exit', 'quit']:
                    sys.exit(0)
                if cmd in ['help', '?']:
                    print(self.help_prompt)
                    continue
                cmd_split = self._parse_cmd(cmd)
                if len(cmd_split) == 1:
                    move_type, = cmd_split
                    if move_type == 'vict':
                        move_obj = DECLARE_VICTORY_MOVE
                    elif move_type == 'done':
                        move_obj = DONE_MOVE
                elif len(cmd_split) == 3:
                    move_type, src, dest = cmd_split
                    if move_type == 'drop':
                        move_obj = Drop(eval(src), eval(dest))
                    elif move_type == 'move':
                        move_obj = Move(eval(src), eval(dest))
                elif len(cmd_split) == 4:
                    move_type, src, dest, piece = cmd_split
                    if move_type == 'take':
                        move_obj = Take(eval(src), eval(dest), eval(piece))
                res = rith.is_legal_move(move_obj)
                if res:
                    move = move_obj
                    break
            except SystemExit as se:
                raise se
            except:
                print("Invalid input. Please try again.\nType 'help' or '?' for more commands.")
                continue # try again
            print("Move disallowed.\nType 'help' or '?' for more commands.")
        return move_obj


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--pylab', default='') # remove from python-mode arguments
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--output-dir', type=str, default=None)
    parser.add_argument('--no-verbose', dest='no_verbose', action='store_true')
    parser.add_argument('--path-output', type=str, default=None)
    parser.add_argument('--even', type=str, default='PlayerAgent')
    parser.add_argument('--odd', type=str, default='PlayerAgent')
    parser.add_argument('--num-games', type=int, default=100)
    parser.add_argument('--no-arena-output-results', dest='arena_output_results', action='store_true')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    if args.output_dir is None:
        if not os.path.exists(RITH_OUT_DIR):
            os.makedirs(RITH_OUT_DIR)
        output_dir = RITH_OUT_DIR
    else:
        output_dir = args.output_dir

    kwargs = {
        'seed': args.seed,
        'verbose': not args.no_verbose,
        'num_games': args.num_games,
        'arena_output_results': not args.arena_output_results,
        'output_dir': output_dir,
        }

    first = eval(args.even)
    second = eval(args.odd)
    arena = Arena(
        lambda: Rith(settings=settings_custom_1),
        lambda: first(Player.even, invalid_move=INVALID_MOVE, seed=args.seed),
        lambda: second(Player.odd, invalid_move=INVALID_MOVE, seed=args.seed),
        **kwargs)
    arena.play()
