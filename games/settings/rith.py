from games.rith.piece import Player, PieceName
from games.rith.piece import Circle, Triangle, Square, Pyramid

def _setup_fulke_1(rith):
    """Following /Fulke/ (1563), first kind of play (and board layout)"""
    ## white
    ## row 3
    rith._board[(1, 3)] = Square(289, Player.even)
    rith._board[(2, 3)] = Square(169, Player.even)
    rith._board[(7, 3)] = Square(81, Player.even)
    rith._board[(8, 3)] = Square(25, Player.even)
    ## row 4
    rith._board[(1, 4)] = Square(153, Player.even)
    rith._board[(2, 4)] = Pyramid(91, Player.even, pieces=[
        Square(36, Player.even),
        Square(25, Player.even),
        Triangle(16, Player.even),
        Triangle(9, Player.even),
        Circle(4, Player.even),
        Circle(1, Player.even),
        ])
    rith._board[(3, 4)] = Triangle(49, Player.even)
    rith._board[(4, 4)] = Triangle(42, Player.even)
    rith._board[(5, 4)] = Triangle(20, Player.even)
    rith._board[(6, 4)] = Triangle(25, Player.even)
    rith._board[(7, 4)] = Square(45, Player.even)
    rith._board[(8, 4)] = Square(15, Player.even)
    ## row 5
    rith._board[(1, 5)] = Triangle(81, Player.even)
    rith._board[(2, 5)] = Triangle(72, Player.even)
    rith._board[(3, 5)] = Circle(64, Player.even)
    rith._board[(4, 5)] = Circle(36, Player.even)
    rith._board[(5, 5)] = Circle(16, Player.even)
    rith._board[(6, 5)] = Circle(4, Player.even)
    rith._board[(7, 5)] = Triangle(6, Player.even)
    rith._board[(8, 5)] = Triangle(9, Player.even)
    ## row 6
    rith._board[(3, 6)] = Circle(8, Player.even)
    rith._board[(4, 6)] = Circle(6, Player.even)
    rith._board[(5, 6)] = Circle(4, Player.even)
    rith._board[(6, 6)] = Circle(2, Player.even)
    ## black
    ## row 14
    rith._board[(1, 14)] = Square(49, Player.odd)
    rith._board[(2, 14)] = Square(121, Player.odd)
    rith._board[(7, 14)] = Square(225, Player.odd)
    rith._board[(8, 14)] = Square(361, Player.odd)
    ## row 13
    rith._board[(1, 13)] = Square(28, Player.odd)
    rith._board[(2, 13)] = Square(66, Player.odd)
    rith._board[(3, 13)] = Triangle(30, Player.odd)
    rith._board[(4, 13)] = Triangle(36, Player.odd)
    rith._board[(5, 13)] = Triangle(56, Player.odd)
    rith._board[(6, 13)] = Triangle(64, Player.odd)
    rith._board[(7, 13)] = Square(120, Player.odd)
    rith._board[(8, 13)] = Pyramid(190, Player.odd, pieces=[
        Square(64, Player.odd),
        Square(49, Player.odd),
        Triangle(36, Player.odd),
        Triangle(25, Player.odd),
        Circle(16, Player.odd),
        ])
    ## row 12
    rith._board[(1, 12)] = Triangle(16, Player.odd)
    rith._board[(2, 12)] = Triangle(12, Player.odd)
    rith._board[(3, 12)] = Circle(9, Player.odd)
    rith._board[(4, 12)] = Circle(25, Player.odd)
    rith._board[(5, 12)] = Circle(49, Player.odd)
    rith._board[(6, 12)] = Circle(81, Player.odd)
    rith._board[(7, 12)] = Triangle(90, Player.odd)
    rith._board[(8, 12)] = Triangle(100, Player.odd)
    ## row 11
    rith._board[(3, 11)] = Circle(3, Player.odd)
    rith._board[(4, 11)] = Circle(5, Player.odd)
    rith._board[(5, 11)] = Circle(7, Player.odd)
    rith._board[(6, 11)] = Circle(9, Player.odd)


def _setup_fulke_3(rith):
    """Following /Fulke/ (1563), third kind of play (and board layout). Is Fulke 1 but shifted back by 2 rows"""
    ## white
    ## row 1
    rith._board[(1, 1)] = Square(289, Player.even)
    rith._board[(2, 1)] = Square(169, Player.even)
    rith._board[(7, 1)] = Square(81, Player.even)
    rith._board[(8, 1)] = Square(25, Player.even)
    ## row 2
    rith._board[(1, 2)] = Square(153, Player.even)
    rith._board[(2, 2)] = Pyramid(91, Player.even, pieces=[
        Square(36, Player.even),
        Square(25, Player.even),
        Triangle(16, Player.even),
        Triangle(9, Player.even),
        Circle(4, Player.even),
        Circle(1, Player.even),
        ])
    rith._board[(3, 2)] = Triangle(49, Player.even)
    rith._board[(4, 2)] = Triangle(42, Player.even)
    rith._board[(5, 2)] = Triangle(20, Player.even)
    rith._board[(6, 2)] = Triangle(25, Player.even)
    rith._board[(7, 2)] = Square(45, Player.even)
    rith._board[(8, 2)] = Square(15, Player.even)
    ## row 3
    rith._board[(1, 3)] = Triangle(81, Player.even)
    rith._board[(2, 3)] = Triangle(72, Player.even)
    rith._board[(3, 3)] = Circle(64, Player.even)
    rith._board[(4, 3)] = Circle(36, Player.even)
    rith._board[(5, 3)] = Circle(16, Player.even)
    rith._board[(6, 3)] = Circle(4, Player.even)
    rith._board[(7, 3)] = Triangle(6, Player.even)
    rith._board[(8, 3)] = Triangle(9, Player.even)
    ## row 4
    rith._board[(3, 4)] = Circle(8, Player.even)
    rith._board[(4, 4)] = Circle(6, Player.even)
    rith._board[(5, 4)] = Circle(4, Player.even)
    rith._board[(6, 4)] = Circle(2, Player.even)
    ## black
    ## row 16
    rith._board[(1, 16)] = Square(49, Player.odd)
    rith._board[(2, 16)] = Square(121, Player.odd)
    rith._board[(7, 16)] = Square(225, Player.odd)
    rith._board[(8, 16)] = Square(361, Player.odd)
    ## row 15
    rith._board[(1, 15)] = Square(28, Player.odd)
    rith._board[(2, 15)] = Square(66, Player.odd)
    rith._board[(3, 15)] = Triangle(30, Player.odd)
    rith._board[(4, 15)] = Triangle(36, Player.odd)
    rith._board[(5, 15)] = Triangle(56, Player.odd)
    rith._board[(6, 15)] = Triangle(64, Player.odd)
    rith._board[(7, 15)] = Square(120, Player.odd)
    rith._board[(8, 15)] = Pyramid(190, Player.odd, pieces=[
        Square(64, Player.odd),
        Square(49, Player.odd),
        Triangle(36, Player.odd),
        Triangle(25, Player.odd),
        Circle(16, Player.odd),
        ])
    ## row 14
    rith._board[(1, 14)] = Triangle(16, Player.odd)
    rith._board[(2, 14)] = Triangle(12, Player.odd)
    rith._board[(3, 14)] = Circle(9, Player.odd)
    rith._board[(4, 14)] = Circle(25, Player.odd)
    rith._board[(5, 14)] = Circle(49, Player.odd)
    rith._board[(6, 14)] = Circle(81, Player.odd)
    rith._board[(7, 14)] = Triangle(90, Player.odd)
    rith._board[(8, 14)] = Triangle(100, Player.odd)
    ## row 13
    rith._board[(3, 13)] = Circle(3, Player.odd)
    rith._board[(4, 13)] = Circle(5, Player.odd)
    rith._board[(5, 13)] = Circle(7, Player.odd)
    rith._board[(6, 13)] = Circle(9, Player.odd)


settings_fulke_1 = {
    'board_setup': 'fulke_1',
    'taking.equality.flight': False,
    'taking.eruption': False,
    'taking.siege.block_marches': True,
    'taking.siege.surrounded': False,
    'taking.addition.marches': True,
    'taking.addition.line_adjacency': False,
    'taking.addition.any_adjacency': False,
    'taking.multiplication.marches': True,
    'taking.multiplication.void_spaces': False,
    'victory.take_pyramid_first': True,
    # 'victory.bodies': -1,
    # 'victory.goods': False,
    # 'victory.goods.num': -1,
    # 'victory.quarrels': -1,
    # 'victory.honour': -1,
}

settings_custom_1 = {
    'board_setup': 'fulke_1', # starts closer together
    'taking.equality.flight': False, # flight should be for jumping only
    'taking.eruption': True, # otherwise the opening game seems slow, and might give a more "math-y" feel
    # after all, what is the equivalent of an "archer"?
    'taking.siege.block_marches': True,
    'taking.siege.surrounded': True,
    'taking.addition.marches': True,
    'taking.addition.line_adjacency': True,
    'taking.addition.any_adjacency': False,
    'taking.multiplication.marches': True,
    'taking.multiplication.void_spaces': False, # eruption better
    'victory.take_pyramid_first': True, # forces the enemy to go after it
## 
    # 'victory.bodies': 1,
    # 'victory.bodies': -1,
    # 'victory.goods': False,
    # 'victory.goods.num': -1,
    # 'victory.quarrels': -1,
    # 'victory.honour': -1,
}
