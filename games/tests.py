import unittest
from proj2 import *
#import pdb

class TestGameCell(unittest.TestCase):

    def setUp(self):
        self.cell1 = game_cell(10,player.black)
        self.cell2 = game_cell(0,player.black)
        self.cell3 = game_cell(10,player.white)
        self.cell4 = game_cell(0,player.white)
        self.cell5 = game_cell(0)

    def test_equality(self):
        self.assertEquals(self.cell1,self.cell1)
        self.assertNotEqual(self.cell1,self.cell2)

    def test_is_empty(self):
        self.assertTrue(self.cell5.is_empty())
        self.assertFalse(self.cell1.is_empty())

class TestGameBoard_Accessors(unittest.TestCase):

    def setUp(self):
        self.gb_blank = game_board()

        self.gb = game_board()
        self.cell1 = game_cell(10,player.black)
#
        self.gb.set_cell((1,3),game_cell(13,player.black))
        self.gb.set_cell((1,2),game_cell(12,player.black))
        self.gb.set_cell((1,1),game_cell(11,player.black))
#
        self.gb.set_cell((2,4),game_cell(23,player.white))
        self.gb.set_cell((2,3),game_cell(23,player.white))
        self.gb.set_cell((2,2),game_cell(22,player.white))
        self.gb.set_cell((2,1),game_cell(21,player.white))
#
        self.gb.set_cell((3,4),game_cell(34,player.black))
        self.gb.set_cell((3,3),game_cell(33,player.black))
        self.gb.set_cell((3,2),game_cell(32,player.black))
        self.gb.set_cell((3,1),game_cell(31,player.black))
#
        self.gb.set_cell((4,4),game_cell(44,player.white))
        self.gb.set_cell((4,3),game_cell(43,player.white))
        self.gb.set_cell((4,2),game_cell(42,player.white))

    def test_init(self):
        self.assertEqual(self.gb.grid[0,0],self.cell1)

    def test_get_cell(self):
        self.assertEqual(self.gb.get_cell((3,4)),game_cell(34,player.black))
        self.assertEqual(self.gb.get_cell((5,5)),self.gb.nowhere_cell)

    def test_is_legal_move(self):
        self.assertTrue(self.gb.is_legal_move(game_move((2,2),wind.north)))
        self.assertFalse(self.gb.is_legal_move(game_move((2,4),wind.north))) # goes off board
        self.assertFalse(self.gb.is_legal_move(game_move((2,4),wind.east))) # blocked by opponent
        self.assertFalse(self.gb_blank.is_legal_move(game_move((2,2),wind.west)))

    def test_get_next_cell(self):
        self.assertEqual(self.gb.get_next_cell((1,1),wind.ne),game_cell(22,player.white))
        self.assertEqual(self.gb.get_next_cell((1,1),wind.sw),self.gb.nowhere_cell)
        self.assertNotEqual(self.gb.get_next_cell((1,1),wind.north),game_cell(44,player.white))

    def test_get_next_coord(self):
        self.assertEqual(self.gb.get_next_coord((2,2),wind.north),(2,3))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.ne),(3,3))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.east),(3,2))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.se),(3,1))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.south),(2,1))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.sw),(1,1))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.west),(1,2))
        self.assertEqual(self.gb.get_next_coord((2,2),wind.nw),(1,3))

        self.assertEqual(self.gb.get_next_coord((1,1),wind.south),self.gb.nowhere_coord)

    def test_coord_to_index(self):
        self.assertEqual(self.gb.coord_to_index((1,1)),(3,0))
        self.assertEqual(self.gb.coord_to_index((3,2)),(2,2))

    def test_get_cell_line(self):
## n
        self.assertEqual(self.gb.get_cell_line((1,1),wind.north),\
                         [game_cell(11,player.black),game_cell(12,player.black),\
                          game_cell(13,player.black),game_cell(10,player.black)])
        self.assertNotEqual(self.gb.get_cell_line((1,1),wind.north),\
                            [game_cell(10,player.black),game_cell(12,player.black),\
                             game_cell(13,player.black),game_cell(10,player.black)])
## ne
        self.assertEqual(self.gb.get_cell_line((1,1),wind.ne),\
                         [game_cell(11,player.black),game_cell(22,player.white),\
                          game_cell(33,player.black),game_cell(44,player.white)])
## east
        self.assertEqual(self.gb.get_cell_line((3,3),wind.east),\
                         [game_cell(33,player.black),game_cell(43,player.white)])
## ...
## west
        self.assertEqual(self.gb.get_cell_line((1,4),wind.west),\
                         [game_cell(10,player.black)])

class TestGameBoard_Movement(unittest.TestCase):

    def setUp(self):
        self.gb = game_board()
        self.gb_man = game_board()
#        print self.gb # differs from
#        print self.gb.grid

    def test_get_legal_move(self):
        self.assertEqual(self.gb.get_legal_move(game_move((1,4),wind.east)),game_move((1,4),wind.east))
        self.assertEqual(self.gb.get_legal_move(game_move((1,4),wind.north)),self.gb.invalid_move)
        self.assertEqual(self.gb.get_legal_move(game_move((2,2),wind.sw)),self.gb.invalid_move)

    def test_get_legal_moves(self):
        self.assertEqual(self.gb.get_legal_moves((1,4)),\
                         [game_move((1,4),wind.east),\
                          game_move((1,4),wind.se),\
                          game_move((1,4),wind.south)])
        self.assertNotEqual(self.gb.get_legal_moves((1,4)),\
                            [game_move((1,4),wind.east),\
                             game_move((1,4),wind.se),\
                             game_move((1,4),wind.sw)])
        self.assertEqual(self.gb.get_legal_moves((2,2)),[])

    def test_get_all_legal_moves(self):
        self.assertEqual(self.gb.get_all_legal_moves(player.black),\
                         [game_move((1,4),wind.east),\
                          game_move((1,4),wind.se),\
                          game_move((1,4),wind.south)])
        self.assertEqual(self.gb.get_all_legal_moves(player.white),\
                         [game_move((4,1),wind.north),\
                          game_move((4,1),wind.west),\
                          game_move((4,1),wind.nw)])
        self.assertNotEqual(self.gb.get_all_legal_moves(player.black),\
                            [game_move((4,1),wind.north),\
                             game_move((4,1),wind.west),\
                             game_move((4,1),wind.nw)])

        self.gb.move_stones(game_move((1,4),wind.east))
        self.assertEqual(self.gb.get_all_legal_moves(player.black),\
                         [game_move((2,4),wind.east),\
                          game_move((2,4),wind.se),\
                          game_move((2,4),wind.south),\
                          game_move((2,4),wind.sw),\
                          game_move((2,4),wind.west),\
#
                          game_move((3,4),wind.east),\
                          game_move((3,4),wind.se),\
                          game_move((3,4),wind.south),\
                          game_move((3,4),wind.sw),\
                          game_move((3,4),wind.west),\
#
                          game_move((4,4),wind.south),\
                          game_move((4,4),wind.sw),\
                          game_move((4,4),wind.west)])

    def test_move_stones(self):
        ## I think I should test what happens when coordinate picked without stones
#        print self.gb

        self.gb.move_stones(game_move((1,4),wind.east))
        self.gb_man.set_cell((1,4),game_cell(0,player.none))
        self.gb_man.set_cell((2,4),game_cell(1,player.black))
        self.gb_man.set_cell((3,4),game_cell(2,player.black))
        self.gb_man.set_cell((4,4),game_cell(7,player.black))
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

        self.gb.move_stones(game_move((4,1),wind.north))
        self.gb_man.set_cell((4,1),game_cell(0,player.none))
        self.gb_man.set_cell((4,2),game_cell(1,player.white))
        self.gb_man.set_cell((4,3),game_cell(9,player.white))
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

        self.gb.move_stones(game_move((4,4),wind.sw))
        self.gb_man.set_cell((4,4),game_cell(0,player.none))
        self.gb_man.set_cell((3,3),game_cell(1,player.black))
        self.gb_man.set_cell((2,2),game_cell(2,player.black))
        self.gb_man.set_cell((1,1),game_cell(4,player.black))
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

        self.gb.move_stones(game_move((4,3),wind.west)) # this is no drop move (so don't count it?)
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

        self.gb.move_stones(game_move((4,3),wind.south))
        self.gb_man.set_cell((4,3),game_cell(0,player.none))
        self.gb_man.set_cell((4,2),game_cell(2,player.white))
        self.gb_man.set_cell((4,1),game_cell(8,player.white))
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

        self.gb.move_stones(game_move((3,3),wind.south))
        self.gb_man.set_cell((3,3),game_cell(0,player.none))
        self.gb_man.set_cell((3,2),game_cell(1,player.black))
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

        self.gb.move_stones(game_move((4,1),wind.west))
        self.gb_man.set_cell((4,1),game_cell(0,player.none))
        self.gb_man.set_cell((3,1),game_cell(1,player.white))
        self.gb_man.set_cell((2,1),game_cell(7,player.white))
        self.assertEqual(self.gb,self.gb_man)
#        print self.gb

class TestGameBoard_SpanningTree(unittest.TestCase):

    def setUp(self):
        self.gb = game_board()

    def test_span_tree_count(self):
        self.assertEqual(15,self.gb.span_tree_count((1,4)))
        self.gb.move_stones(game_move((1,4),wind.east))
        self.assertEqual(15,self.gb.span_tree_count((2,4)))
        self.assertEqual(45,self.gb.span_trees_count(player.black))
        self.assertEqual(13,self.gb.span_trees_count(player.white))
        self.gb.move_stones(game_move((4,1),wind.nw))
        self.assertEqual(39,self.gb.span_trees_count(player.white))

if __name__ == '__main__':
    unittest.main()
