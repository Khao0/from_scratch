import sys
from search import Search
import myglobal
from time import time

secret_map_file = "map_441_381_Astar.txt"
K = 0
solution = 8137

with open(secret_map_file, 'r') as file:
    m, n = map(int, file.readline().split())
    sr, sc = map(int, file.readline().split())
    gr, gc = map(int, file.readline().split())
    myglobal.secret_map = [file.readline().strip() for _ in range(m)]
    myglobal.secret_map = [[myglobal.secret_map[i][j] for j in range(n)] for i in range(m)]

start_time = time()

myglobal.explore_calls = []
ms = Search()
ms.initialize_Astar(m, n, sr, sc, gr, gc, K)
answer = ms.Astar()

end_time = time()

print("Time taken: {:.6f} seconds".format(end_time - start_time))

if solution == answer:
    print("Your function returns " + str(answer))
    print("Correct shortest distance!!!")
    print("You have called the explore() function", len(myglobal.explore_calls), "times")
else:
    print("Your function returns " + str(answer))
    print("Incorrect shortest distance :(")
