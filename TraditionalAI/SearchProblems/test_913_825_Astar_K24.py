import sys
from search import Search
import myglobal

secret_map_file = "map_913_825_Astar.txt"
K = 24
solution = 4013

with open(secret_map_file, 'r') as file:
    m, n = map(int, file.readline().split())
    sr, sc = map(int, file.readline().split())
    gr, gc = map(int, file.readline().split())
    myglobal.secret_map = [file.readline().strip() for _ in range(m)]
    myglobal.secret_map = [[myglobal.secret_map[i][j] for j in range(n)] for i in range(m)]

from time import time
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
