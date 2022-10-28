#import pygame
from asyncore import loop
from time import time
from typing import Literal
from ipywidgets import Output
from random import choice, sample, shuffle

from src.StateGrid import StateGrid

#pygame.font.init()
#screen = pygame.display.set_mode((500, 600))

x = 0
y = 0
dif = 500 / 9
val = 0
#font1 = pygame.font.SysFont("comicsans", int(40))
#font2 = pygame.font.SysFont("comicsans", int(40 / 3))

bg_color = (255, 255, 255)
done_color = (0, 0, 0)
done_bg_color = (0, 153, 153)
selected_color = (0, 0, 200)
option_color = (100, 100, 100)
frame_color = (0, 0, 0)

"""def cubicPath():
    path = list()
    for cube_row in range(0, 9, 3):
        for cube_col in range(0, 9, 3):
            for row in range(cube_row, cube_row + 3):
                for col in range(cube_col, cube_col + 3):
                    path.append(row * 9 + col)
    return path"""
#
#   UTILITIES
#
def printGrid(grid: list[list[int]], inline=False, msg='', clue_amt=False):
    if msg:
        print(f"{msg}", end='')
    if clue_amt:
        amount = 0
        for i in range(81):
            if grid[i//9][i%9] != 0:
                amount += 1
        print(f"[{amount}]", end='\t')
    for r in range(9):
        for i in range(3):
            for j in range(0 + i*3, 3 + i*3):
                print(f"{grid[r][j]}", end= '' if inline else ' ')
            if not inline:
                print('  ', end='')
        if not inline:
            print()
        if not inline and (r + 1) % 3 == 0:
            print()
    print()
    if clue_amt: return amount

def gridToStr(grid: list[list[int]]) -> str:
    return ''.join([str(grid[idx//9][idx%9]) for idx in range(81)])

def strToGrid(sudoku_str: str) -> list[list[int]]:
    grid = [[0] * 9 for _ in range(9)]
    if not type(sudoku_str) is str:
        raise ValueError
    for i in range(len(sudoku_str)):
        grid[i//9][i%9] = int(sudoku_str[i])
    return grid

def mergeGridWithSolution(grid: list[list[int]], solution: list[int], indexes: list[int]):
    new_grid = [[grid[r][c] for c in range(9)] for r in range(9)]
    for i in range(len(indexes)):
        new_grid[indexes[i]//9][indexes[i]%9] = solution[i]
    return new_grid
#
#   DRAW
#
def __draw_(func, grid, candidates, indexes, idx):
    draw_grid = [[0]*9 for _ in range(9)]
    c_i = 0
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0 and candidates and indexes:
                draw_grid[i][j] = (indexes[c_i], candidates[c_i])
                c_i += 1
            else:
                draw_grid[i][j] = grid[i][j]
    func(draw_grid, idx)
#
#   SOLVE SUDOKU
#
def fillIndexes(grid: list[list[int]], unsolved_grid_idnexes, cell_next_indexes):
    for idx in range(81):
        if grid[idx//9][idx%9] == 0:
            unsolved_grid_idnexes.append(idx)
            cell_next_indexes.append(0)

def backTrack(grid: list[list[int]], solution_limit, shuffle_guesses=False, draw_func=None, output=False) -> list[list[list[int]]]:
    if output:
        print(f" v2:\t{gridToStr(grid)}")

    state_grid = StateGrid(grid)
    unsolved_grid_idnexes = []
    cell_next_indexes = []
    fillIndexes(grid, unsolved_grid_idnexes, cell_next_indexes)
    solutions = []
    possible_guesses = state_grid.getFilteredCandidatesList(unsolved_grid_idnexes)
    if shuffle_guesses:
        for x in range(len(possible_guesses)):
            shuffle(possible_guesses[x])

    if len(cell_next_indexes) == 0:
        return []

    i = 0
    loop_count = 0
    going_back = False
    while i >= 0:
        loop_count += 1
        if going_back:
            state_grid.rmDigit(unsolved_grid_idnexes[i], possible_guesses[i][cell_next_indexes[i]])
            if cell_next_indexes[i] == len(possible_guesses[i]) - 1:
                cell_next_indexes[i] = 0
                i -= 1
                continue
            else:
                cell_next_indexes[i] += 1
                going_back = False

        ##### funky stuff
        if draw_func:
            __draw_(draw_func, grid, possible_guesses, cell_next_indexes, unsolved_grid_idnexes[i])
        ##### end of the funk

        if state_grid.isAValidMove(unsolved_grid_idnexes[i], possible_guesses[i][cell_next_indexes[i]]):
            state_grid.addDigit(unsolved_grid_idnexes[i], possible_guesses[i][cell_next_indexes[i]])
            if i == len(unsolved_grid_idnexes) - 1:
                solution = [possible_guesses[j][cell_next_indexes[j]] for j in range(len(possible_guesses))]
                solution = mergeGridWithSolution(grid, solution, unsolved_grid_idnexes)
                solutions.append(solution)
                if solution_limit > 0 and len(solutions) == solution_limit:
                    if output:
                        print(f"Exceeded {solution_limit} solution limit. Counting stopped")
                    return solutions
                if output:
                    print(f"#{len(solutions)}\t{gridToStr(solutions[-1])}")
                going_back = True
            else:
                i += 1
        else:
            cell_next_indexes[i] += 1
            if cell_next_indexes[i] == len(possible_guesses[i]):
                going_back = True
                cell_next_indexes[i] = 0
                i -= 1

    if output:
        print(f"{loop_count} loops")
    return solutions

def countSolutions(grid: list[list[int]], solution_limit=100, draw_func=None, output=False) -> list[str]:
    solutions = backTrack(
        grid, 
        solution_limit, 
        shuffle_guesses=False, 
        draw_func=draw_func, 
        output=output
        )
    return [gridToStr(s) for s in solutions]

def genSolvedSudoku(draw_func=None, output=False) -> list[list[int]]:
    solutions = backTrack(
        [[0]*9 for _ in range(9)], 
        1,
        shuffle_guesses=True, 
        draw_func=draw_func, 
        output=output
        )
    return solutions[0]

def singleSolution(grid: list[list[int]], draw_func=None, output=False):
    solutions = backTrack(
        grid, 
        2,
        shuffle_guesses=True, 
        draw_func=draw_func, 
        output=output
        )
    return len(solutions) == 1

def genSudoku(clues=17, draw_func=None, do_draw: list[Literal['all', 'gen', 'del', 'solve']] = ['all'], output=False) -> list[list[int]]:
    if clues < 17:
        raise ValueError("Impossible clue amount")
    if do_draw == 'all' or 'all' in do_draw:
        do_draw = ['gen', 'del', 'solve']
    do_draw = {
        'gen': draw_func if 'gen' in do_draw else None,
        'del': draw_func if 'del' in do_draw else None,
        'solve': draw_func if 'solve' in do_draw else None
    }
    removes_left = 81 - clues
    solved_grid = genSolvedSudoku(draw_func=do_draw['gen'], output=output)

    indexes_order = list(range(81))
    shuffle(indexes_order)

    removed_digit = None
    for idx in indexes_order:
        removed_digit = solved_grid[idx//9][idx%9]
        solved_grid[idx//9][idx%9] = 0
        if not singleSolution(solved_grid, draw_func=do_draw['del'], output=output):
            solved_grid[idx//9][idx%9] = removed_digit
        else:
            removes_left -= 1
            if removes_left == 0:
                break
        idx += 1
    return solved_grid

def deleteRandom(grid, amount=17, draw_func=None):
    res_grid = [[grid[i][j] for j in range(9)] for i in range(9)]
    deleted_i = sample(range(81), (81-amount))
    for i in deleted_i:
        if draw_func:
            __draw_(draw_func, res_grid, [], [], i)
        res_grid[i//9][i%9] = 0
    return res_grid

"""
628513497954267183173498652749152836382976514516834279267385941495721368831649725
628513497954267183173498652749152836382976514516834279267385941495721368831649725

5 0 0   1 0 0   0 6 0   
0 4 9   0 5 0   0 0 0   
0 3 0   0 0 0   8 0 0   

7 0 8   9 0 3   2 5 6   
9 0 0   0 0 5   0 0 0   
0 0 4   2 0 0   0 0 7   

0 0 2   0 0 0   7 8 0   
0 0 0   3 0 0   0 1 0   
0 0 0   0 0 8   0 0 4 
"""