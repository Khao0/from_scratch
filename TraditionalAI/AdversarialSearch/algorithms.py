from check_cons import ConnectNWinChecker, Board
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
import time


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


def baseline_heuristic(board, N):
    rows = len(board)
    cols = len(board[0])
    
    score = 0
    
    # exponential weights
    weights = [0] + [10**(k-1) for k in range(1, N)]
    # weights[k] = weight for k in a row

    def evaluate_window(window):
        nonlocal score
        
        x_count = window.count(1)
        o_count = window.count(-1)
        
        if x_count > 0 and o_count > 0:
            return  # blocked line
        
        # add case that have 2 but it doenst' matter  
        # add statigic
        if x_count == N:
            score += 10**N  # big win
        elif o_count == N:
            score -= 10**N
        elif x_count > 0:
            score += weights[x_count]
        elif o_count > 0:
            score -= weights[o_count]

    # Horizontal
    for r in range(rows):
        for c in range(cols - N + 1):
            window = [board[r][c+i] for i in range(N)]
            evaluate_window(window)

    # Vertical
    for c in range(cols):
        for r in range(rows - N + 1):
            window = [board[r+i][c] for i in range(N)]
            evaluate_window(window)

    # Diagonal /
    for r in range(rows - N + 1):
        for c in range(cols - N + 1):
            window = [board[r+i][c+i] for i in range(N)]
            evaluate_window(window)

    # Diagonal \
    for r in range(N-1, rows):
        for c in range(cols - N + 1):
            window = [board[r-i][c+i] for i in range(N)]
            evaluate_window(window)

    return score


class Minimax(Base):
    def __init__(self, checker, time_limit):
        super().__init__(checker)
        self.time_limit = time_limit*0.95
        self.start_time = None

    def set_start_time(self):
        self.start_time = time.time()

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
            base_reward = 10 ** (self.checker.win_score + 2)
            # If it's currently Maximizer's turn and there's a win, Maximizer lost
            reward = base_reward + (depth *1)

            return -reward if isMaximizingPlayer else reward
        
        elif count_list == self.tie_state:
            return 0
        
        elif depth == 0:
            return baseline_heuristic(board, self.checker.win_score)
        
        
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
    

class MinimaxV2(Minimax):
    def __init__(self, checker, time_limit):
        super().__init__(checker, time_limit)
        # cubic weights instead of exponential
        self.weights = [0] + [k**3 for k in range(1, self.checker.win_score+1)]

        self.WIN_SCORE = self.weights[self.checker.win_score] * 10  # priotize the most

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


class MinimaxBitboard(Base):
    pass