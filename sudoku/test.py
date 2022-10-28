from typing import Literal
import unittest
import src.SudokuEngine as se
from time import process_time as cpu_t

def repeat(times):
    def repeatHelper(f):
        def callHelper(*args):
            for i in range(0, times):
                f(*args)

        return callHelper

    return repeatHelper

def validSudoku(grid: list[list[int]]):
    no_errors = True
    row = []
    col = []
    box = []
    def error(group_i, digit: int, collision: tuple[int, int], col_type: str):
        print(f"{digit} collides in {group_i} {col_type} indexes {collision[0]} and {collision[1]}")

    for g in range(9):
        row.clear()
        col.clear()
        box.clear()
        for i in range(9):
            r_dig = grid[g][i]
            c_dig = grid[i][g]
            b_dig = grid[g//3*3 + i//3][g*3%9 + i%3]
            if r_dig in row:
                error(g, r_dig, (i, row.index(r_dig)), 'row')
                no_errors = False
            row.append(r_dig)
            if c_dig in col:
                error(g, c_dig, (i, col.index(c_dig)), 'col')
                no_errors = False
            col.append(c_dig)
            if b_dig in box:
                error(g, b_dig, (i, box.index(b_dig)), 'box')
                no_errors = False
            box.append(b_dig)

    if not no_errors:
        se.printGrid(grid)
        
    return no_errors

class SudokuTest(unittest.TestCase):
    g_n = 10
    tot_g_t = 0
    min_g_t = 10**100
    max_g_t = 0
    @repeat(100)
    def test_genSolved(self):
        grid = se.genSolvedSudoku()
        self.assertTrue(validSudoku(grid))
    @repeat(100)
    def test_converting(self):
        grid = se.genSolvedSudoku()
        s_grid = se.gridToStr(grid)
        grid_from_str = se.strToGrid(s_grid)
        self.assertEqual(grid, se.strToGrid(s_grid))
        self.assertEqual(s_grid, se.gridToStr(grid_from_str))
    @repeat(100)
    def test_solving(self):
        grid = se.genSolvedSudoku()
        grid = se.deleteRandom(grid, 50)
        solutions = se.countSolutions(grid, output=False)
        for s in solutions:
            self.assertTrue(validSudoku(se.strToGrid(s)))
    @repeat(g_n)
    def test_gen(self):
        b_t = cpu_t()
        grd = se.genSudoku()
        t = cpu_t() - b_t
        self.tot_g_t += t
        self.max_g_t = max(self.max_g_t, t)
        self.min_g_t = min(self.min_g_t, t)
        self.assertTrue(se.singleSolution(grd))
    def test_main(self):
        return
        n = 100
        for i in range(n):
            grd = se.genSolvedSudoku()
            grd = se.deleteRandom(grd, 50)
            sols = se.countSolutions(grd)
            sols_ = se.countSolutions(grd)
            if len(sols_) != len(sols):
                print()
                print('*'*10)
                se.printGrid(grd, True)
                print('*'*10)
            self.assertEqual(len(sols_), len(sols))

def run():
    unittest.main()

if __name__ == '__main__':
    unittest.main()
    print(
        "avrg gen_time:{}s min:{}s max:{}s".format(
            round(SudokuTest.tot_g_t/SudokuTest.g_n, 3),
            round(SudokuTest.min_g_t, 3),
            round(SudokuTest.max_g_t, 3)
        )
        )
    #for _ in range(1000):
    #    grd = se.genSolvedSudoku()
    #    grd = se.deleteRandom(grd, 0.02)
    #    sols = se.checkNumberOfSolutions(grd)
    #   sols_ = se.checkNumberOfSolutions_(grd)