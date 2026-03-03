from typing import TypeAlias, Literal, List, Tuple
from enum import Enum

Player: TypeAlias = Literal[-1, 1]
Board : TypeAlias = List[List[Player|None]]

# use node to link instead
class ConnectNWinChecker():
    def __init__(self, N:int, M:int, X:int):
        self.num_row = N
        self.num_col = M
        self.win_score = X

    @staticmethod
    def next_cell(cell:Tuple[int], offset:Tuple[int]):
        return [cell[0] + offset[0], cell[1] + offset[1]]

    def is_in_grid(self, cell:Tuple[int]):
        return (cell[0] >= 0 and
                cell[0] < self.num_row and 
                cell[1] >= 0 and
                cell[1] < self.num_col)
                
    def count_diagonal(self, last_played_cell:Tuple[int], offset1:Tuple[int], offset2:Tuple[int]):
        count = 1
        
        cell = last_played_cell
        while self.is_in_grid(self.next_cell(cell, [offset1[0], offset1[1]])):
            count += 1
            cell = self.next_cell(cell, [offset1[0], offset1[1]])
        
        cell = last_played_cell  
        while self.is_in_grid(self.next_cell(cell, [offset2[0], offset2[1]])):
            count += 1
            cell = self.next_cell(cell, [offset2[0], offset2[1]])
            
        return count

    def is_horizontal_win(self, board:Board, player:Player, last_played_cell:Tuple[int]):
        score = 0
        for cell in board[last_played_cell[0]]:
            if cell == player:
                score += 1
                if score >= self.win_score:
                    return True
            else:
                score = 0
        return False
        
    def is_vertical_win(self, board:Board, player:Player, last_played_cell:Tuple[int]):
        score = 0
        for row in range(0, self.num_row):
            if board[row][last_played_cell[1]] == player:
                
                score += 1
                if score >= self.win_score:
                    return True
            else:
                score = 0
        return False
        
    def is_diagonal_win(self, 
                    board: Board, player: Player,
                    last_played_cell: Tuple[int, int],
                    offset1: Tuple[int, int],
                    offset2: Tuple[int, int]) -> bool:

        diag_length = self.count_diagonal(last_played_cell, offset1, offset2)

        if diag_length < self.win_score:
            return False

        # Move to the start of diagonal
        cell = last_played_cell
        while self.is_in_grid(self.next_cell(cell, offset1)):
            cell = self.next_cell(cell, offset1)

        score = 0
        for _ in range(diag_length):
            if board[cell[0]][cell[1]] == player:
                score += 1
                if score >= self.win_score:
                    return True
            else:
                score = 0

            cell = self.next_cell(cell, offset2)

        return False
            
    def is_win(self, board:Board, player:bool, last_played_cell:Tuple[int]) -> bool:
        player:Player = 1 if player else -1
        if self.is_horizontal_win(board, player, last_played_cell):
            return True
        if self.is_vertical_win(board, player, last_played_cell):
            return True
        #Descending diagonal  
        if self.is_diagonal_win(board, player, last_played_cell, (-1, -1), (1, 1)):
            return True
        #Ascending diagonal
        else:
            return self.is_diagonal_win(board, player, last_played_cell, (-1, 1), (1, -1))
        

# check by last player play
# if __name__ =="__main__":
#     board = [[None] * 3]*2
#     print(board)