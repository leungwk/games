def _score_area_count(conga, player):
    ## area count (in [1,10])
    area_count_player = conga.area_count(player)
    opponent = conga.opponent(player)
    area_count_opponent = conga.area_count(opponent)
    score_area_count = (area_count_player -area_count_opponent)/10.
    return score_area_count


def _score_border_concentration(conga, player):
    ## TODO: Player_type, type(player)., or something else?
    ## corner, side, center -ness
    ## concentration of stones (separate out >= 3 and \lt 3 conditions)
    ## assuming a 4x4 board
    borderness_player = borderness_opponent = 0
    concentration_player = concentration_opponent = 0
    for coord_src, cell_src in conga._board.items():
        cell_player = cell_src.player
        if cell_player not in [type(player).black, type(player).white]: # using type() seems ugly ...
            continue
        cell_opponent = conga.opponent(player)
        ## border in [0,16]
        if coord_src in [(1, 1), (1, 4), (4, 1), (4, 4)]: # corners
            if player == cell_player:
                borderness_player += 2
            else:
                borderness_opponent += 2
        elif coord_src in [(2, 2), (2, 3), (3, 2), (3, 3)]: # center
            pass
        else: # side
            if player == cell_player:
                borderness_player += 1
            else:
                borderness_opponent += 1
        ## concentration (in [0,3])
        ## tuned when number of stones adds up to 10
        if 4 <= cell_src.num <= 5:
            if player == cell_player:
                concentration_player += 1
            else:
                concentration_opponent += 1
        elif cell_src.num >= 6:
            if player == cell_player:
                concentration_player += 3
            else:
                concentration_opponent += 3
    # borderness_player /= 16.
    # borderness_opponent /= 16.
    score_borderness = (borderness_player -borderness_opponent)/16.
    # concentration_player /= 3.
    # concentration_opponent /= 3.
    score_concentration = (concentration_player -concentration_opponent)/3.
    return score_borderness, score_concentration


def heuristic_1(conga, player):
    """Score how 'good' the current board is for player.

    How much area does player take up?
    How much area does the opponent potentially take up?

    ====
    assuming the root player was max player? (there's something strange that it doesn't account for whether player is max or min)

    16 points per feature

    (why input player? because search requires taking opponent's view. However, it will ignore whose /turn/ it is, as set in the Game board)

    Assuming if good for player, is bad for opponent? (hence also calculate for opponent those features).

    Assuming a 4x4 board
    """
    # from conga import Player

    ## all heuristics variables should be within [-1,1] (or [0,1] if assuming the opponent provides the opposite half), and the weight will adjust this
    ## TODO: use [-1,1] (assuming symmetric; everything is wrt to current player)
    weight_area = 8
    weight_ratio_avail_moves = 8 # probably somewhat correlates with area
    weight_border = -8
    weight_concentration = -8
    ## shapes
    weight_victory_hole = 32*2

    ## terminal check
    opponent = conga.opponent(player)
    if conga._is_line_formed():
        return float('-Inf') if conga.turn == player else float('Inf')

    ## near terminal check
    player_legal_moves = list(conga.get_moves(player))
    if not player_legal_moves:
        return float('-Inf')
    opponent_legal_moves = list(conga.get_moves(opponent))
    if not opponent_legal_moves:
        return float('Inf')

    score_area_count = _score_area_count(conga, player)

    tot_moves = len(player_legal_moves) +len(opponent_legal_moves)
    ratio = 1.0*len(player_legal_moves)/len(opponent_legal_moves)
    score_ratio_avail_moves = min(1, ratio/2.) if ratio >= 1 else -min(1, 1./ratio/2.)

    #### shape heuristics
    ## "victory hole": good if player's turn (also would be caught by 1-ply lookahead)
    ## check all directions
    score_victory_hole = 0
    for move in conga._move_lines: # starts at the edge, so will cover the entire line
        num_empty = num_black = num_white = 0
        seeds = 0 # check for same number
        coord_hole = None
        coord_cell_list = [c for c in conga._board.items_vec(move)]
        for coord, cell in coord_cell_list:
            if cell.player == type(player).none:
                coord_hole = coord
                num_empty += 1
                if num_empty >= 2:
                    break # no line
            elif cell.player == type(player).black:
                num_black += 1
            elif cell.player == type(player).white:
                num_white += 1
            ## does all holes have 0 or the same number of seeds?
            if not seeds:
                seeds = cell.num
            elif seeds != cell.num:
                break # no line
        else: # a line found
            ## TODO: this doesn't make sense if the seeds >= 2, since neighbours can put in at most 1, unless it is the edge
            ## num_empty should == 1, because if it were 0, then it should be game over, and it is supposed to break for >= 2
            ## ... but then again, this heuristic should work on /all/ board positions
            ## hole should be defined
            inline_coords, _ = zip(*coord_cell_list)
            if coord_hole is None:
                return float('-inf') # because it is player's turn, the previous move was the opponent's, and the opponent's move created a line victory
            ##
            for coord_nei in conga._board.keys_neighbours(coord_hole):
                ## skip those in the line
                if coord_nei in inline_coords:
                    continue
                cell_nei = conga._board[coord_nei]
                if seeds != cell_nei.num:
                    continue

                if conga.opponent(player) == cell_nei.player:
                    score_victory_hole = -1 # bad for current player
                elif player == cell_nei.player:
                    score_victory_hole = +1
                break # exit outermost loop, since done
            ## TODO: if there are non-neighbours of the hole

    score_borderness, score_concentration = _score_border_concentration(conga, player)

    term_area = weight_area * score_area_count
    term_ratio_avail_moves = weight_ratio_avail_moves * score_ratio_avail_moves
    ## TODO: shouldn't it be bad for a player to be too much on the border, or too concentrated?
    term_borderness = weight_border * score_borderness
    term_concentration = weight_concentration * score_concentration
    term_victory_hole = weight_victory_hole * score_victory_hole

    return term_area +term_ratio_avail_moves +term_borderness +term_concentration +term_victory_hole
