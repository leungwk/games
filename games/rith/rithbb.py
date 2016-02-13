from collections import defaultdict
from itertools import product

mask_w128 = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

col_letter_coord_map = {
    v: k for k,v in enumerate(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
    }

class UINT128(int):
    """Unsigned 128-bit integer"""
    MAX_VALUE = mask_w128
    def __new__(cls, arg=0):
        if arg > mask_w128:
            raise OverflowError('arg too large for custom uint128')
        return int.__new__(UINT128, arg)

    def __repr__(self):
        return 'UINT128({0:#0{1}x})'.format(int.__and__(self, mask_w128), 32)
    def __str__(self):
        return int.__str__(self)
    def __hash__(self):
        return int.__hash__(self)

    def __eq__(self, arg):
        return int.__eq__(self, arg)
    def __ne__(self, arg):
        return not self.__eq__(arg)
    def __bool__(self):
        return int.__bool__(self)
    def __invert__(self):
        return self.__new__(self, int.__xor__(self, mask_w128))

    def __lshift__(self, k):
        return self.__new__(self, int.__lshift__(self, k) & mask_w128)
    def __rshift__(self, k):
        return self.__new__(self, int.__rshift__(self, k) & mask_w128)
    def __or__(self, arg):
        return self.__new__(self, int.__or__(self, arg) & mask_w128)
    def __and__(self, arg):
        return self.__new__(self, int.__and__(self, arg) & mask_w128)
    def __xor__(self, arg):
        return self.__new__(self, int.__xor__(self, arg) & mask_w128)

    def __rlshift__(self, k):
        return int.__rlshift__(k, self)
    def __rrshift__(self, k):
        return int.__rrshift__(k, self)
    def __ror__(self, arg):
        return arg.__or__(self)
    def __rand__(self, arg):
        return arg.__and__(self)
    def __rxor__(self, arg):
        return arg.__xor__(self)

    def __ilshift__(self, arg):
        return self.__lshift__(arg)
    def __irshift__(self, arg):
        return self.__rshift__(arg)
    def __ior__(self, arg):
        return self.__or__(arg)
    def __iand__(self, arg):
        return self.__and__(arg)
    def __ixor__(self, arg):
        return self.__xor__(arg)

    def __mul__(self, arg):
        return self.__new__(self, int.__mul__(self, arg) & mask_w128)
    def __rmul__(self, arg):
        return arg.__mul__(self)
    def __imul__(self, arg):
        return self.__mul__(arg)


class BB_8_16(UINT128):
    """8x16 bitboard.

A1 is bottom left, H16 is the top right.
bit0 is A1, bit127 is H16
    """
    nrows = 16
    ncols = 8
    def __new__(cls, arg=0):
        if arg > mask_w128:
            raise OverflowError('arg too large for custom uint128')
        return int.__new__(BB_8_16, arg)


    def __repr__(self):
        return 'BB_8_16({0:#0{1}x})'.format(int.__and__(self, mask_w128), 32)


    def __str__(self):
        line = bin(self)[2:].zfill(BB_8_16.nrows * BB_8_16.ncols)
        n = BB_8_16.ncols
        return '\n'.join([line[i:i+n][::-1] for i in range(0, len(line), n)])


    @staticmethod
    def locs_to_bb(locs):
        bb = BB_8_16()
        for loc in locs:
            col, row = loc[0], int(loc[1:]) # letter, idx-1
            k = (row -1)*BB_8_16.ncols +col_letter_coord_map[col]
            bb ^= BB_8_16(1 << k)
        return bb


    @staticmethod
    def coords_to_bb(coords):
        ## coords are idx-0
        bb = BB_8_16()
        for coord in coords:
            col, row = coord
            k = col +row*BB_8_16.ncols
            bb ^= BB_8_16(1 << k)
        return bb


class Coord(object):
    """Helper class for coordinate objects. Discrete and two dimensions. (col,row)"""
    @staticmethod
    def add(arg1, arg2):
        return (arg1[0] +arg2[0], arg1[1] +arg2[1])


    @staticmethod
    def subtract(arg1, arg2):
        return (arg1[0] -arg2[0], arg1[1] -arg2[1])


    @staticmethod
    def negate(arg):
        return (-arg[0], -arg[1])


    @staticmethod
    def grid_normalize(arg):
        cx, cy = 0,0
        if arg[0] > 0:
            cx = 1
        elif arg[0] < 0:
            cx = -1
        if arg[1] > 0:
            cy = 1
        elif arg[1] < 0:
            cy = -1
        return (cx, cy)


    @staticmethod
    def linearize(arg, dims): # where arg is a bb, and dims is a 2-tuple # assume valid for now
        return arg[0] +arg[1]*dims[0]


    @staticmethod
    def unlinearize(lidx, dims): # assume valid for now
        icol = lidx % dims[0]
        irow = lidx // dims[0]
        return (icol, irow)


    @staticmethod
    def oob_rect(coord, dims): # assuming a rectangle starting at (0,0) and ending at dims # idx-0
        cx, cy = coord
        dx, dy = dims
        return not ((0 <= cx < dx) and (0 <= cy < dy))




deltas_cross = [
    # orthogonal ('+')
    (+1, 0),
    (0, +1),
    (-1, 0),
    (0, -1),
]
deltas_xshape = [
    # diagonal ('x')
    (+1, +1),
    (-1, +1),
    (-1, -1),
    (+1, -1),
]
deltas_star = deltas_xshape +deltas_cross

from games.common.board import Board
## up to the caller to handle duplicates
## also up to the caller to handle the pyramid?
class LineOfSightBoard(Board):
    """DEPRECATED. Line of sight board using Board object.

    Each space stores the direction and piece seen ("los"), unless an occupied space ("occ"), in which case the direction is None.
    """

    ## coord corresponds to bitboard?
    ## (coord is such that no computations should be needed)
    def __init__(self, nrows, ncols, **kwargs):
        super().__init__(nrows, ncols, lambda: [], **kwargs) # nodes
        self._cache_sight = defaultdict(dict) # rays # from: {dir: [to]}

    # coord_it: (seen_coord, piece_seen)

    def insert(self, piece_in, coord_in):
        """Insert piece at coord. Update the LoS board and cache"""
        ## coord: idx-0
        ## check if piece (colour, loc, number, and if pyramid, all its components) already exists ... (or don't, because the pyramid makes possible multiple?)

        acc_los = defaultdict(list)
        acc_occ = []
        for coord_orig, piece_orig in self._board[coord_in]:
            if coord_orig is None:
                acc_occ.append((coord_orig, piece_orig))
            else:
                delta_dir = Coord.grid_normalize(Coord.negate(Coord.subtract(coord_orig, coord_in)))
                acc_los[delta_dir].append((coord_orig, piece_orig))

        ## invalid the cache if acc_occ is not None (because otherwise its pieces should still sees pieces at coord_in)
        if len(acc_occ) == 0:
            for delta_dir, coord_piece_list in acc_los.items():
                for coord_orig, _ in coord_piece_list:
                    dir_to_dict = self._cache_sight.get(coord_orig, {})
                    if delta_dir in dir_to_dict: # there is something to invalidate
                        del dir_to_dict[delta_dir]

        self._board[coord_in].append((None, piece_in)) # "None" means piece occupies coord_in (as opposed to being seen at coord_in)
        if coord_in not in self._cache_sight:
            self._cache_sight[coord_in] = {} # piece at coord_in sees nothing

        for delta in deltas_star:
            los_to_rm = acc_los.get(delta, [])
            for coord_cur, records_cur in self.items_delta_xy(
                    coord_in, delta, incl_src=False):
                acc = []
                stop = False
                for rec in records_cur:
                    c,_ = rec
                    if c is None:
                        stop = True
                        acc.append(rec)
                        self._cache_sight[coord_in][delta] = coord_cur
                        self._cache_sight[coord_cur][Coord.negate(delta)] = coord_in
                    else: # is los
                        if rec not in los_to_rm:
                            acc.append(rec)
                        ## drop otherwise
                self._board[coord_cur] = acc
                acc.append((coord_in, piece_in))
                if stop:
                    break


    def delete(self, piece_in, coord_in):
        """Delete piece from coord. Update the LoS board and cache"""
        ## separate LoS from occ records
        acc_los = defaultdict(list) # change to set()?
        acc_occ = []
        removed = False
        for coord_orig, piece_orig in self._board[coord_in]:
            if coord_orig is None:
                if piece_orig == piece_in:
                    removed = True
                    continue
                else:
                    acc_occ.append((coord_orig, piece_orig))
            else:
                delta_dir = Coord.grid_normalize(Coord.negate(Coord.subtract(coord_orig, coord_in)))
                acc_los[delta_dir].append((coord_orig, piece_orig))

        ## put everything back
        res = acc_occ +[l for los in acc_los.values() for l in los]
        self._board[coord_in] = res

        if not removed:
            return # nothing changed

        if len(acc_occ) != 0: # no LoS change
            return

        ## remove entries that saw coord_in
        for delta, coord in self._cache_sight.get(coord_in, {}).items():
            opp_delta = Coord.negate(delta)
            del self._cache_sight[coord][opp_delta]
        del self._cache_sight[coord_in] # remove cache from coord_in

        ## extend all existing LoS not from removed piece, and remove all LoS from piece
        for delta in deltas_star:
            los_to_add = acc_los.get(delta, [])
            for coord_cur, records_cur in self.items_delta_xy(
                    coord_in, delta, incl_src=False):
                acc = []
                stop = False
                for rec in records_cur:
                    c,_ = rec
                    if c is None:
                        for clos, _ in los_to_add: # if there are los, there should only be one clos
                            self._cache_sight[coord_cur][delta] = clos
                        stop = True
                    if rec != (coord_in, piece_in): # keep any LoS or occupied pieces accept for the removed piece
                        acc.append(rec)
                    acc.extend(los_to_add)
                self._board[coord_cur] = acc
                if stop:
                    break


MASK_ROW_1 = BB_8_16(0xFF)
MASK_COL_1 = BB_8_16(0x01010101010101010101010101010101)
## starting from row 1
MASK_DIAG_NE_A1 = BB_8_16(0x8040201008040201)
MASK_DIAG_NE_B1 = MASK_DIAG_NE_A1 >> 8
MASK_DIAG_NE_C1 = MASK_DIAG_NE_B1 >> 8
MASK_DIAG_NE_D1 = MASK_DIAG_NE_C1 >> 8
MASK_DIAG_NE_E1 = MASK_DIAG_NE_D1 >> 8
MASK_DIAG_NE_F1 = MASK_DIAG_NE_E1 >> 8
MASK_DIAG_NE_G1 = MASK_DIAG_NE_F1 >> 8
MASK_DIAG_NE_H1 = MASK_DIAG_NE_G1 >> 8

MASK_DIAG_NW_H1 = BB_8_16(0x0102040810204080)
MASK_DIAG_NW_G1 = BB_8_16(0x01020408102040)
MASK_DIAG_NW_F1 = BB_8_16(0x010204081020)
MASK_DIAG_NW_E1 = BB_8_16(0x0102040810)
MASK_DIAG_NW_D1 = BB_8_16(0x01020408)
MASK_DIAG_NW_C1 = BB_8_16(0x010204)
MASK_DIAG_NW_B1 = BB_8_16(0x0102)
MASK_DIAG_NW_A1 = BB_8_16(0x01)

MASK_DIAG_SW_H16 = BB_8_16(0x80402010080402010000000000000000)
MASK_DIAG_SW_G16 = MASK_DIAG_SW_H16 << 8
MASK_DIAG_SW_F16 = MASK_DIAG_SW_G16 << 8
MASK_DIAG_SW_E16 = MASK_DIAG_SW_F16 << 8
MASK_DIAG_SW_D16 = MASK_DIAG_SW_E16 << 8
MASK_DIAG_SW_C16 = MASK_DIAG_SW_D16 << 8
MASK_DIAG_SW_B16 = MASK_DIAG_SW_C16 << 8
MASK_DIAG_SW_A16 = MASK_DIAG_SW_B16 << 8

MASK_DIAG_SE_A16 = BB_8_16(0x01020408102040800000000000000000)
MASK_DIAG_SE_B16 = MASK_DIAG_SE_A16 << 8
MASK_DIAG_SE_C16 = MASK_DIAG_SE_B16 << 8
MASK_DIAG_SE_D16 = MASK_DIAG_SE_C16 << 8
MASK_DIAG_SE_E16 = MASK_DIAG_SE_D16 << 8
MASK_DIAG_SE_F16 = MASK_DIAG_SE_E16 << 8
MASK_DIAG_SE_G16 = MASK_DIAG_SE_F16 << 8
MASK_DIAG_SE_H16 = MASK_DIAG_SE_G16 << 8
## MASK [TYPE] [DIR] [START]

## East is at idx=0, then go clockwise
order_winds = [
    (1,0),
    (1,-1),
    (0,-1),
    (-1,-1),
    (-1,0),
    (-1,1),
    (0,1),
    (1,1),
    ]

table_ray_masks = [
    ## ordered by order_winds
    ## given a ray, lists idx'd by col unless axis-aligned to the x-axis, in which case it is idx'd by row
    ## all lists start at row 1 or col 1 depending, unless diagonal and pointing down, then they start at row 16
    [
        (MASK_ROW_1 >> k) ^ MASK_ROW_1 for k in range(8, 0, -1)
    ],
    [
        MASK_DIAG_SE_A16,
        MASK_DIAG_SE_B16,
        MASK_DIAG_SE_C16,
        MASK_DIAG_SE_D16,
        MASK_DIAG_SE_E16,
        MASK_DIAG_SE_F16,
        MASK_DIAG_SE_G16,
        MASK_DIAG_SE_H16,
    ],
    [
        (MASK_COL_1 >> (k << 3)) for k in range(15, -1, -1)
    ],
    [
        MASK_DIAG_SW_A16,
        MASK_DIAG_SW_B16,
        MASK_DIAG_SW_C16,
        MASK_DIAG_SW_D16,
        MASK_DIAG_SW_E16,
        MASK_DIAG_SW_F16,
        MASK_DIAG_SW_G16,
        MASK_DIAG_SW_H16,
    ],
    [
        MASK_ROW_1 >> k for k in range(7, -1, -1)
    ],
    [
        MASK_DIAG_NW_A1,
        MASK_DIAG_NW_B1,
        MASK_DIAG_NW_C1,
        MASK_DIAG_NW_D1,
        MASK_DIAG_NW_E1,
        MASK_DIAG_NW_F1,
        MASK_DIAG_NW_G1,
        MASK_DIAG_NW_H1,
    ],
    [
        (MASK_COL_1 >> (k << 3)) ^ MASK_COL_1 for k in range(16, 0, -1)
    ],
    [
        MASK_DIAG_NE_A1,
        MASK_DIAG_NE_B1,
        MASK_DIAG_NE_C1,
        MASK_DIAG_NE_D1,
        MASK_DIAG_NE_E1,
        MASK_DIAG_NE_F1,
        MASK_DIAG_NE_G1,
        MASK_DIAG_NE_H1,
    ],
]

table_ray_msb_lsb = [
    ## ordered by order_winds
    ## in a bb, use the lsb or msb to find the number spaces from the ray's origin to the first set '1'
    'lsb',
    'msb',
    'msb',
    'msb',
    'msb',
    'lsb',
    'lsb',
    'lsb',
]


def _los_bb_cache_init(bb_in):
    """Initalize the los cache for the input bb.

    It is OK if this function is slow because it should only be called once per game"""
    bb_dims = (bb_in.ncols, bb_in.nrows)
    los_cache = {}
    for icol, irow in product(range(bb_in.ncols), range(bb_in.nrows)):
        coord_iter = (icol, irow)
        bb_in_only_orig = bb_in & BB_8_16(
            1 << Coord.linearize(coord_iter, bb_dims))
        if not bb_in_only_orig: # nothing set
            continue
        for ray_dir in order_winds:
            coord_step = coord_iter
            while True:
                coord_step = Coord.add(coord_step, ray_dir)
                if Coord.oob_rect(coord_step, bb_dims):
                    break
                bb_iter = bb_in & BB_8_16(
                    1 << Coord.linearize(coord_step, bb_dims))
                if not bb_iter:
                    continue
                rays_seen = los_cache.setdefault(coord_iter, {})
                rays_seen[ray_dir] = coord_step
                opp_ray_dir = Coord.negate(ray_dir)
                rays_seen = los_cache.setdefault(coord_step, {})
                rays_seen[opp_ray_dir] = coord_iter
                break
    return los_cache



def los_bb(bb_in, coord_in, los_cache):
    """Find the seen coords from coord_in (idx-0) for the state of bb_in.

    This will /not/ update other coordinates. For the cache to be consistent, it must be initalized on every space, and then dynamically updated on each board state change"""
    bb_dims = (bb_in.ncols, bb_in.nrows)
    lidx = Coord.linearize(coord_in, bb_dims)
    icol, irow = coord_in
    bb_new = bb_in

    bb_orig = BB_8_16(1 << lidx)
    bb_orig_inv = ~bb_orig

    bb_new_only_coord = bb_new & bb_orig
    bb_new_wo_coord = bb_new & bb_orig_inv

    def _star_sb(bb, star_sb):
        """index of * significant bit (idx-0)"""
        if star_sb == 'lsb':
            bl = (bb & -bb).bit_length() -1
        elif star_sb == 'msb':
            bl = bb.bit_length() -1
        else:
            raise ValueError('Unrecognized significant bit command: {}'.format(star_sb))
        return bl

    acc_seen = []
    seen_change = {ray_dir: None for ray_dir in order_winds}
    for ray_dir, mask_list, star_sb in zip(order_winds, table_ray_masks, table_ray_msb_lsb):
        # star_sb = table_ray_msb_lsb[idx]
        if ray_dir in [(0, 1), (0, -1)]: # up/down
            ## use irow, offset from left
            mask = mask_list[irow] << icol
        elif ray_dir in [(1, 0), (-1, 0)]: # r/l
            ## use icol, offset from bottom
            mask = mask_list[icol] << bb_in.ncols*irow
        elif ray_dir in [(-1, -1), (1, -1)]: # sw/se
            ## use icol, offset from top
            mask = mask_list[icol] >> bb_in.ncols*((bb_in.nrows-1)-irow)
        else: # nw/ne
            ## use icol, offset from bottom
            mask = mask_list[icol] << bb_in.ncols*irow
        bb_masked = mask & bb_new_wo_coord # mask; remove the origin square
        sb = _star_sb(bb_masked, star_sb)
        if sb <= -1: # no bits in bb_masked set
            continue
        n_bfo = sb -lidx # num bits from orig
        res_coord = Coord.unlinearize(lidx +n_bfo, bb_dims)
        seen_change[ray_dir] = res_coord
        acc_seen.append(res_coord)

    ## update cache
    if bb_new_only_coord: # coord_in bit set
        ## need to update from coord_in, and to coord_in (ie. from all coord_seen)
        los_cache.setdefault(coord_in, {})
        for ray_dir, coord_seen in seen_change.items():
            ## from orig to seen
            if coord_seen is None:
                ## remove it only if it exists
                ## cache should be such that null entries do not exist
                rays_seen = los_cache.get(coord_in, {})
                if len(rays_seen) == 0:
                    if coord_in in los_cache:
                        del los_cache[coord_in]
                else:
                    rays_seen.pop(ray_dir, None)
                ## ok to stop because coord_seen is undefined
                ## it could have been any of the spaces, or none of them
                continue
            rays_seen = los_cache.setdefault(coord_in, {})
            rays_seen[ray_dir] = coord_seen
            ## from seen to orig
            opp_ray_dir = Coord.negate(ray_dir)
            rays_seen = los_cache.setdefault(coord_seen, {})
            rays_seen[opp_ray_dir] = coord_in
    else: # coord_in bit not set
        def _update_seen(ray_dir_a, ray_dir_b):
            coord_a = seen_change[ray_dir_b] # point the other way
            coord_b = seen_change[ray_dir_a]
            if (coord_a is not None) and (coord_b is None):
                rays_seen = los_cache.get(coord_a, {})
                if len(rays_seen) == 0:
                    pass
                elif len(rays_seen) == 1: # if it saw one dir, it no longer does
                    del los_cache[coord_a]
                else:
                    rays_seen.pop(ray_dir_a, None)
            elif (coord_a is None) and (coord_b is not None):
                rays_seen = los_cache.get(coord_b, {})
                if len(rays_seen) == 0:
                    pass
                elif len(rays_seen) == 1:
                    del los_cache[coord_b]
                else:
                    rays_seen.pop(ray_dir_b, None)
            elif (coord_a is None) and (coord_b is None):
                pass
            else: # both are not None
                rays_seen_a = los_cache.setdefault(coord_a, {})
                rays_seen_b = los_cache.setdefault(coord_b, {})
                rays_seen_a[ray_dir_a] = coord_b # not setdefault because it should always update, incl. overwrite
                rays_seen_b[ray_dir_b] = coord_a
        ## remove the entry for coord_in
        los_cache.pop(coord_in, None) # don't need the return value
        ## update each pair on directions on the same line
        _update_seen((1,0), (-1,0))  # --> <--
        _update_seen((1,-1), (-1,1)) # \v ^\
        _update_seen((0,-1), (0,1))  # v ^
        _update_seen((-1,-1), (1,1)) # v/ /^

    if bb_new_only_coord: # the queried coord was set
        return acc_seen
    return []
