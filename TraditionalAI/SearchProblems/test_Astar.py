from dataclasses import dataclass
from typing import List
from time import time
from search import Search
import myglobal


HEADER = (
    f"{'Map':<22} {'K':>3} "
    f"{'Sol':>6} {'Ans':>6} "
    f"{'Expl(B)':>10} {'Expl(Y)':>10} {'ΔExpl%':>9} "
    f"{'Time(B)':>9} {'Time(Y)':>9} {'×Speed':>8}"
)


print(HEADER)
print("-" * len(HEADER))

@dataclass
class Test:
    map_file:str
    K:int
    solution:int
    explore_baseline:int
    time_baseline:float

tests:List[Test] = [
    Test("map_441_381_Astar",0, 8137, 154782, 0.438269),
    Test("map_441_381_Astar",1, 4766, 144177, 0.983800),
    Test("map_715_751_Astar",1, 8079, 465035, 3.956212),
    Test("map_715_751_Astar",4, 8064, 465248, 4.554169),
    Test("map_913_825_Astar",24, 4013, 149291, 2.035410),
]

for test in tests:
    with open(f"{test.map_file}.txt", 'r') as file:
        m, n = map(int, file.readline().split())
        sr, sc = map(int, file.readline().split())
        gr, gc = map(int, file.readline().split())
        myglobal.secret_map = [list(file.readline().strip()) for _ in range(m)]

    myglobal.explore_calls = []

    start_time = time()
    ms = Search()
    ms.initialize_Astar(m, n, sr, sc, gr, gc, test.K)
    answer = ms.Astar()
    end_time = time()

    expl_yours = len(myglobal.explore_calls)
    time_yours = end_time - start_time

    delta_expl_pct = (
        (expl_yours - test.explore_baseline) / test.explore_baseline * 100
        if test.explore_baseline > 0 else 0.0
    )
    speedup = test.time_baseline / time_yours if time_yours > 0 else float('inf')

    status = "✓" if answer == test.solution else "✗"

    print(
    f"{test.map_file:<22} {test.K:>3} "
    f"{test.solution:>6} {answer:>6} "
    f"{test.explore_baseline:>10} {expl_yours:>10} "
    f"{delta_expl_pct:>+8.2f}% "
    f"{test.time_baseline:>9.3f} {time_yours:>9.3f} {speedup:>8.2f} {status}"
)