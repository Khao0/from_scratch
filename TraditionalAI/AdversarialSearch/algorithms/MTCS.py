from check_cons import ConnectNWinChecker, Board
from algorithms import Base
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
import random
import copy
import math
import time

# this method not working for connect-N due to weight (C) depend on board size 
# and difficult to fine tune param


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