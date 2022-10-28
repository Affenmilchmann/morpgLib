# list of accociations index -> [row_idx, column_idx, box_idx]
precomputed_locations = [[i//9, i%9, 3*(i//9//3)+(i%9//3)] for i in range(81)]

class StateGrid():
    def __init__(self, grid: list[list[int]]):
        # states: 
        # 0 - free to use
        # 1 - occupied
        # 2 - occupied and cannot be altered
        self.rows = [[0]*9 for _ in range(9)]
        self.columns = [[0]*9 for _ in range(9)]
        self.boxes = [[0]*9 for _ in range(9)]

        for i in range(81):
            if grid[i//9][i%9]:
                self.addConstantDigit(i, grid[i//9][i%9])

    def __addDigit(self, idx: int, digit: int, val: int):
        if not self.isAValidMove(idx, digit):
            raise ValueError("Not a valid move!")
        row_i, col_i, box_i = precomputed_locations[idx]
        self.rows[row_i][digit-1] = val
        self.columns[col_i][digit-1] = val
        self.boxes[box_i][digit-1] = val

    def addConstantDigit(self, idx: int, digit: int):
        self.__addDigit(idx, digit, 2)

    def addDigit(self, idx: int, digit: int):
        self.__addDigit(idx, digit, 1)

    def rmDigit(self, idx: int, digit: int):
        row_i, col_i, box_i = precomputed_locations[idx]
        self.rows[row_i][digit-1] = 2 if self.rows[row_i][digit-1] == 2 else 0
        self.columns[col_i][digit-1] = 2 if self.columns[col_i][digit-1] == 2 else 0
        self.boxes[box_i][digit-1] = 2 if self.boxes[box_i][digit-1] == 2 else 0

    def getFilteredCandidatesList(self, filter: list[int]) -> list[list[int]]:
        out_list = []
        for idx in range(81):
            if not idx in filter:
                continue
            row_i, col_i, box_i = precomputed_locations[idx]
            result_arr = []
            for i in range(9):
                if int(bool(self.rows[row_i][i])) + int(bool(self.columns[col_i][i])) + int(bool(self.boxes[box_i][i])) == 0:
                    result_arr.append(i+1)
            out_list.append(result_arr)
        return out_list

    def getCandidates(self, filter:list[int]):
        grid = [[0]*9 for _ in range(9)]
        for idx in range(81):
            if not idx in filter:
                continue
            row_i, col_i, box_i = precomputed_locations[idx]
            result_arr = []
            for i in range(9):
                if int(bool(self.rows[row_i][i])) + int(bool(self.columns[col_i][i])) + int(bool(self.boxes[box_i][i])) == 0:
                    result_arr.append(i+1)
            grid[idx//9][idx%9] = result_arr
        return grid

    def isAValidMove(self, idx: int, digit: int) -> bool:
        row_i, col_i, box_i = precomputed_locations[idx]
        return not (self.rows[row_i][digit-1] or self.columns[col_i][digit-1] or self.boxes[box_i][digit-1])
