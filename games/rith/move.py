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
## include the forward and reverse orders, because unlike taking by elementary operations, where each combination of 2 is checked, progressions must not be rearranged
deltas_line_adjacency_vict = [
    [(-1, 0), (+1, 0)],
    [(+1, 0), (-1, 0)],

    [(-1, -1), (+1, +1)],
    [(+1, +1), (-1, -1)],

    [(0, -1), (0, +1)],
    [(0, +1), (0, -1)],

    [(-1, +1), (+1, -1)],
    [(+1, -1), (-1, +1)],
]

delta_right_angle = [
    [(+1, 0), (0, +1)], # ^-
    [(0, +1), (+1, 0)], # ^-

    [(-1, 0), (0, +1)], # -^
    [(0, +1), (-1, 0)], # -^

    [(-1, 0), (0, -1)], # -v
    [(0, -1), (-1, 0)], # -v

    [(+1, 0), (0, -1)], # v-
    [(0, -1), (+1, 0)], # v-
]

delta_squares = [
    ## these need to be consecutive to simplify the code
    [(+1, 0), (+1, +1), (0, +1)], # <|
    [(0, +1), (+1, +1), (+1, 0)], # <|

    [(0, +1), (-1, +1), (-1, 0)], # v-
    [(-1, 0), (-1, +1), (0, +1)], # v-

    [(-1, 0), (-1, -1), (0, -1)], # |>
    [(0, -1), (-1, -1), (-1, 0)], # |>

    [(0, -1), (+1, -1), (+1, 0)], # >|
    [(+1, 0), (+1, -1), (0, -1)], # >|
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
