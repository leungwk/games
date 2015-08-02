from games.rith.move import deltas_cross, deltas_xshape, Move
from games.common.coord import Coord
from games.rith.piece import NONE_PIECE, OOB_PIECE, Player
import copy

class CoordPiece(object): # sub-class of View
    def __init__(self, coord, piece):
        self.coord = coord
        self.piece = piece


    def __str__(self):
        return '({}, {})'.format(self.coord, self.piece)


    def __repr__(self):
        return '({}, {})'.format(repr(self.coord), repr(self.piece))


class PlusShape(object):
    def __init__(self, board, coord): # "look"
        self.start = CoordPiece(coord, board.get(coord, OOB_PIECE))

        new_coord = Coord.add(coord, (+1, 0))
        self.east = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))

        new_coord = Coord.add(coord, (0, -1))
        self.south = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))

        new_coord = Coord.add(coord, (-1, 0))
        self.west = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))

        new_coord = Coord.add(coord, (0, +1))
        self.north = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))


    def keys_wind(self):
        for direction in [self.east, self.south, self.west, self.north]:
            yield direction.coord


    def items_wind(self):
        for direction in [self.east, self.south, self.west, self.north]:
            yield direction.coord, direction.piece


class EcksShape(object):
    def __init__(self, board, coord):
        self.start = CoordPiece(coord, board.get(coord, OOB_PIECE))

        new_coord = Coord.add(coord, (+1, +1))
        self.north_east = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))

        new_coord = Coord.add(coord, (+1, -1))
        self.south_east = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))

        new_coord = Coord.add(coord, (-1, -1))
        self.south_west = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))

        new_coord = Coord.add(coord, (-1, +1))
        self.north_west = CoordPiece(new_coord, board.get(new_coord, OOB_PIECE))


    def keys_wind(self):
        for direction in [self.north_east, self.south_east, self.south_west, self.north_west]:
            yield direction.coord


    def items_wind(self):
        for direction in [self.north_east, self.south_east, self.south_west, self.north_west]:
            yield direction.coord, direction.piece


def _pieces_movable(rith, coord_dest, allow_unoccupied=False):
    ## find all pieces moveable into coord_dest
    ## allow_unoccupied: consider what if coord_dest where unoccupied
    piece_dest = rith._board.get(coord_dest, OOB_PIECE)
    if not allow_unoccupied:
        if piece_dest != NONE_PIECE:
            return []
    else:
        if piece_dest == OOB_PIECE:
            return []
        ## takes ~70% of the running time under the current architecture
        # rith_new = copy.deepcopy(rith)
        # rith_new._board[coord_dest] = NONE_PIECE
        tmp_piece = rith._board[coord_dest]
        rith._board[coord_dest] = NONE_PIECE

    acc_pieces = []
    for coord_cur, piece_cur in rith._board.items():
        if piece_cur == NONE_PIECE:
            continue
        if coord_cur == coord_dest:
            continue
        for deltas in [piece_cur.marches, piece_cur.flights]:
            for coord_delta in rith._board.keys_fan(coord_cur, deltas):
                if coord_delta != coord_dest:
                    continue
                move_obj = Move(coord_cur, coord_delta)
                if rith.is_legal_move(move_obj):
                    acc_pieces.append((coord_cur, piece_cur))
                    break
    if allow_unoccupied:
        ## restore it
        ## currently assuming nothing occurs when manipulating state
        ## also assuming something about thread safety when doing this
        rith._board[coord_dest] = tmp_piece
    return acc_pieces


def _score_siege_surrounded(rith, coord_dest):
    siegeness = 0
    shape_ecks = EcksShape(rith._board, coord_dest)
    shape_plus = PlusShape(rith._board, coord_dest)
    for shape in [shape_plus, shape_ecks]:
        res = _score_siege_surrounded_shape(rith, coord_dest, shape)
        if res is None:
            continue
        siegeness = max(siegeness, res)
    return siegeness/100.


def _bound(low, val, high):
    if val < low:
        return low
    elif val > high:
        return high
    return val


def _score_siege_surrounded_shape(rith, coord_dest, shape):
    ## number of potential sieges
    ## number of sides (within the shape) surrounded, and if by piece or by border
    ## sieging the pyramid or not when taking.siege.surrounded enabled

    ## assuming a standard 8x16 board; and "standard" rules

    ## half siege (2 of 4, and another piece can march/fly into the missing space); potential/no potential
    ## imminent siege (3 of 4); potential/no potential
    ## siege (4 of 4)

    """Calculate "siegeness" for the piece at coord_dest

Consider all combinations of size 4 of oob, none, player, opponent, except where #oob in {3,4}. Organize by partitions of 4

# 4
{none, player, opponent} x4

# 3 +1
none x3, {player, opponent, oob} x1
player x3, {none, opponent, oob} x1
opponent x3, {none, player, oob} x1

# 2 +2
none, player
none, oob
none, opponent

player, opponent
player, oob

opponent, oob

# 2 +1 +1
none x2
    player, opponent
    player, oob
    opponent, oob

player x2
    none, opponent
    none, oob
    opponent, oob

opponent x2
    none, player
    none, oob
    player, oob

oob x2
    none, player
    none, opponent
    player, opponent

# 1 +1 +1 +1
none, player, opponent, oob

Given these combinations, (totally) order them by "siege-ness" (whether block_marches, or surrounded), while also considering _pieces_movable to where NONE_PIECE exists.
    """

    if not rith.settings.get('taking.siege.surrounded', False):
        return None

    piece_dest = rith._board.get(coord_dest, OOB_PIECE)
    if piece_dest in [OOB_PIECE, NONE_PIECE]:
        return None

    player = piece_dest.colour # ie. use player's perspective of the piece being sieged
    opponent = Player.opponent(player)

    siegeness = 0
    #### rather than loop and delta, "perceive", count, and evaluate as a bundle
    ## perceive
    # shape_ecks = EcksShape(rith._board, coord_dest) # TODO: iterate

    # shape_plus = PlusShape(rith._board, coord_dest)
    coords_shape = {x for x in shape.keys_wind()}

    ## count
    stats = {k: 0 for k in ['oob', 'none', 'player', 'opponent'] +['potential_opponent', 'potential_player', 'pinned_player', 'pinned_opponent'] +['potential_opponent_distinct', 'potential_player_distinct', 'pinned_player_distinct', 'pinned_opponent_distinct']}
    ## depending on how it is represented, there are 5 or 8 features, +2 or +4
    for coord_wind, piece_wind in shape.items_wind():
        ## get all pieces that can move to coord_wind but that are not part of the plus shape
        pieces_movable = [(c,p) for c,p in _pieces_movable(rith, coord_wind, allow_unoccupied=True) if c not in coords_shape]

        if piece_wind == OOB_PIECE:
            stats['oob'] += 1
        elif piece_wind == NONE_PIECE:
            stats['none'] += 1
            ## now count the number of potential/anti-potential
            is_distinct_opp = is_distinct_pla = False
            for _, piece_pm in pieces_movable:
                if piece_pm.colour == opponent:
                    stats['potential_opponent'] += 1
                    is_distinct_opp = True
                elif piece_pm.colour == player:
                    stats['potential_player'] += 1
                    is_distinct_pla = True
            if is_distinct_opp:
                stats['potential_opponent_distinct'] += 1
            if is_distinct_pla:
                stats['potential_player_distinct'] += 1
        elif piece_wind.colour == player:
            stats['player'] += 1
            ## now count the number of pinned
            is_pinned = False
            for _, piece_pm in pieces_movable:
                if piece_pm.colour == opponent:
                    stats['pinned_player'] += 1
                    is_pinned = True
            if is_pinned:
                stats['pinned_player_distinct'] += 1
        elif piece_wind.colour == opponent:
            stats['opponent'] += 1
            is_pinned = False
            ## now count the number of anti-pinned
            for _, piece_pm in pieces_movable:
                if piece_pm.colour == opponent:
                    stats['pinned_opponent'] += 1
                    is_pinned = True
            if is_pinned:
                stats['pinned_opponent_distinct'] += 1
    ## evaluate
    ## on a scale of [0,100]
    """
    0,1 opponent+oob are closer to each other than 2, which is just a bit further to 3, whose gap then is larger to 4. Graphically:
    |0  1    2      3        4|
     0123456789012345678901234

    Within each level of opponent/oob, these are moderated, sometimes to the next level, by the number of (anti-)potential and (anti-)pinned pieces

    All else being equal, more is preferred over less for opponent+oob, oob, and none, while vice-versa for pinned_player and potential_opponent.
    pinned_opponent and potential_player are strange cases, esp. if opponent+oob is low.
    """
    ## TODO: not separating out what particular space, ie. potential_player and potential_opponent could both be > 0, but limited to one particular space each
    ## TODO: add more equivalence comments to check the logic
    MAX_SIEGENESS = 100
    # diff_pot_opp_pla = stats['potential_opponent'] -stats['potential_player']
    diff_pin_pla_uniq = stats['pinned_player'] -stats['pinned_player_distinct']
    if (stats['opponent'] +stats['oob']) == 4:
        ## measuring efficiency
        if stats['oob'] == 2:
            siegeness = 100
        elif stats['oob'] == 1:
            siegeness = 98
        elif stats['oob'] == 0:
            siegeness = 96
        ## by the time of a (complete) siege, being surrounded by oob does not matters as much as before
        #
        ## how many opponents are pinned does not matter, even if player's turn (unless they can take)
    elif (stats['opponent'] +stats['oob']) == 3:
        siegeness = 80
        ## Ordered by how "secure" is a player.
        ## roughly, from worse to best: potential_opponent, pinned_player, none (has no potential), potential_player, player
        ##
        if stats['none'] == 1: # implies player == 0
            siegeness = 84 # this will be set as is if potential_player and potential_opponent == 0
            ## if the opponent could threaten to move into the none space, that it changes to the opponent's turn adds at least +8, /and/ it only requires one of the opponent's pieces, not 4
            # if piece_dest.colour == player: # because assumed True
            if rith.turn == player:
                if stats['potential_player'] > 0:
                    siegeness = 80
                siegeness += min(4, stats['potential_opponent']) # ie. the player needs to act now
            else: # opponent's turn
                if stats['potential_opponent'] > 0:
                    siegeness = 92 # almost as good as a siege if the opponent's turn
                siegeness -= min(4, stats['potential_player'])
        elif stats['none'] == 0: # implies player == 1
            ## TODO: not calculating /how many/ potential player or opponent
            siegeness = 76
            if stats['pinned_player'] == 1: # eq. to pinned_player_distinct
                siegeness = 84
                ## says being pinned is equivalent to the player having the potential to occupy a none space, under the threat of the 4 opponent's doing the same on their next turn
                ## says it is 4 units less worse to be pinned than to have an empty space with no potential for the player to move into it during the player's turn, and the opponent has 4 potential pieces
                ## says being pinned is equivalent to there being no potential player or opponent at a none space. This might make sense if one assumes being pinned is bad, but having a player piece occupying the space is good.
        #
        ## oob not dependent on turn
        if stats['oob'] == 2:
            siegeness += 4
            ## says that oob matters more when opponent+oob == 3 rather than 4
            ## says if it's the opponent's turn, and they have a potential to move into a none space, and the player has no potential, and the player's piece is surrounded by two oob, then it is equivalent to being (completely) sieged without any oob; one might question whether "certain potential" is equivalent to an actual functioning result, given that there are other opportunities for the opponent
        elif stats['oob'] == 1:
            siegeness += 2
    elif (stats['opponent'] +stats['oob']) == 2:
        siegeness = 50
        siegeness += -4*stats['player'] # how many spaces does player occupy?
        siegeness += 8*stats['pinned_player_distinct'] # how many uniq player spaces (not pieces) are pinned?
        siegeness += 4*min(2, diff_pin_pla_uniq) # how strong is being pinned?
        # if stats['none'] == 2: # implies player == 0
        #     pass
        # elif stats['none'] == 1: # implies player == 1
        #     pass
        # elif stats['none'] == 0: # implies player == 2
        #     pass
        w_pp = stats['none']//2
        w_po = stats['none']
        if rith.turn == player:
            ## consider overcounting as bonus additives if highly (dis)favourable, in lieu of using exponents
            siegeness += -2*w_pp*min(4, stats['potential_player_distinct'])
            siegeness += 1*w_po*min(4, stats['potential_opponent_distinct'])
            siegeness += -2*min(2, stats['potential_player'])
            siegeness += 1*min(2, stats['potential_opponent'])
        else:
            siegeness += -1*w_pp*min(4, stats['potential_player_distinct'])
            siegeness += 2*w_po*min(4, stats['potential_opponent_distinct'])
            siegeness += -1*min(2, stats['potential_player'])
            siegeness += 2*min(2, stats['potential_opponent'])
        # setting to same difference as opponent+oob == 3
        if stats['oob'] == 2:
            siegeness += 4
        elif stats['oob'] == 1:
            siegeness += 2
    elif (stats['opponent'] +stats['oob']) == 1:
        siegeness = 20
        siegeness += -3*stats['player']
        siegeness += 6*stats['pinned_player_distinct'] # how many uniq spaces (not pieces) pinned? # weighted less than opponent+oob == 2, because many turns exist as a buffer
        siegeness += 3*min(2, diff_pin_pla_uniq) # how strong is being pinned?
        # if stats['none'] == 3:
        #     pass
        # elif stats['none'] == 2:
        #     pass
        # elif stats['none'] == 1:
        #     pass
        # elif stats['none'] == 0:
        #     pass
        w_pp = stats['none']//2
        w_po = stats['none']
        if rith.turn == player:
            ## consider overcounting as bonus additives if highly (dis)favourable, in lieu of using exponents
            siegeness += -2*w_pp*min(4, stats['potential_player_distinct'])
            siegeness += 1*w_po*min(4, stats['potential_opponent_distinct'])
            siegeness += -2*min(2, stats['potential_player'])
            siegeness += 1*min(2, stats['potential_opponent'])
        else:
            siegeness += -1*w_pp*min(4, stats['potential_player_distinct'])
            siegeness += 2*w_po*min(4, stats['potential_opponent_distinct'])
            siegeness += -1*min(2, stats['potential_player'])
            siegeness += 2*min(2, stats['potential_opponent'])
        #
        # setting to same difference as opponent+oob == 3
        if stats['oob'] == 1:
            siegeness += 2
    elif (stats['opponent'] +stats['oob']) == 0:
        siegeness = 0
        siegeness += -2*stats['player']
        siegeness += 4*stats['pinned_player_distinct'] # how many uniq spaces (not pieces) pinned?
        siegeness += 2*min(2, diff_pin_pla_uniq) # how strong is being pinned?
        # if stats['none'] == 4:
        #     pass
        # elif stats['none'] == 3:
        #     pass
        # elif stats['none'] == 2:
        #     pass
        # elif stats['none'] == 1:
        #     pass
        # elif stats['none'] == 0:
        #     pass
        w_pp = stats['none']//2
        w_po = stats['none']
        if rith.turn == player:
            ## consider overcounting as bonus additives if highly (dis)favourable, in lieu of using exponents
            siegeness += -2*w_pp*min(4, stats['potential_player_distinct'])
            siegeness += 1*w_po*min(4, stats['potential_opponent_distinct'])
            siegeness += -2*min(2, stats['potential_player'])
            siegeness += 1*min(2, stats['potential_opponent'])
        else:
            siegeness += -1*w_pp*min(4, stats['potential_player_distinct'])
            siegeness += 2*w_po*min(4, stats['potential_opponent_distinct'])
            siegeness += -1*min(2, stats['potential_player'])
            siegeness += 2*min(2, stats['potential_opponent'])
    siegeness -= min(4, stats['pinned_opponent']) # this totally depends on the scale of differences used
    siegeness = _bound(0, siegeness, MAX_SIEGENESS)
    return siegeness
