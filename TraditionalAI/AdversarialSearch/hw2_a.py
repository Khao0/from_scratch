#####
#
# Name: Kwankhao Tangprasert
# Student ID: 653040165-6
#
#####

import random

print("ready")

N,M,F,X,T = input("").strip().split(" ")
N = int(N)
M = int(M)
F = int(F)
T = float(T)


count_list = [0] * M

board = [[0] * M for _ in range(N)]

import json
import copy
from check_cons import ConnectNWinChecker
checker = ConnectNWinChecker(N, M, int(X))
from algorithms import UltimateMinimax

uMinimax = UltimateMinimax(checker, T)


if F == 0:
    oppo_move = int(input(""))
    row = N - count_list[oppo_move] - 1
    board[row][oppo_move] = -1
    count_list[oppo_move] += 1

while True:

    my_move = uMinimax.get_best_move(copy.deepcopy(board), copy.deepcopy(count_list))

    row = N - count_list[my_move] - 1
    board[row][my_move] = 1
    count_list[my_move] += 1

    # # check that the search won't change the original board
    # with open("board.json", "w") as wf:
    #     json.dump({"board":board}, wf)

    print(my_move)

    # OPPONENT TURN
    oppo_move = int(input(""))
    row = N - count_list[oppo_move] - 1
    board[row][oppo_move] = -1
    count_list[oppo_move] += 1