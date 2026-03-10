#####
#
# Name: Kwankhao Tangprasert
# Student ID: 653040165-6
#
#####
from typing import TypeAlias, Literal, List, Tuple
from abc import ABC, abstractmethod
import copy
import time

Player: TypeAlias = Literal[-1, 1]
Board : TypeAlias = List[List[Player|None]]

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
        
class Base(ABC):
    def __init__(self, checker:ConnectNWinChecker):
        pass
        self.checker = checker
        self.tie_state = [self.checker.num_row]*self.checker.num_col
        

    def list_valid_move(self, count_list:List[int])->List[int]:
        valid_actions = []
        for i, count in enumerate(count_list):
            if count < self.checker.num_row:
                valid_actions.append(i)
        # prefer center position due to it can control the board leading to better order and make alpha-beta pruning more efficient
        valid_actions.sort(key=lambda c: abs(c - self.checker.num_col // 2))
        return valid_actions
    
    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def get_best_move(self):
        pass


class MinimaxV2(Base):
    def __init__(self, checker:ConnectNWinChecker, time_limit:float)->None:
        super().__init__(checker)
        self.time_limit = time_limit*0.95 # cubic weights instead of exponential
        self.start_time = None

        self.weights = [0] + [k**3 for k in range(1, self.checker.win_score+1)]

        self.WIN_SCORE = self.weights[self.checker.win_score] * 10  # priotize the most

    def set_start_time(self):
        self.start_time = time.time()

    def heuristic_blocking(self, board:Board)->int:
        score = 0

        def evaluate_window(window):
            nonlocal score
            
            x_count = window.count(1)
            o_count = window.count(-1)
            empty = window.count(0)
            
            # Blocked window
            if x_count > 0 and o_count > 0:
                return
            
            # Win detection
            if x_count == self.checker.win_score:
                score += self.WIN_SCORE
                return
            elif o_count == self.checker.win_score:
                score -= self.WIN_SCORE
                return
            
            elif x_count == self.checker.win_score-1 and empty == 1:
                score += self.weights[x_count]

            elif o_count == self.checker.win_score-1 and empty == 1:
                score -= self.weights[o_count] * 1.2
            
            elif x_count == self.checker.win_score-2 and empty == 2:
                score += self.weights[x_count]

            elif o_count == self.checker.win_score-2 and empty == 2:
                score -= self.weights[o_count] * 1.1

            elif x_count > 0:
                score += self.weights[x_count]
            elif o_count > 0:
                score -= self.weights[o_count]

        # Center Biased
        # center_col = self.checker.num_col // 2

        # for r in range(self.checker.num_row):
        #     for c in range(self.checker.num_col):
        #         if board[r][c] == 1:
        #             score += (self.checker.num_col - abs(c - center_col))
        #         elif board[r][c] == -1:
        #             score -= (self.checker.num_col - abs(c - center_col)) * 1.1

        # Horizontal
        for r in range(self.checker.num_row):
            for c in range(self.checker.num_col - self.checker.win_score + 1):
                window = [board[r][c+i] for i in range(self.checker.win_score)]
                evaluate_window(window)

        #  Vertical 
        for c in range(self.checker.num_col):
            for r in range(self.checker.num_row - self.checker.win_score + 1):
                window = [board[r+i][c] for i in range(self.checker.win_score)]
                evaluate_window(window)

        #  Diagonal  Ascendant
        for r in range(self.checker.num_row - self.checker.win_score + 1):
            for c in range(self.checker.num_col - self.checker.win_score + 1):
                window = [board[r+i][c+i] for i in range(self.checker.win_score)]
                evaluate_window(window)

        # Diagonal Descendant
        for r in range(self.checker.win_score-1, self.checker.num_row):
            for c in range(self.checker.num_col - self.checker.win_score + 1):
                window = [board[r-i][c+i] for i in range(self.checker.win_score)]
                evaluate_window(window)

        return int(score)

    def search(self,
            board:Board, 
            count_list:List[int], 
            last_played_cell:Tuple[int], 
            depth:int, 
            isMaximizingPlayer:bool, 
            alpha:float, 
            beta:float
    ):
        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError
    
        if self.checker.is_win(board, not isMaximizingPlayer, last_played_cell): # because it evaluate N-1 played
            # If it's currently Maximizer's turn and there's a win, Maximizer lost
            reward = self.WIN_SCORE + (depth * 1)

            return -reward if isMaximizingPlayer else reward
        
        elif count_list == self.tie_state:
            return 0
        
        elif depth == 0:
            return self.heuristic_blocking(board)
        
        
        if isMaximizingPlayer:
            best_reward = -float("inf")
            valid_moves = self.list_valid_move(count_list)
            for col in valid_moves:
                row = self.checker.num_row - count_list[col] - 1
                last_played_cell = (row, col)

                board[row][col] = 1 # max player
                count_list[col] +=1
                reward = self.search(board, count_list, last_played_cell, depth-1, False, alpha, beta)
                count_list[col] -=1
                board[row][col] = 0 # reset for next simu move

                best_reward = max(best_reward, reward)
                alpha = max(alpha, best_reward)
                if alpha >= beta: # Pruning
                    break 
            
            return best_reward
        
            
        else:
            best_reward = float("inf")
            valid_moves = self.list_valid_move(count_list)
            for col in valid_moves:
                row = self.checker.num_row - count_list[col] - 1
                last_played_cell = (row, col)

                board[row][col] = -1 # min player
                count_list[col] +=1
                reward = self.search(board, count_list, last_played_cell, depth-1, True, alpha, beta)
                count_list[col] -=1
                board[row][col] = 0 # reset for next simu move
                
                best_reward = min(best_reward, reward)
                beta = min(beta, best_reward)
                if beta <= alpha: #pruning
                    break

            return best_reward
        
    def get_best_move(self, board:Board, count_list:List[int])->int:

        self.set_start_time()

        best_move = None
        depth = 1

        valid_moves = self.list_valid_move(count_list)

        while True:
            if time.time() - self.start_time > self.time_limit:
                break

            try:

                best_score = -float("inf")
                current_best_move = None

                for move in valid_moves:

                    # time check
                    if time.time() - self.start_time > self.time_limit:
                        raise TimeoutError

                    row = self.checker.num_row - count_list[move] - 1
                    board[row][move] = 1
                    count_list[move] += 1

                    score = self.search(
                        board,
                        count_list,
                        (row, move),
                        depth - 1,
                        False,
                        -float("inf"),
                        float("inf"),
                    )

                    # this process will consequence undo until it back to original value
                    # level 1 -> 0 + 1,  level 2 -> 1 + 1 then hit the base line at level 3
                    # level 2 -> 2 - 1, level 1 -> 1-1  
                    count_list[move] -= 1
                    board[row][move] = 0

                    if score > best_score:
                        best_score = score
                        current_best_move = move
            
            except TimeoutError:
                break

            if time.time() - self.start_time <= self.time_limit:
                best_move = current_best_move
                depth += 1
            else:
                break
        
        return best_move


print("ready")

N,M,F,X,T = input("").strip().split(" ")
N = int(N)
M = int(M)
F = int(F)
T = float(T)
count_list = [0] * M

board = [[0] * M for _ in range(N)]

checker = ConnectNWinChecker(N, M, int(X))

minimax = MinimaxV2(checker, T)


if F == 0:
    oppo_move = int(input(""))
    row = N - count_list[oppo_move] - 1
    board[row][oppo_move] = -1
    count_list[oppo_move] += 1

while True:

    my_move = minimax.get_best_move(copy.deepcopy(board), copy.deepcopy(count_list))

    row = N - count_list[my_move] - 1
    board[row][my_move] = 1
    count_list[my_move] += 1
    last_played_cell = (row, my_move)


    print(my_move)

    # OPPONENT TURN
    oppo_move = int(input(""))
    row = N - count_list[oppo_move] - 1
    board[row][oppo_move] = -1
    count_list[oppo_move] += 1