from enum import Enum
from games.rith.move import deltas_cross, deltas_xshape, deltas_line_adjacency, delta_right_angle, delta_squares, marches_circle, marches_triangle, marches_square, flying_circle, flying_triangle, flying_square
from itertools import zip_longest

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


# class ContainerPieces(object):
#     def __init__(self, pieces):
#         self.pieces = pieces


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


class NonePiece(Piece):
    def __init__(self):
        super().__init__(None, PieceName.none, Player.none, set([]), set([]))

    def __str__(self):
        return '  '


class OOBPiece(Piece):
    """Useful as a fill value for pattern matching"""
    ## TODO: distinguish it from garbage input to board[]
    def __init__(self):
        super().__init__(None, PieceName.invalid, Player.invalid, set([]), set([]))

    def __str__(self):
        return 'OOB'

NONE_PIECE = NonePiece()
OOB_PIECE = OOBPiece()

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
