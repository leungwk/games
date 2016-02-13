import pytest
from games.rith.rithbb import UINT128, BB_8_16

from games.rith.rithbb import Coord

from games.rith.rithbb import los_bb, table_ray_masks, order_winds, _los_bb_cache_init

RITH_BOARD_SHAPE = (8,16)

#### ================================================================
#### UINT128
#### ================================================================

with pytest.raises(OverflowError):
    x = UINT128(UINT128.MAX_VALUE +1)

mask_1_w128 = UINT128(UINT128.MAX_VALUE)
mask_byte_1 = UINT128(0x000000000000000000000000000000FF)
mask_byte_2 = UINT128(0x0000000000000000000000000000FF00)
mask_byte_1_2 = UINT128(0x0000000000000000000000000000FFFF)

xval = UINT128()
assert xval == UINT128(0x0)
assert xval != UINT128(0x1)
assert 'b' == ('a' if xval else 'b')
assert ~xval == mask_1_w128
# assert repr(xval) == 'UINT128(0x0)' # TODO: fix
assert str(xval) == '0'
assert hash(xval) == hash(0)
assert type(xval) == UINT128

num = eval('0b' +'1000' +'0010' +'0100' +'0001' +'0'*112) # 0x8241000...
xval = UINT128(num)
num_ls1 = eval('0b' +bin(num)[3:] +'0')
num_ls1_wrong = eval('0b' +bin(num)[2:] +'0')
assert int((xval << 1)) != num_ls1_wrong # don't use UINT128 otherwise overflow
assert (xval << 1) == UINT128(num_ls1)
assert (xval >> 128-4) == UINT128(0x8)
assert (xval >> 128+1) == UINT128(0x0) # it should fall off
assert (xval >> 128-16) == UINT128(0x8241)
assert (xval >> 128-16) | mask_byte_1_2 == UINT128(0xFFFF)
assert (xval >> 128-16) & mask_byte_1_2 == UINT128(0x8241)
assert (xval >> 128-16) ^ mask_byte_1_2 == UINT128(0x7DBE)
assert mask_byte_1_2 | (xval >> 128-16) == UINT128(0xFFFF)
assert mask_byte_1_2 & (xval >> 128-16) == UINT128(0x8241)
assert mask_byte_1_2 ^ (xval >> 128-16) == UINT128(0x7DBE)

# not working
# with pytest.raises(ValueError):
#     x = (1 << xval)
# with pytest.raises(ValueError):
#     x = (1 >> xval)

xval <<= 1
assert xval == UINT128(num_ls1)
xval >>= 1
assert xval == UINT128(0x2410000000000000000000000000000)

xval = UINT128(0x42)
xval &= mask_byte_1
assert xval == UINT128(0x42)
xval |= UINT128(0x01)
assert xval == UINT128(0x43)
xval ^= mask_byte_1
assert xval == UINT128(0xBC)

xval = UINT128(0x8241)
xval2 = UINT128(0x100000001)
xval3 = UINT128(0x824100008241)
assert (xval * xval2) == xval3
assert (xval2 * xval) == xval3
xval *= xval2
assert xval == xval3

#### ================================================================
#### Coord
#### ================================================================

coord1 = (5,13)
coord2 = (1,9)
assert Coord.subtract(coord1, coord2) == (4,4)
assert Coord.negate(coord1) == (-5,-13)
assert Coord.grid_normalize((-4,3)) == (-1,1)
res = 2 +14*8
assert Coord.linearize((2,14), RITH_BOARD_SHAPE) == res
assert Coord.unlinearize(res, RITH_BOARD_SHAPE) == (2,14)

## coordinate conversions
# fulke 1, all circles. bb per row is reversed (since the A column is LSB)
coords = [
    (1,3),
    (2,4), (3,4), (4,4), (5,4),
    (2,5), (3,5), (4,5), (5,5),
    (2,10), (3,10), (4,10), (5,10),
    (2,11), (3,11), (4,11), (5,11),
    (7,12),
]
locs = [
    'B4',
    'C5', 'D5', 'E5', 'F5',
    'C6', 'D6', 'E6', 'F6',
    'C11', 'D11', 'E11', 'F11',
    'C12', 'D12', 'E12', 'F12',
    'H13',
]
bb = '0b' +"""
00000000
00000000
00000000
10000000
00111100
00111100
00000000
00000000
00000000
00000000
00111100
00111100
00000010
00000000
00000000
00000000
""".translate({ord('\n'): None})
bb_occ_ac = BB_8_16.locs_to_bb(locs)
assert bb_occ_ac == BB_8_16(eval(bb))
bb_occ_ac = BB_8_16.coords_to_bb(coords)
assert bb_occ_ac == BB_8_16(eval(bb))

k = Coord.linearize((2,14), RITH_BOARD_SHAPE)
bb_list = [list('0'*8) for _ in range(16)]
bb_list[15-14][2] = '1'
bb_str = '\n'.join([''.join(l) for l in bb_list])
assert bb_str == str(BB_8_16(1 << k))

#### ================================================================
#### los_bb (bitboard line of sight calculation)
#### ================================================================

lookup_ow = dict([(v,k) for k,v in enumerate(order_winds)])
assert 15+1 == bin(table_ray_masks[lookup_ow[(0,-1)]][15]).count('1') # row 16
assert 16-14 == bin(table_ray_masks[lookup_ow[(0,1)]][14]).count('1') # row 15
assert 5+1 == bin(table_ray_masks[lookup_ow[(-1,1)]][5]).count('1') # col F
assert 4+1 == bin(table_ray_masks[lookup_ow[(-1,0)]][4]).count('1') # col E
assert 3+1 == bin(table_ray_masks[lookup_ow[(-1,-1)]][3]).count('1') # col D
assert 8-2 == bin(table_ray_masks[lookup_ow[(1,0)]][2]).count('1') # col C
assert 8-1 == bin(table_ray_masks[lookup_ow[(1,-1)]][1]).count('1') # col B
assert 8-0 == bin(table_ray_masks[lookup_ow[(1,1)]][0]).count('1') # col A

## inspect visually
# for ray in table_ray_masks:
#     for bb in table_ray_masks[ray]:
#         print(ray, repr(bb), '\n', str(bb), '\n\n')


bb = BB_8_16(0x0)
los_cache = _los_bb_cache_init(bb)
assert set(los_bb(bb, (3,3), los_cache)) == set()

bb = BB_8_16(0x80449000008)
los_cache = _los_bb_cache_init(bb)
assert (0,0) not in los_cache
assert len(los_cache) == bin(bb).count('1')
assert len(los_cache[(3,3)]) == 5
#
assert los_cache[(3,3)][(-1,0)] == (0,3)
assert los_cache[(3,3)][(-1,1)] == (2,4)
assert los_cache[(3,3)][(1,0)] == (6,3)
assert los_cache[(3,3)][(0,1)] == (3,5)
assert los_cache[(3,3)][(0,-1)] == (3,0)
#
assert len(los_cache[(0,3)]) == 2
assert los_cache[(0,3)][(1,0)] == (3,3)
assert los_cache[(0,3)][(1,-1)] == (3,0)
#
assert len(los_cache[(3,0)]) == 3
assert los_cache[(3,0)][(-1,1)] == (0,3)
assert los_cache[(3,0)][(0,1)] == (3,3)
assert los_cache[(3,0)][(1,1)] == (6,3)
#
assert len(los_cache[(6,3)]) == 2
assert los_cache[(6,3)][(-1,0)] == (3,3)
assert los_cache[(6,3)][(-1,-1)] == (3,0)
#
assert len(los_cache[(2,4)]) == 2
assert los_cache[(2,4)][(1,-1)] == (3,3)
assert los_cache[(2,4)][(1,1)] == (3,5)
#
assert len(los_cache[(3,5)]) == 2
assert los_cache[(3,5)][(-1,-1)] == (2,4)
assert los_cache[(3,5)][(0,-1)] == (3,3)
#
assert set(los_bb(bb, (3,3), los_cache)) == set([(3, 5), (0, 3), (2, 4), (3, 0), (6, 3)])
assert set(los_bb(bb, (2,4), los_cache)) == set([(3, 3), (3, 5)])

bb = BB_8_16(0x1180449000008) # the "1"s are not seen
los_cache = _los_bb_cache_init(bb)
assert los_cache[(3,3)][(-1,1)] == (2,4)
assert los_cache[(3,3)][(-1,1)] != (0,6) # '1' not seen
assert los_cache[(2,4)][(-1,1)] == (0,6)
assert set(los_bb(bb, (3,3), los_cache)) == set([(3, 5), (0, 3), (2, 4), (3, 0), (6, 3)])
## multiple bits in a row (only leftmost is seen)

bb = BB_8_16(0xE40001)
los_cache = _los_bb_cache_init(bb)
assert set(los_bb(bb, (2,2), los_cache)) == set([(0, 0), (5, 2)])

## "edge" cases
bb = BB_8_16(0x01000000000000008000000000000081)
los_cache = _los_bb_cache_init(bb)
assert set(los_bb(bb, (0,0), los_cache)) == set([(7,0), (7,7), (0,15)])
assert set(los_bb(bb, (7,7), los_cache)) == set([(0,0), (7,0)])






bb = BB_8_16(0x1020408000008)
los_cache = _los_bb_cache_init(bb)
assert los_cache[(3,3)][(-1,1)] == (2,4)
assert los_cache[(2,4)][(-1,1)] == (1,5)
assert los_cache[(2,4)][(1,-1)] == (3,3)
bb &= ~BB_8_16(1 << Coord.linearize((2,4), RITH_BOARD_SHAPE))
assert set(los_bb(bb, (2,4), los_cache)) == set([])
assert (2,4) not in los_cache
assert None not in los_cache # for now, it shouldn't have null entries
assert len(los_cache) == 4 # num of '1' bits
assert len(los_cache[(3,3)]) == 2
assert los_cache[(3,3)][(-1,1)] == (1,5)
assert len(los_cache[(1,5)]) == 2
assert los_cache[(1,5)][(1,-1)] == (3,3)
assert los_cache[(1,5)][(-1,1)] == (0,6)
assert len(los_cache[(0,6)]) == 1
assert los_cache[(0,6)][(1,-1)] == (1,5)

bb &= ~BB_8_16(1 << Coord.linearize((3,0), RITH_BOARD_SHAPE))
assert set(los_bb(bb, (3,0), los_cache)) == set([])
assert len(los_cache[(3,3)]) == 1
assert los_cache[(3,3)][(-1,1)] == (1,5)

bb |= BB_8_16(1 << Coord.linearize((0,3), RITH_BOARD_SHAPE))
assert set(los_bb(bb, (0,3), los_cache)) == set([(0,6),(3,3)])
assert len(los_cache[(0,3)]) == 2
assert los_cache[(0,3)][(0,1)] == (0,6)
assert los_cache[(0,3)][(1,0)] == (3,3)
assert len(los_cache[(3,3)]) == 2
assert los_cache[(3,3)][(-1,0)] == (0,3)
assert los_cache[(3,3)][(-1,1)] == (1,5)

bb &= ~BB_8_16(1 << Coord.linearize((3,3), RITH_BOARD_SHAPE))
los_bb(bb, (3,3), los_cache)

bb |= BB_8_16(1 << Coord.linearize((3,6), RITH_BOARD_SHAPE))
los_bb(bb, (3,6), los_cache)

bb &= ~BB_8_16(1 << Coord.linearize((0,6), RITH_BOARD_SHAPE))
los_bb(bb, (0,6), los_cache)
assert (1,5) not in los_cache
