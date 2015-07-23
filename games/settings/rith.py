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
