#!/usr/bin/env python

from enum import Enum
#import numpy as np
#import pylab as pl
#from numpy import *
import random
#import Queue
import collections# import deque
from statlib import stats
import time

#from multimethod import multimethod
#import copy # doesn't work with Enum for some reason (they don't appear on the copy'd game_board)

# a = matrix([[1,2],[3,4]])
# st = "string"
# print(a)
# print(st)

# # M-/

# def fact(n):
#     pass

# b = array(["Hello","world","!"])
# c = matrix([["Hello","world","!"],["world","ok","?"]])


####

""" should be enum
8 1 2
7   3
6 5 4
"""
wind = Enum('north','ne','east','se','south','sw','west','nw')

player = Enum('invalid','none','black','white') # invalid, no player, player 1, player 2

def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


class game_cell(object):
    def __init__(self, stone_cnt=0, poss=player.none):
        self.stone_cnt = stone_cnt
        self.poss = poss # possessor

    def __str__(self):
        st = 'A' if self.stone_cnt == 10 else str(self.stone_cnt) # hex number
        po = '_'
        if self.poss == player.black:
            po = 'B'
        elif self.poss == player.white:
            po = 'W'
        else:
            po = '_'
        return st +po
    def __eq__(a, b):
        """Equal in stone count and player"""
        return a.stone_cnt == b.stone_cnt and \
               a.poss == b.poss

    def __ne__(a, b): # this should always be defined if __eq__ is defined, otherwise there will be asymmetry
        return not (a == b)

    def is_empty(self):
        ## todo: should really have self.poss == player.none too
        return self.stone_cnt == 0

    def set_stone_count(self, cnt):
        self.stone_cnt = cnt
    def set_player(self, poss):
        self.poss = poss

    def get_stone_count(self):
        return self.stone_cnt
    def get_player(self):
        return self.poss
    def get_opponent(self):
        if self.poss == player.black:
            return player.white
        if self.poss == player.white:
            return player.black
        return player.none

class game_move:
    def __init__(self, coord=(-1,-1), direction=wind.north):
        self.coord = coord
        self.direction = direction

    def __eq__(a,b):
#        if a == None or b == None:
#            return False

        return a.coord == b.coord and a.direction == b.direction

    def __str__(self):
        return str(self.coord) +' ' +str(self.direction)

## game grid has (1,1) at bottom left, and (4,4) at top right
## stored order is (0,0) top level, and (3,3) bottom right (like matricies, but zero index)
class game_board(object):
    ## define class attributes here (like static variables)

    def __init__(self):
        ## init to 4x4 object matrix

# if numpy available
#         self.grid = np.array([[game_cell(0,player.none) for i in xrange(4)] for j in xrange(4)]) # problem with numpy's copy method
#         self.grid[0,0] = game_cell(10,player.black)
#         self.grid[3,3] = game_cell(10,player.white)


        self.grid = [[game_cell(0,player.none) for i in xrange(4)] for j in xrange(4)]
        self.grid[0][0] = game_cell(10,player.black)
        self.grid[3][3] = game_cell(10,player.white)

        self.maxx = 4
        self.maxy = 4
        self.minx = 1
        self.miny = 1
        self.nowhere_cell = game_cell(-1,player.invalid)
        self.nowhere_coord = (-1,-1)
        self.invalid_move = game_move(self.nowhere_coord,wind.north)

    def __str__(self):
#        return str(self.grid)
#        return str(np.array(self.grid))

        s = ''
        for i in range(0,4):
            for j in range(0,4):
                s = s +str(self.grid[i][j]) +' '
            s = s +'\n'
        return s

    def __eq__(a, b):
        for i in range(0,4):
            for j in range(0,4):
#                if a.grid[i,j] != b.grid[i,j]: # use if numpy available
                if a.grid[i][j] != b.grid[i][j]:
                    return False
        return True

    def deepcopy(self):
        new_gb = game_board()
        for i in range(0,4):
            for j in range(0,4):
#                cell = self.grid[i,j]
                cell = self.grid[i][j]

                new_cell = game_cell(cell.get_stone_count(),cell.get_player())
#                new_gb.grid[i,j] = new_cell
                new_gb.grid[i][j] = new_cell
        return new_gb

#     def __deepcopy__(self, memo={}):
#         result = self.__class__()
#         memo[id(self)] = result
#         result.__init__(copy.deepcopy(tuple(self), memo))
#         return result        

    def is_valid_coord(self, coord):
        if len(coord) != 2:
#            raise Exception('Invalid coordinate size' +':' +str(len(coord)))
            return False

        if coord[0] > self.maxx or \
               coord[0] < self.minx or \
               coord[1] > self.maxy or \
               coord[1] < self.miny:
#            raise Exception('Invalid coordinate' +str(coord))
            return False
        return True

    def coord_to_index(self, coord):
        """coord
(1,4) (2,4) (3,4) (4,4)
(1,3) (2,3) (3,3) (4,3)
(1,2) (2,2) (3,2) (4,2)
(1,1) (2,1) (3,1) (4,1)

maps to indicies

(0,0) (0,1) (0,2) (0,3)
(1,0) (1,1) (1,2) (1,3)
(2,0) (2,1) (2,2) (2,3)
(3,0) (3,1) (3,2) (3,3)

(this is messed)"""
        if coord == (1,4): return (0,0)
        if coord == (2,4): return (0,1)
        if coord == (3,4): return (0,2)
        if coord == (4,4): return (0,3)

        if coord == (1,3): return (1,0)
        if coord == (2,3): return (1,1)
        if coord == (3,3): return (1,2)
        if coord == (4,3): return (1,3)

        if coord == (1,2): return (2,0)
        if coord == (2,2): return (2,1)
        if coord == (3,2): return (2,2)
        if coord == (4,2): return (2,3)

        if coord == (1,1): return (3,0)
        if coord == (2,1): return (3,1)
        if coord == (3,1): return (3,2)
        if coord == (4,1): return (3,3)           

#     @multimethod((int,int),int,player) # doesn't work
#     def set_cell(self, coord, stone_cnt, poss):
#         if not self.is_valid_coord(coord):
#             return None

#         self.set_cell(coord,game_cell(stone_cnt, poss))

#    @multimethod((int,int),game_cell)
    def set_cell(self, coord, cellobj):
        if not self.is_valid_coord(coord):
            return False # unsuccessful

        idx = self.coord_to_index(coord)
#        self.grid[idx[0],idx[1]] = cellobj
        self.grid[idx[0]][idx[1]] = cellobj
        return True

    def get_cell(self, coord):
        if not self.is_valid_coord(coord):
            return self.nowhere_cell

        idx = self.coord_to_index(coord)
#        return self.grid[idx[0],idx[1]]
        return self.grid[idx[0]][idx[1]]

    def get_next_cell(self, coord, direction):
        c = self.get_next_coord(coord, direction)
        if c is self.nowhere_coord:
            return self.nowhere_cell

        return self.get_cell(c)

    def get_next_coord(self, coord, direction):
        if not self.is_valid_coord(coord):
            return self.nowhere_coord

        ## should really check boundaries
        res = self.nowhere_coord
        if direction == wind.north:   res = (coord[0],coord[1]+1)
        elif direction == wind.ne:    res = (coord[0]+1,coord[1]+1)
        elif direction == wind.east:  res = (coord[0]+1,coord[1])
        elif direction == wind.se:    res = (coord[0]+1,coord[1]-1)
        elif direction == wind.south: res = (coord[0],coord[1]-1)
        elif direction == wind.sw:    res = (coord[0]-1,coord[1]-1)
        elif direction == wind.west:  res = (coord[0]-1,coord[1])
        elif direction == wind.nw:    res = (coord[0]-1,coord[1]+1)

        if not self.is_valid_coord(res):
            return self.nowhere_coord
        return res

    def get_cell_line(self, coord, direction):
        cell_list = []
        acell = self.get_cell(coord)
        while acell is not self.nowhere_cell:
            cell_list.append(acell)
            acell = self.get_next_cell(coord, direction)
            coord = self.get_next_coord(coord, direction)
        return cell_list

    def is_legal_move(self, move):
        coord = move.coord
        direction = move.direction

        curr_cell = self.get_cell(coord)
        if curr_cell.is_empty():
            return False

        next_cell = self.get_next_cell(coord, direction)
        next_poss = next_cell.get_player()

        if next_cell is self.nowhere_cell or \
           next_poss is curr_cell.get_opponent():
            return False
        return True

#     @multimethod(tuple(int,int),wind) # doesn't work, again
#     def get_legal_move(self, coord, direction):
#         move = game_move(coord, direction)
#         return self.get_legal_move(move)

#    @multimethod(game_move)
    def get_legal_move(self, move):
        if self.is_legal_move(move):
            return move
        return self.invalid_move

    def get_legal_moves(self, coord):
        moves = []
        for d in wind:
            move = self.get_legal_move(game_move(coord,d))
            if move is not self.invalid_move:
                moves.append(move)
        return moves

    def get_legal_moves_count(self, coord):
        cnt = 0
        for d in wind:
            move = self.get_legal_move(game_move(coord,d))
            if move is not self.invalid_move:
                cnt += 1
        return cnt

    def get_all_legal_moves_count(self, pla):
        cnt = 0
        for i in range(1,5):
            for j in range(1,5):
                coord = (i,j)
                curr_cell = self.get_cell(coord)
                if curr_cell.get_player() is pla:
                    cnt += self.get_legal_moves_count(coord)
        return cnt

    def get_all_legal_moves(self, pla):
        moves = []
        for i in range(1,5):
            for j in range(1,5):
                coord = (i,j)
                curr_cell = self.get_cell(coord)
                if curr_cell.get_player() is pla:
                    moves.append(self.get_legal_moves(coord))
        return flatten(moves)

    def peek_move(self, move):
        """Returns movement directions, but doesn't actually displace stones"""
        return self.get_cell_line(move.coord,move.direction)

    def area_count(self, pla):
        """Counts number of cells taken up by player"""
        count = 0
        for i in range(1,5):
            for j in range(1,5):
                cell = self.get_cell((i,j))
                if cell.get_player() == pla:
                    count += 1
        return count

## span tree

    def get_opponent(self, pla):
        opponent = player.invalid
        if pla == player.white or \
           pla == player.black:
            opponent = player.black if pla == player.white else player.white
        elif pla == player.none:
            opponent = player.none
        else:
            opponent = player.invalid
        return opponent

    def get_neighbour_coords(self, coord):
        """8 potential neighbours, only returns those that are on the board"""
        cx = coord[0]
        cy = coord[1]

        north = (cx,cy+1)
        ne = (cx+1,cy+1)
        east = (cx+1,cy)
        se = (cx+1,cy-1)
        south = (cx,cy-1)
        sw = (cx-1,cy-1)
        west = (cx-1,cy)
        nw = (cx-1,cy+1)

        coord_list = []
        for direction in (north,ne,east,se,south,sw,west,nw):
            cell = self.get_cell(direction)
            if cell is not self.nowhere_cell:
                coord_list.append(direction)
        return coord_list

    def get_neighbour_cells(self, coord):
        """8 potential neighbours"""
        cx = coord[0]
        cy = coord[1]

        north = (cx,cy+1)
        ne = (cx+1,cy+1)
        east = (cx+1,cy)
        se = (cx+1,cy-1)
        south = (cx,cy-1)
        sw = (cx-1,cy-1)
        west = (cx-1,cy)
        nw = (cx-1,cy+1)

        cell_list = []
        for direction in (north,ne,east,se,south,sw,west,nw):
            cell = self.get_cell(direction)
            if cell is not self.nowhere_cell:
                cell_list.append(cell)
        return cell_list

    def span_tree_count(self, coord):
        """Returns the count of the spanning tree of the given stone at coord. Done to determine the size of the 'enclosure' available to the stone at coord."""
        pla = self.get_cell(coord).get_player()
        opp = self.get_opponent(pla)

        if pla == player.none:
            return 0 # nothing to expand

        if pla == player.invalid:
            return -1 # something went wrong

        ## cell contains black or white stone

        neighbours = self.get_neighbour_coords(coord)

        open_set = set(neighbours) # coords to explore
        closed_set = set([coord]) # coords previously explored # including coord already given

#        print "open_set (begin):", open_set
#        print "closed_set (begin):", closed_set

        while len(open_set) is not 0:
            coordinate = open_set.pop()
            cell = self.get_cell(coordinate) # self: now I wish I had attached coordinates to these cells
            if cell is self.nowhere_cell:
                continue # go to next neighbours

            ## cell is a valid cell

            cell_pla = cell.get_player()
            if cell_pla == opp: # is an opponent
                continue # discard

            ## cell is friendly or empty

            ## since using a set, can add indiscriminatenly and it will automatically remove duplicates.
#            print coordinate
            closed_set.add(coordinate)
#            print "closed_set:",closed_set

            ## otherwise "TypeError: list objects are unhashable"
            for nei in self.get_neighbour_coords(coordinate):
                if nei not in closed_set: # do not want to revisit nodes
                    open_set.add(nei)


#        print "closed set (end):",closed_set
        return len(closed_set) # includes origin

    def span_trees_count(self, pla):
        span_cnt = 0
        for i in range(1,5):
            for j in range(1,5):
                cell = self.get_cell((i,j))
                if cell.get_player() == pla:
                    span_cnt += self.span_tree_count((i,j))
        return span_cnt

##

    def move_stones(self, move):
        coord = move.coord
        direction = move.direction

        cline = self.get_cell_line(coord, direction)
        if cline == []:
            return False

        first = cline[0]
        if first.is_empty():
            return False # nothing moved

        # at least one stone in first
        move = self.get_legal_move(game_move(coord, direction))
        if move is self.invalid_move:
            return False

        # move is valid

        stone_cnt = first.get_stone_count() # number of stones to move
        drop_cnt = 0 # first movement (and also how many stones to drop)

        curr_coord = coord

        first_poss = first.get_player()

        ## reset cell where stones were moved from
        first.set_stone_count(0)
        first.set_player(player.none)

        for cell in cline:
            curr_cnt = cell.get_stone_count()
            curr_poss = cell.get_player()

            next_cell = self.get_next_cell(curr_coord, direction)
            next_poss = next_cell.get_player()
            next_coord = self.get_next_coord(curr_coord, direction)

            remain_cnt = stone_cnt -drop_cnt

            ## check if either blocked or at edge of board
            if (next_poss is not first_poss and next_poss is not player.none) or \
               next_cell is self.nowhere_cell or \
               remain_cnt <= 0:

                ## dump remaining stones into current cell
                cell.set_stone_count(stone_cnt +curr_cnt)
                cell.set_player(first_poss)

                return True

            ## next cell empty or is friendly, and more to go
            cell.set_stone_count(drop_cnt +curr_cnt)
            if drop_cnt > 0:
                cell.set_player(first_poss)
            else: # is first cell
                pass # is already set to no player

            stone_cnt = remain_cnt
            drop_cnt += 1
            curr_coord = next_coord
        return True

class agent: # is this how to do an "abstract" class
    def __init__(self):
        self.__init_values()

    def __init_values(self):
        self.explore_count = 0
        self.explore_depth = 0

        self.history = collections.deque()

        self.max_history = 4 # needed to break cycles of length 3 (or 4?) between player/opponent
        self.history.append((game_move((-1,-1),wind.north),game_board()))
        ## append() and popleft() to treat as FIFO

        self.explore_count_history = collections.deque()

        self.explore_depth_history = collections.deque()

        self.decision_time_history = collections.deque() # how long it takes to make one decision

    def restart_agent(self):
        self.__init_values()

    def get_stats(self):
        stat = {}
#        stat = {'mean_explore_count': 0, 'mean_depth_count': 0,\
#                'var_explore_count': 0, 'var_depth_count': 0}
        explore_count_history_list = list(self.explore_count_history)
        explore_depth_history_list = list(self.explore_depth_history)
        decision_time_history_list = list(self.decision_time_history)

        stat['mean_explore_count'] = stats.mean(explore_count_history_list[1:]) # remove first elements since it is for the first move, which is compartively small, and hence distorts the value
        stat['var_explore_count'] = stats.var(explore_count_history_list[1:])

        stat['mean_depth_count'] = stats.mean(explore_depth_history_list[1:])
        stat['var_depth_count'] = stats.var(explore_depth_history_list[1:])

        stat['mean_decision_time'] = stats.mean(decision_time_history_list[1:])
        stat['var_decision_time'] = stats.var(decision_time_history_list[1:])
        return stat

    def print_stats(self):
        print self.explore_count_history
        print self.explore_depth_history
        print "mean explore count:",stats.mean(list(self.explore_count_history))
        print "mean explore depth:",stats.mean(list(self.explore_depth_history))

    def decision(self, gb, pla):
        pass

    def get_opponent(self, pla):
        opponent = player.invalid
        if pla == player.white or \
           pla == player.black:
            opponent = player.black if pla == player.white else player.white
        elif pla == player.none:
            opponent = player.none
        else:
            opponent = player.invalid
        return opponent

    def heuristic(self, gb, pla):
        """This heuristic weights positively area taken up by player, and weights negatively number of potential moves of opponent. In addition, this weights negativly the 'enclosed' area the opponent has"""
        area_weight = 10
#        opponent_move_weight = -1
        opponent_spantree_weight = -200

        acnt = gb.area_count(pla)
        pla_move_cnt = gb.get_all_legal_moves_count(pla)
        if pla_move_cnt == 0:
            return float('-Inf')

        opponent = self.get_opponent(pla)
        opp_move_cnt = gb.get_all_legal_moves_count(opponent)
#        print "opp_move_cnt",opp_move_cnt
        if opp_move_cnt == 0:
            return float('Inf')

        opp_spantree_cnt = gb.span_trees_count(opponent)

        return acnt * area_weight + \
               opp_spantree_cnt * opponent_spantree_weight

#         return acnt * area_weight + \
#                opp_move_cnt * opponent_move_weight + \
#                opp_spantree_cnt * opponent_spantree_weight


        ## no good
#        opponent_future_move_weight = -0.01
        #opp_future_move_cnt = 0
        ## calculate future moves of opponent and how many potential moves they offer
#         for move in opponent_moves:
#             new_gb = gb.deepcopy()
#             new_gb.move_stones(move)
#             opp_future_move_cnt += len(new_gb.get_all_legal_moves(opponent))
#        return acnt * area_weight + \
#               opp_move_cnt * opponent_move_weight
#              + opp_future_move_cnt * opponent_future_move_weight






#         """This heuristic select number of '3' and '4' moves that are available"""
#         pla_moves = gb.get_all_legal_moves(pla)
#         opponent = player.black if pla == player.white else player.white

#         hval = 0
#         for pla_move in pla_moves:
#             move_len = len(gb.peek_move(pla_move))
#             if move_len == 3 or move_len == 4:
#                 hval += 1
#         return hval

#         """This heuristic measures how many potential moves the opponent has available for any move player makes (less is better) (like a lookahead)"""
#         pla_moves = gb.get_all_legal_moves(pla)
#         opponent = player.black if pla == player.white else player.white

#         opp_move_cnt = 0
#         for pla_move in pla_moves:
#             new_gb = gb.deepcopy()
#             new_gb.move_stones(pla_move)
#             opp_move_cnt += len(new_gb.get_all_legal_moves(opponent))
#         return -opp_move_cnt

#         """This heuristic measures how many free moves player has compared to opponent (this heuristic also sucks)"""
#         pla_move_cnt = len(gb.get_all_legal_moves(pla))
#         opponent = player.black if pla == player.white else player.white
#         opp_move_cnt = len(gb.get_all_legal_moves(opponent))
#         return pla_move_cnt -opp_move_cnt

    def terminal_state(self, gb, pla):
        return gb.get_all_legal_moves_count(pla) == 0

class random_agent(agent):
    def __init__(self):
        pass

    def restart_agent(self):
        agent.restart_agent(self)

    def decision(self, gb, pla):
        return self.random_decision(gb, pla)

    def random_decision(self, gb, pla):
        moves = gb.get_all_legal_moves(pla)
        if moves == []:
            return gb.invalid_move # perhaps a specifc "no more moves" instead?
        return moves[random.randint(0,len(moves)-1)]

class minimax_agent(agent):
    def __init__(self):
        agent.__init__(self) # super constructor

    def restart_agent(self):
        agent.restart_agent(self)

    def decision(self, gb, pla):

        ## first apply "common sense", namely, if one of the possible moves in current position leads to victory, then take it. (because otherwise by doing the tree thing, you assume your opponent is perfect like you (so it might be a good idea to assume the opponent is stupid sometimes))
        ## Also, terminal_state() doesn't catch this I think because it assumes perfect play (for both opponents)
        moves = gb.get_all_legal_moves(pla)
        for move in moves:
            new_gb = gb.deepcopy()
            new_gb.move_stones(move)
            if self.heuristic(new_gb,pla) == float('Inf'): # ie. is winning state
                return move

        self.explore_count = 0

        begin_time = time.time()
        de = self.minimax_decision(gb, pla)
        end_time = time.time()

        self.explore_count_history.append(self.explore_count)
        self.explore_depth_history.append(self.explore_depth)
        self.decision_time_history.append(end_time -begin_time) # does not include 'common sense' because we are measuring the time taken for the particular search technique

        for his in self.history:
            if his[0] == de and his[1] == gb: # will skip over this line on first run
                return moves[random.randint(0,len(moves)-1)] # cause random perturbation to force full reevaluation later

        if len(self.history) >= self.max_history: # '>' should be an error
            self.history.popleft()
        self.history.append((de,gb))
        return de

    def minimax_decision(self, gb, pla):
        self.explore_depth = 2
        ret_val,ret_move = self.minimax(gb, self.explore_depth, pla, "max")
        return ret_move

    def minimax(self, gb, depth, pla, mm):
        """gb is a particular game state, mm is either max or min"""
        if self.terminal_state(gb,pla) or \
           depth == 0:
            return (self.heuristic(gb,pla),gb.invalid_move)

        if mm == "max":
            curr_val = float('-Inf')
        else: # mm is min
            curr_val = float('Inf')

        curr_move = gb.invalid_move
        moves = gb.get_all_legal_moves(pla)
        for move in moves:
            new_gb = gb.deepcopy()
            new_gb.move_stones(move)
            self.explore_count += 1

            ret_val,ret_move = self.minimax(new_gb,\
                                            depth -1,\
                                            self.get_opponent(pla),\
                                            "max" if mm == "min" else "min") # only root wants ret_move
            if mm == "max":
                if ret_val > curr_val:
                    curr_move = move
                curr_val = max(curr_val,ret_val)
            else:
                if ret_val < curr_val:
                    curr_move = move
                curr_val = min(curr_val,ret_val)
        return (curr_val,curr_move)

class alphabeta_agent(agent):
    def __init__(self):
        agent.__init__(self) # super constructor
        self.__init_values()

    def __init_values(self):
        self.prune_count = 0
        self.prune_count_history = collections.deque()

    def restart_agent(self):
        agent.restart_agent(self)
        self.__init_values()

    def get_stats(self):
        prune_count_history_list = list(self.prune_count_history)
        stat = agent.get_stats(self)
        stat['mean_prune_count'] = stats.mean(prune_count_history_list[1:])
        stat['var_prune_count'] = stats.var(prune_count_history_list[1:])
        return stat

    def print_stats(self):
        agent.print_stats(self)
        print self.prune_count_history
        print "mean prune count:",stats.mean(list(self.prune_count_history))

    def decision(self, gb, pla):

        ## first apply "common sense", namely, if one of the possible moves in current position leads to victory, then take it. (because otherwise by doing the tree thing, you assume your opponent is perfect like you (so it might be a good idea to assume the opponent is stupid sometimes))
        ## Also, terminal_state() doesn't catch this I think because it assumes perfect play (for both opponents)
        moves = gb.get_all_legal_moves(pla)
        for move in moves:
            new_gb = gb.deepcopy()
            new_gb.move_stones(move)
            if self.heuristic(new_gb,pla) == float('Inf'): # ie. is winning state
                return move

        self.explore_count = 0
        self.prune_count = 0

        begin_time = time.time()
        de = self.alphabeta_decision(gb, pla)
        end_time = time.time()

        self.explore_count_history.append(self.explore_count)
        self.explore_depth_history.append(self.explore_depth)
        self.prune_count_history.append(self.prune_count)
        self.decision_time_history.append(end_time -begin_time) # does not include 'common sense' because we are measuring the time taken for the particular search technique

        for his in self.history:
            if his[0] == de and his[1] == gb: # will skip over this line on first run
                return moves[random.randint(0,len(moves)-1)] # cause random perturbation to force full reevaluation later

        if len(self.history) >= self.max_history: # '>' should be an error
            self.history.popleft()
        self.history.append((de,gb))
        return de

    def alphabeta_decision(self, gb, pla):
        neginf = float('-Inf')
        posinf = float('Inf')
        self.explore_depth = 2
        ret_val,ret_move = self.alphabeta(gb, neginf, posinf, self.explore_depth, pla, "max")
        return ret_move

    def alphabeta(self, gb, alpha, beta, depth, pla, mm):
        if self.terminal_state(gb,pla) or \
           depth == 0:
            return (self.heuristic(gb,pla),gb.invalid_move)

        curr_move = gb.invalid_move
        moves = gb.get_all_legal_moves(pla)
        for move in moves:
            new_gb = gb.deepcopy()
            new_gb.move_stones(move)
            self.explore_count += 1

            ret_val,ret_move = self.alphabeta(new_gb,\
                                              alpha,\
                                              beta,\
                                              depth -1,\
                                              self.get_opponent(pla),\
                                              "max" if mm == "min" else "min")
            if mm == "max":
                if ret_val > alpha: # '>=' causes wrong move to be selected
                    curr_move = move
                alpha = max(alpha,ret_val)
                if alpha >= beta: # value of adversery has now been exceeded, so no need to search further
                    self.prune_count += len(moves) -moves.index(move)
                    return (beta,curr_move) # pruning
#                alpha = max(alpha,ret_val)

            else: # is "min"
                if ret_val < beta: # '<=' causes wrong move to be selected
                    curr_move = move
                beta = min(beta,ret_val)
                if beta <= alpha:
                    self.prune_count += len(moves) -moves.index(move)
                    return (alpha,curr_move) # pruning
#                beta = min(beta,ret_val)

        if mm == "max":
            return (alpha,curr_move)
        else: # is "min"
            return (beta,curr_move)

class arena:
    def __init__(self, black, white):
        self.gb = game_board()
        self.black_agent = black
        self.white_agent = white
        self.stat_history = collections.deque()

    def update_board(self, move):
        self.gb.move_stones(move)

    def begin_games(self, n):
        for i in range(0,n):
            self.black_agent.restart_agent()
            self.white_agent.restart_agent()
            self.gb = game_board()
            self.__begin_game()
        total = {}
        for stat in self.stat_history:
            for key in stat.keys():
                if key not in total:
                    total[key] = stat[key]
                else:
                    total[key] += stat[key]

        for key in total.keys(): ## now average it
            total[key] = total[key]/float(n)
        print total

    def __begin_game(self):
        stat = self.play()
        self.stat_history.append(stat)

    def play(self):
        print "Game start: "
        print self.gb
        while 1:

            ## black move
            move = self.black_agent.decision(self.gb,player.black)
            if move == self.gb.invalid_move:
                print "White wins!"
                return self.white_agent.get_stats()

            self.update_board(move)
            print self.gb

            ## white move
            move = self.white_agent.decision(self.gb,player.white)
            if move == self.gb.invalid_move:
                print "Black wins!"
                return self.black_agent.get_stats()

            self.update_board(move)
            print self.gb



"""
gb = None
new_gb = None

# gb = game_board()
# new_gb = copy.deepcopy(gb)
# print gb
# print new_gb

gb = game_board()
new_gb = gb.deepcopy()
print gb
print new_gb

gb.set_cell((2,3),game_cell(5,player.black))
print gb
print new_gb




gb = game_board()
gb.move_stones(game_move((1,4),wind.east))
mma = minimax_agent()
move = mma.minimax_decision(gb, player.black)

gb = game_board()
gb.move_stones(game_move((1,4),wind.east))
aba = alphabeta_agent()
move = aba.alphabeta_decision(gb, player.black)

## minimax_agent has no more legal moves, and it's its turn
gb = game_board()
gb.set_cell((4,1),game_cell(0,player.none))
gb.set_cell((1,3),game_cell(3,player.white))
gb.set_cell((2,3),game_cell(3,player.white))
gb.set_cell((2,4),game_cell(4,player.white))
mma = minimax_agent()
move = mma.minimax_decision(gb, player.black) # black has no more legal moves

## playing the game
ra = random_agent()
mma = minimax_agent()
aba = alphabeta_agent()
#ar = arena(mma,ra)
ar = arena(aba,ra)
ar.begin_games(1)


begin_time = time.time()
ar.begin_games(2)
end_time = time.time()
print 'Time elapsed:',end_time -begin_time,'s'


gb = game_board()
gb.move_stones(game_move((1,4),wind.east))
gb.span_tree_count((2,4))
gb.span_trees_count(player.black)

gb = game_board()
gb.span_tree_count((4,1))





## playing the game
aba = alphabeta_agent()
gb = game_board()
gb.set_cell((4,1),game_cell(0,player.none))
gb.set_cell((1,3),game_cell(1,player.white))
gb.set_cell((2,3),game_cell(1,player.white))
gb.set_cell((3,3),game_cell(1,player.white))
aba.heuristic(gb,player.white)

gb.set_cell((2,4),game_cell(1,player.white))
aba.heuristic(gb,player.white)

gb.set_cell((2,4),game_cell(0,player.none))
gb.move_stones(game_move((1,4),wind.east))
aba.heuristic(gb,player.white)




for i in range(5,100):
    if i == 75:
        print range(5,100)[i]
        break

"""

if __name__ == '__main__':
    gb = game_board()
    gb.move_stones(game_move((1,4),wind.east))
    mma = minimax_agent()
    move = mma.minimax_decision(gb, player.black)
