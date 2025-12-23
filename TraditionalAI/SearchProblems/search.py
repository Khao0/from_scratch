#####
#
# Name: Kwankhao Tangprasert
# Student ID: 653040165-6
#
#####

from explore import explore  ##### DO NOT CHANGE THIS LINE #####

from typing import Tuple, List, Set, Literal, TypeAlias, Dict
Step: TypeAlias = Literal[-1, 0, 1]
Action: TypeAlias = Tuple[Step, Step]
Position:TypeAlias = Tuple[int, int]
import heapq
from dataclasses import dataclass, field

@dataclass(order=True) # set for heapq
class Node:
    priority: int = field(init=False, repr=False) # total cost f(n) = g(n) + h(n)
    position: Position
    distance:int
    heuristic:int
    is_ZT_used:bool
    parent: "Node | None" = None # for path reconstruction


    def __post_init__(self):
        self.priority = self.distance + self.heuristic

    def is_goal(self, goal:Position) -> bool:
        return self.position == goal
    
# heapq for priority queue with time complexity O(log n)


class Search:
    SUCCESSORS : List[Position] = [
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 0),
    ]

    def __init__(self):
        """
        Initializes the Search class.
        """
        self.fringe:List[Position] = list()
        self.explored:Set[Position] = set() # used set instead of list due to O(1) when access the value 
        self.m:int = 0 # row number of the map
        self.n:int = 0 # column number of the map
        self.len_ZT:int = 0 # number of Zanka no Tachi
        self.start:Position = (0, 0)  # start position (row, col)
        self.goal:Position = (0, 0)  # goal position (row, col)

    def successor(self, current_position:Position, action:Action)->Position|None:
        dr, dc = action
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
            
            for action in self.SUCCESSORS:
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
            
            for action in self.SUCCESSORS:
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

    @staticmethod
    def _manhattan_distance(pos1:Position, pos2:Position) -> int: # because we can perform only 4 action
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])
    # have to find new heuristic function that fit with ZT and without ZT due to manhattan distance is baseline
    
    def heuristic(self, position:Position)->int:
        # due to we utilized priority queue so the node that activate this function is the lowest cost already
        # the 
        dx = abs(position[0]-self.goal[0])
        dy = abs(position[1]- self.goal[1])
        # manhattan_distance - (len_zt+1 - min between x and y)
        ...
    
    def successor_Astar(self, current_position:Position, action:Action)->Position|None:
        dr, dc = action
        next_position = (current_position[0] + dr, current_position[1] + dc)

        # the column and row should start at (1, 1) and end with -1 because the given size includes the wall
        # shotcut circuit due to that the posibility of the next position is explored higher than wall
        if  (next_position[0] <= 0) or (next_position[1] <= 0) or \
            (next_position[0] >= self.m - 1) or (next_position[1] >= self.n - 1):
            return None
        return next_position

    def initialize_Astar(self, m:int, n:int, sr:int, sc:int, gr:int, gc:int, k:int):
        """
        Initializes parameters for A* Search.
        Task #3
        """
        self.m = m 
        self.n = n
        self.len_ZT = k
        self.start = (sr, sc)
        self.goal = (gr, gc)

        self.successors: List[Position] = [
            (dx * i, dy * i)
            for i in range(1, self.len_ZT + 1)
            for dx, dy in self.SUCCESSORS
        ]

        # print(self.successors)

        self.fringe : List[Node] = list() # open list
        heapq.heappush(self.fringe, Node(self.start, 0, self._manhattan_distance(self.start, self.goal), False))

        self.cell_cache : Dict[Position, str] = {self.start: "S"} # remember that is this state call explore function
        self.best_distance : Dict[Position, int] = {self.start:self._manhattan_distance(self.start, self.goal)} #closed list : with better distance only
        self.position_cache : Set[Position] = set(self.start) # preventing from re-expanding the node that already expand

    def Astar(self)->int:
        """
        Executes A* Search to find the optimal path distance.
        Task #3
        """

        while len(self.fringe) > 0:
            node = heapq.heappop(self.fringe)
            current_position = node.position
            if node.is_goal(self.goal):
                return node.distance
                #return node.distance, node
            elif (current_position, node.is_ZT_used) in self.position_cache:
                continue
            else:
                self.position_cache.add((current_position, node.is_ZT_used))
            # if node.position was pop from the queue then continue because it already pop the best node
            
            if node.is_ZT_used:
                self.perform_action(self.SUCCESSORS, node, current_position, False, True)
            else:
                self.perform_action(self.SUCCESSORS, node, current_position, False, False)
                if self.len_ZT:
                    self.perform_action(self.successors, node, current_position,True, True)


    def perform_action(self, successors, node, current_position, use_ZT, is_ZT_used):
        for successor in successors:
        # for successor in self.SUCCESSORS:
            dr, dc = successor
            next_position = (current_position[0] + dr, current_position[1] + dc)

            if  not ((next_position[0] <= 0) or (next_position[1] <= 0) or \
                (next_position[0] >= self.m - 1) or (next_position[1] >= self.n - 1)):
                if use_ZT:
                    state = "ZT"
                elif next_position in self.cell_cache:
                    # if it in cache, no need to explore again -> {(1,1):"S"} is a constant-time average operation due to the underlying hash table implementation which equal to set structure.
                    state = self.cell_cache[next_position]
                else:
                    state:str=explore(next_position[0], next_position[1])
                    self.cell_cache[next_position] = state
                    

                # Compute g(n)
                if state == "X":
                    continue
                elif state in {"S", "G", "ZT"}:
                    distance = node.distance
                else:
                    distance = node.distance + int(state)
                
                if (next_position, is_ZT_used) in self.best_distance and distance >= self.best_distance[(next_position, is_ZT_used)]:
                    continue   # worse path > reject, prevent from compute too much
                self.best_distance[(next_position, is_ZT_used)] = distance
                
                heuristic_val = self._manhattan_distance(next_position, self.goal)
                heapq.heappush(self.fringe, Node(next_position, distance, heuristic_val, is_ZT_used, node))

if __name__ == "__main__":
    print(Search._manhattan_distance((0,0), (4,3)))

    # TODO : refactor code
    # TODO : change heuristic function
    # TODO : optimize performance both time and space