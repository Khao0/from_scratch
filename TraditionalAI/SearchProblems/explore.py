import myglobal

def explore(i, j):
    myglobal.explore_calls.append((i, j))
    return myglobal.secret_map[i][j]
