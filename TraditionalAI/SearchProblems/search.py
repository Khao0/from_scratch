#####
#
# Name: Kwankhao Tangprasert
# Student ID: 653040165-6
#
#####

from explore import explore  ##### DO NOT CHANGE THIS LINE #####

from typing import Tuple, List, Set, Literal, TypeAlias, Dict
Action:TypeAlias = Literal["right", "top", "left", "bottom"]
Position = Tuple[int, int]

class Search:
    ACTIONS :List[Action]= ["right", "top", "left", "bottom"]
    MOVE_MAP : Dict[Action, Position]= {
        "right":  (0, 1),
        "top":    (-1, 0),
        "left":   (0, -1),
        "bottom": (1, 0),
    }

    def __init__(self):
        """
        Initializes the Search class.
        """
        self.fringe:List[Position] = list()
        self.explored:Set[Position] = set() # used set instead of list due to O(1) when access the value 
        self.m:int = 0 # row number of the map
        self.n:int = 0 # column number of the map
        self.num_ZT:int = 0 # number of Zanka no Tachi
        self.start:Position = (0, 0)  # start position (row, col)
        self.goal:Position = (0, 0)  # goal position (row, col)

    def successor(self, current_position:Position, action:Action)->Position|None:
        dr, dc = self.MOVE_MAP[action]
        next_position = (current_position[0] + dr, current_position[1] + dc)

        # the column and row should start at (1, 1) and end with -1 because the given size includes the wall
        # shotcut circuit due to that the posibility of the next position is explored higher than wall
        if (next_position in self.explored) or \
            (next_position[0] <= 0) or (next_position[1] <= 0) or \
            (next_position[0] >= self.m - 1) or (next_position[1] >= self.n - 1):
            return None
        return next_position

    def initialize_dfs(self, m:int, n:int, sr:int, sc:int, gr:int, gc:int):
        """
        Initializes parameters for Depth-First Search (DFS).
        Task #1
        """
        self.m = m 
        self.n = n
        self.start = (sr, sc)
        self.goal = (gr, gc) # this is for hueristic function in A* search
        self.fringe.append(self.start)
        self.explored.add(self.start)

    def dfs(self):
        """
        Executes Depth-First Search to find a solution path.
        Task #1
        """

        while len(self.fringe) > 0:
            position = self.fringe.pop(-1)
            stack:List[Position] = list()
            
            for action in self.ACTIONS:
                next_position = self.successor(position, action)

                if next_position:
                    self.explored.add(next_position) # prevent duplicated explore calls, due to that the node in fringe will not explore again
                    result = explore(next_position[0], next_position[1])
                    if result =="G":
                        return
                    elif result == "X":
                        continue
                    else:
                        # Do not use insert because it take O(n)
                        stack.append(next_position)
            self.fringe.extend(stack[::-1])

    def initialize_bfs(self, m:int, n:int, sr:int, sc:int, gr:int, gc:int):
        """
        Initializes parameters for Breadth-First Search (BFS).
        Task #2
        """
        self.m = m 
        self.n = n 
        self.start = (sr, sc)
        self.goal = (gr, gc)
        self.fringe.append(self.start)
        self.explored.add(self.start)

    def bfs(self) -> None:
        """
        Executes Breadth-First Search to find a solution path.
        Task #2
        """
        while len(self.fringe) > 0:
            position = self.fringe.pop(0)
            
            for action in self.ACTIONS:
                next_position = self.successor(position, action)
                if next_position:
                    self.explored.add(next_position) # prevent duplicated explore calls, due to that the node in fringe will not explore again
                    result=explore(next_position[0], next_position[1])
                    if result =="G":
                        return
                    elif result == "X":
                        continue
                    else:
                        self.fringe.append(next_position)
            

    def initialize_Astar(self, m:int, n:int, sr:int, sc:int, gr:int, gc:int, k:int):
        """
        Initializes parameters for A* Search.
        Task #3
        """
        pass #TODO

    def Astar(self):
        """
        Executes A* Search to find the optimal path distance.
        Task #3
        """
        # priority Queue
        pass #TODO