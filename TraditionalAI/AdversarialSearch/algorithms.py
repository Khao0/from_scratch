from check_cons import ConnectNWinChecker, Board
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
import random
import copy
import json
import math


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
        # prefer center position due to it can control the board
        valid_actions.sort(key=lambda c: abs(c - self.checker.num_col // 2))
        return valid_actions
    
    @abstractmethod
    def search(self):
        pass

    @abstractmethod
    def get_best_move(self):
        pass


class Minimax(Base):

    def __init__(self, checker):
        super().__init__(checker)
        self.depth_limit = 5
    
    def search(self,board:Board, depth:int, isMaximizingPlayer:bool, count_list:List[int], last_played_cell:Tuple[int]):
        if self.checker.is_win(board, isMaximizingPlayer, last_played_cell) :
            return 1 if isMaximizingPlayer else -1
        if depth == self.depth_limit  or count_list == self.tie_state:
            return 0
        
        if isMaximizingPlayer:
            best_score = -float("inf")
            
            for col in self.list_valid_move(count_list):
                row = self.checker.num_row - count_list[col] - 1
                last_played_cell = (row, col)

                board[row][col] = 1 # min player
                
                count_list[col] +=1
                
                score = self.search(board, depth+1, False, count_list, last_played_cell)
                
                count_list[col] -=1
                
                board[row][col] = 0 # reset for next simu move
                best_score = max(score, best_score)
            return best_score
            
        else:
            best_score = float("inf")
            for col in self.list_valid_move(count_list):
                row = self.checker.num_row - count_list[col] - 1
                last_played_cell = (row, col)

                board[row][col] = -1 # min player
                
                count_list[col] +=1
                
                score = self.search(board, depth+1, True, count_list, last_played_cell)
                
                count_list[col] -=1
                
                board[row][col] = 0 # reset for next simu move
                
                best_score = min(score, best_score)
            return best_score
    
    def get_best_move(self, board:Board, count_list:List[int])->int:
        best_score = -float("inf")
        best_moves = []

        for move in self.list_valid_move(count_list):

            row = self.checker.num_row - count_list[move] - 1
            board[row][move] = 1 # assume that i always maximize
            count_list[move] += 1

            score = self.search(
                board,
                0,
                False,  # opponent turn
                count_list,
                (row, move)
            )

            count_list[move] -= 1
            board[row][move] = 0

            if score == best_score:
                best_moves.append(move)
            elif score > best_score:
                best_score = score
                best_moves = [move]
        
        return random.choice(best_moves)

import time

def evaluate(board, N):
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

class UltimateMinimax(Base):
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
            win_value = 10 ** (self.checker.win_score + 1) 
            # If it's currently Maximizer's turn and there's a win, Maximizer lost
            return -win_value if isMaximizingPlayer else win_value 
        elif count_list == self.tie_state:
            return 0
        elif depth == 0:
            return evaluate(board, self.checker.win_score)
        
        
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






class Node:
    def __init__(self, move=None, parent=None, player=True, terminal=False):
        self.move: Optional[int] = move
        self.parent:Optional[Node] = parent
        self.player = player  # player to move at this node
        self.children = []
        self.wins = 0.0
        self.visits = 0
        self.terminal = terminal

    def expand_node(self, valid_actions:List[int])->"Node":
        move = random.choice(valid_actions)
        nc = Node(move, self, not self.player)
        self.children.append(nc)
        return nc

    def update(self, r):
        self.visits += 1
        self.wins += r

    def is_leaf(self):
        return len(self.children)==0

    def has_parent(self):
        return self.parent is not None

class MCTS(Base):
    def __init__(self, checker):
        super().__init__(checker)
        self.depth_limit = 5 # then compute by hueristic function
        self.time_limit = 0
        self.weight = 1

    @staticmethod
    def heursistic(board:Board)->float:
        return
    

    def calculate_UCB(self, node:Node)->float:
        if node.visits == 0:
            return float("inf") # priotize it due to it never explore, encourage to explore each child node at once
        avg = (node.wins / node.visits)
        explore = (math.log(node.parent.visits) / node.visits)**(1/2)
        return avg + (self.weight*explore)
    

    def select_best_child(self, node:Node)->Node:
        best_score = -float("inf")
        best_node = None
        for child_node in node.children:
            score = self.calculate_UCB(child_node)
            if score > best_score:
                best_score = score
                best_node = child_node
        return best_node
    
    def apply_move(self, board: Board, count_list: List[int], node: Node)->Tuple[Board, List[int]]:
        col = node.move
        row = self.checker.num_row - count_list[col] - 1
        board[row][col] = node.player
        count_list[col] += 1
        return board, count_list

    def simulate(self, board:Board, count_list:List[int], isMaximizingPlayer:bool):
        depth = 0
        
        while True:
            valid_actions = self.list_valid_move(count_list)
            if not valid_actions: # tie
                return 0
            
            action = random.choice(valid_actions)
            row = self.checker.num_row - count_list[action] - 1 # find row 
            last_played_cell = (row, action)

            board[row][action] = isMaximizingPlayer

            if self.checker.is_win(board, isMaximizingPlayer, last_played_cell) :
                return 1 if isMaximizingPlayer else -1
            
            count_list[action] +=1
            isMaximizingPlayer  = not isMaximizingPlayer
            depth +=1


    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent


    def search(self):
        return super().search()

    def get_best_move(self, base_board:Board, base_count_list:List[int]):
        root_node = Node(None, None, True)

        # row = self.checker.num_row - count_list[self.move] - 1

        node = root_node
        board = copy.deepcopy(base_board)
        count_list = copy.deepcopy(base_count_list)

        #* Selection
        while not node.is_leaf():
            node = self.select_best_child(node) # select the best node in the same level
            board, count_list = self.apply_move(board, count_list, node)

        if node.terminal:
            reward = 1 if node.player else -1

        else :
            valid_moves = self.list_valid_move(count_list)
            if not valid_moves:
                reward = 0
            else:
                #* Expansion
                child_node = node.expand_node(valid_moves)
                node = child_node

                board, count_list = self.apply_move(board, count_list, node)
                row = self.checker.num_row - count_list[node.move] -1
                if self.checker.is_win(board,count_list, (row, node.move)):
                    node.terminal = True
                    reward = 1 if node.player else -1
                else :
                    #* Simulation
                    reward = self.simulate(copy.deepcopy(board), copy.deepcopy(count_list), node.player)

        #* Backpropagate
        self.backpropagate(node, reward)