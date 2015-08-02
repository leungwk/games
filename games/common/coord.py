class Coord(object):
    def __init__(self, val_x, val_y):
        self._x = val_x
        self._y = val_y


    def __hash__(self):
        ## so that any existing objects (like Board) that used a 2-tuple would get the same hash
        return hash((self._x, self._y))


    def __eq__(self, coord):
        return (self._x == coord[0]) and (self._y == coord[1])


    def __ne__(self, coord):
        return not self.__eq__(coord)


    def __iter__(self):
        ## for unpacking as if a 2-tuple
        yield self._x
        yield self._y


    def __getitem__(self, idx):
        if idx == 0:
            return self._x
        elif idx == 1:
            return self._y
        else:
            raise IndexError('Coord index out of range')


    ## TODO: problem, will not handle if addition reversed
    def __add__(self, coord):
        return Coord(self._x +coord[0], self._y +coord[1])


    def __sub__(self, coord):
        return Coord(self._x -coord[0], self._y -coord[1])


    def __repr__(self):
        return 'Coord({x},{y})'.format(x=self._x, y=self._y)


    def __str__(self):
        return '({x},{y})'.format(x=self._x, y=self._y)


    ## not preserving types; intended as convenience functions instead
    @staticmethod
    def add(coord_a, coord_b):
        return (coord_a[0] +coord_b[0], coord_a[1] +coord_b[1])


    @staticmethod
    def subtract(coord_a, coord_b):
        return (coord_a[0] -coord_b[0], coord_a[1] -coord_b[1])
