import sys
from search import Search
import myglobal

secret_map_file = "map_medium_bfs_dfs.txt"
solution_file = "sol_medium_bfs.txt"

with open(secret_map_file, 'r') as file:
    m, n = map(int, file.readline().split())
    sr, sc = map(int, file.readline().split())
    gr, gc = map(int, file.readline().split())
    myglobal.secret_map = [file.readline().strip() for _ in range(m)]
    myglobal.secret_map = [[myglobal.secret_map[i][j] for j in range(n)] for i in range(m)]

with open(solution_file, 'r') as file:
    sol_len = int(file.readline().strip())
    solution = [tuple(map(int, file.readline().split())) for _ in range(sol_len)]

myglobal.explore_calls = []
ms = Search()
ms.initialize_bfs(m, n, sr, sc, gr, gc)
ms.bfs()

correct = True
if sol_len != len(myglobal.explore_calls):
    correct = False
else:
    for i in range(sol_len):
        if myglobal.explore_calls[i] != solution[i]:
            correct = False
            break
if correct:
    print("Correct Order!!!")
else:
    print("Incorrect Order :(")
