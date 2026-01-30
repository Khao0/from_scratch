import time
import random

time.sleep(2)
print("ready")

N,M,F,X,T = input("").strip().split(" ")
N = int(N)
M = int(M)
F = int(F)
T = float(T)
count_list = [0] * M

if F == 0:
    oppo_move = int(input("").strip())
    count_list[oppo_move] +=1

while True:
    if T > 0.3:
        time.sleep(T-0.3)
    while True:
        my_move = random.randint(0,M-1)
        if count_list[my_move] != N:
            count_list[my_move] += 1
            print(my_move)
            break
    oppo_move = int(input("").strip())
    count_list[oppo_move] +=1
