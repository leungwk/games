import itertools

class Board(object):
    """Define the ... board.

    The board is an object/container to track and enforce legal
    coordinates and contents. Legal moves, plays, and so on are to be
    handled by the Game object.

    Assuming 2D and rectangular. Also assuming that not one of the
    entries will be deleted.
    """
    _neighbour_deltas = [(dx, dy) for dx, dy in
                         itertools.product([-1, 0, 1], [-1, 0, 1])
                         if (dx, dy) != (0, 0)]


    def __init__(self, nrows, ncols, constructor, **kwargs):
        self._board = {}
        for (col, row) in itertools.product(range(1, ncols +1),
                                            range(1, nrows +1)):
            coord = (col, row)
            self._board[coord] = constructor()
        self.nrows = nrows
        self.ncols = ncols
        # for key, value in kwargs.items():
        #     ## if defined, all invalid inputs return value rather than error
        #     if key == 'default_cell':
        #         self.default_cell = value

        # self._invalid_cell = invalid_cell # "0" # TODO: make a class variable


    def __getitem__(self, coord):
        """coord is index-1"""
        return self._board[coord]


    def get(self, coord, default=None):
        return self._board.get(coord, default)


    def __setitem__(self, coord, item):
        if self.is_valid_coord(coord):
            self._board[coord] = item # TODO: enforce containee type?
        ## invalid keys set "nowhere"


    def __iter__(self):
        for coord in self._board:
            yield coord


    def __str__(self):
        """Print the board.

        Rather than matrix order, use quadrant 1, where (1,1) is in the
        bottom left rather than top left.

        (1,4) (2,4) (3,4) (4,4)
        (1,3) (2,3) (3,3) (4,3)
        (1,2) (2,2) (3,2) (4,2)
        (1,1) (2,1) (3,1) (4,1)
        """
        acc_tot = ''
        for col in range(self.nrows, 0, -1):
            acc_row = ''
            for row in range(1, self.ncols +1):
                coord = (row, col)
                acc_row += str(self._board[coord]) +' '
            acc_tot += acc_row +'\n'
        return acc_tot.strip()


    # def __contains__(self, cell):
    #     """Check if the board has the same cell contents at the cell's coord"""
    #     # coord, _ = self._get_coord(cell)
    #     return self[coord] == cell


    def __eq__(self, other):
        """Check that shape and contents are equal"""
        try:
            other.nrows
            other.ncols
            other._board
        except AttributeError:
            return False

        if not ((self.nrows == other.nrows) and (self.ncols == other.ncols)):
            return False

        for (col, row) in itertools.product(range(1, self.ncols +1),
                                            range(1, self.nrows +1)):
            coord = (col, row)
            try:
                other_cell = other._board[coord]
            except KeyError:
                return False
            if self._board[coord] != other_cell:
                return False
        return True


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        tot_hash = 0
        for (col, row) in itertools.product(range(1, self.ncols +1),
                                            range(1, self.nrows +1)):
            coord = (col, row)
            tot_hash += (hash(coord) +hash(self._board[coord]))
        # tot_hash += hash((self.ncols, self.nrows))
        return tot_hash


    def is_valid_coord(self, coord):
        """Check if coord is a valid position"""
        return coord in self._board


    def items(self):
        for coord in self:
            yield coord, self[coord]


    def values(self):
        for coord in self:
            yield self[coord]


    def keys_neighbours(self, coord):
        """Returns a list of valid neighbouring coords around coord. Ordering not guarenteed. Skip where OOB."""
        row, col = coord
        for d_x, d_y in self._neighbour_deltas:
            new_coord = (row +d_x, col +d_y)
            if not self.is_valid_coord(new_coord):
                continue
            yield new_coord


    def items_neighbours(self, coord):
        """Returns a list of valid neighbouring coords and cells around coord. Ordering not guarenteed."""
        for key in self.keys_neighbours(coord):
            yield key, self[key]


    def values_neighbours(self, coord):
        """Returns a list of valid neighbouring coords and cells around coord. Ordering not guarenteed."""
        for key in self.keys_neighbours(coord):
            yield self[key]


    def keys_vec(self, move):
        """Yield all cells arraying from src along direction dest, and stop when OOB"""
        ## figure out the iteration direction
        (src_x, src_y), (dest_x, dest_y) = move
        delta_x, delta_y = dest_x -src_x, dest_y -src_y

        cur_x, cur_y = move.src
        while self.is_valid_coord((cur_x, cur_y)):
            yield (cur_x, cur_y)
            cur_x += delta_x
            cur_y += delta_y


    def items_vec(self, move):
        """Yield all coords (keys) and cells (values) arraying from src along direction dest"""
        for key in self.keys_vec(move):
            yield key, self[key]


    def values_vec(self, move):
        """Yield all cells (values) arraying from src along direction dest"""
        for key in self.keys_vec(move):
            yield self[key]


    def keys_fan(self, coord_src, deltas):
        """Yield all coords, by each deltas, always starting from src. Skip where OOB"""
        for delta_x, delta_y in deltas:
            cur_x, cur_y = coord_src
            coord = (cur_x +delta_x, cur_y +delta_y)
            if not self.is_valid_coord(coord):
                continue
            yield coord


    def items_fan(self, coord_src, deltas):
        for key in self.keys_fan(coord_src, deltas):
            yield key, self[key]


    def values_fan(self, coord_src, deltas):
        for key in self.keys_fan(coord_src, deltas):
            yield self[key]


    def keys_delta_xy(self, coord_src, delta_xy):
        """Yield all coords, starting from src, by successive delta, and stop when OOB"""
        cur_x, cur_y = coord_src
        delta_x, delta_y = delta_xy

        coord = (cur_x, cur_y)
        while self.is_valid_coord(coord):
            yield coord
            cur_x += delta_x
            cur_y += delta_y
            coord = (cur_x, cur_y)


    def items_delta_xy(self, coord_src, delta_xy):
        for key in self.keys_delta_xy(coord_src, delta_xy):
            yield key, self._board[key]


    def values_delta_xy(self, coord_src, delta_xy):
        for key in self.keys_delta_xy(coord_src, delta_xy):
            yield self._board[key]
