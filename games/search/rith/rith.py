from games.search.rith.siege import _score_siege_surrounded, _score_siege_surrounded_2, BoxShape
from games.rith.piece import NONE_PIECE, Player, PieceName
from games.rith.move import DONE_MOVE, DECLARE_VICTORY_MOVE

def _bound(low, val, high):
    if val < low:
        return low
    elif val > high:
        return high
    return val


def heuristic_1(rith, player):
    w_siegeness = 16
    w_prisoner = 64
    # w_area_count = 4
    w_forwardness = 2
    w_pyramid_fullness = 64

    opponent = Player.opponent(player)

    ## pre-calculate some frequently used stats
    stats = {k: 0 for k in
             ['num_even', 'num_odd', 'num_player', 'num_opponent'] # number on board
             }
    for coord_cur, piece_cur in rith._board.items():
        if piece_cur.colour == Player.even:
            stats['num_even'] += 1
        elif piece_cur.colour == Player.odd:
            stats['num_odd'] += 1
    if player == Player.even:
        stats['num_player'] = stats['num_even']
        stats['num_opponent'] = stats['num_odd']
    elif player == Player.odd:
        stats['num_player'] = stats['num_odd']
        stats['num_opponent'] = stats['num_even']



    available_moves = rith.get_moves(player)
    ## but what if DONE_MOVE is the only move?
    ## OR, will this encourage player to make as many moves as possible during one's own turn?
    num_moves = {k: 0 for k in ['done', 'vict', 'drop', 'take', 'move']}
    for move in available_moves:
        if move == DECLARE_VICTORY_MOVE:
            return float('inf')
        elif move.type == 'move':
            num_moves['move'] += 1
        elif move.type == 'take':
            num_moves['take'] += 1
        elif move.type == 'drop':
            num_moves['drop'] += 1
        elif move == DONE_MOVE:
            num_moves['done'] += 1

    w_move = 2
    w_drop = 2
    w_done = -1
    w_take = 32
    tot_move_eval = \
      w_move * min(32, num_moves['move']) + \
      w_drop * min(4, num_moves['drop']) + \
      w_done * min(1, num_moves['done']) + \
      w_take * min(8, num_moves['take'])

    ## pyramid fullness
    ## in [-1,1]
    pyramid_fullness_player = pyramid_fullness_opponent = 0
    # p_num = 0
    if player == Player.even:
        denom_player = 91
        denom_opponent = 190
    else:
        denom_player = 190
        denom_opponent = 91

    even_forward = 0
    odd_forward = 0
    for coord_cur, piece_cur in rith._board.items():
        ## piece forwardness
        ## or, the soviet army heuristic:
        ## "it takes more courage to retreat than to advance"
        if piece_cur.colour == Player.even:
            even_forward += coord_cur[1]
        elif piece_cur.colour == Player.odd:
            odd_forward += (16 -coord_cur[1]) # assuming a fixed rith board size

        ## pyramid fullness; [-1,1]
        if piece_cur.name != PieceName.pyramid:
            continue
        if piece_cur.colour == player:
            pyramid_fullness_player = piece_cur.num/denom_player
        else:
            pyramid_fullness_opponent = piece_cur.num/denom_opponent

    tot_pyramid_fullness = w_pyramid_fullness * (pyramid_fullness_player -pyramid_fullness_opponent)



    ## forwardness; [-1,1]
    even_forwardness = even_forward/(16*stats['num_even']) if stats['num_even'] > 0 else 0
    odd_forwardness = odd_forward/(16*stats['num_odd']) if stats['num_odd'] > 0 else 0
    if player == Player.even:
        diff_forwardness = even_forwardness -odd_forwardness # diff from opponent
    elif player == Player.odd:
        diff_forwardness = odd_forwardness -even_forwardness
    tot_forwardness = w_forwardness * diff_forwardness



    ## siegeness; [-1,1]
    cnt_siegeness = {k: 0 for k in ['player', 'opponent']}
    for coord_cur, piece_cur in rith._board.items():
        if piece_cur == NONE_PIECE:
            continue
        # siegeness = _score_siege_surrounded(rith, coord_cur) # in [0,1] # too slow
        siegeness = _score_siege_surrounded_2(rith, coord_cur) # in [0,1]
        whose_piece_cur = 'player' if piece_cur.colour == player else 'opponent'
        cnt_siegeness[whose_piece_cur] += siegeness

    siegeness_player = cnt_siegeness['player']/stats['num_player'] if stats['num_player'] > 0 else 0
    siegeness_opponent = cnt_siegeness['opponent']/stats['num_opponent'] if stats['num_opponent'] > 0 else 0
    tot_siegeness = w_siegeness * (siegeness_opponent -siegeness_player)

    if player == Player.even:
        player_prisoners = rith._board.prisoners_held_by_even
        opponent_prisoners = rith._board.prisoners_held_by_odd
    elif player == Player.odd:
        player_prisoners = rith._board.prisoners_held_by_odd
        opponent_prisoners = rith._board.prisoners_held_by_even

    r = len(player_prisoners)/len(opponent_prisoners) if len(opponent_prisoners) > 0 else 1
    tot_prisoner_ness = w_prisoner *_bound(-1, (r -1), 1)

    return sum([tot_move_eval, tot_pyramid_fullness, tot_forwardness, tot_siegeness, tot_prisoner_ness])
