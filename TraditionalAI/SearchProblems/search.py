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
    # parent: "Node | None" = None # for path reconstruction and debugging

    def __post_init__(self):
        self.priority = self.distance + self.heuristic

    def is_goal(self, goal:Position) -> bool:
        return self.position == goal
    
    def get_key(self) -> Tuple[Position, bool]:
        return (self.position, self.is_ZT_used)
    
# heapq for priority queue with time complexity O(log n)


class Search:
    SUCCESSORS : List[Action] = [
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
        # visited is mean the node that in the queue but might not explore yet
        self.visited:Set[Position] = set() # used set instead of list due to O(1) when access the value
        self.m:int = 0 # row number of the map
        self.n:int = 0 # column number of the map
        self.len_ZT:int = 0 # number of Zanka no Tachi
        self.start:Position = (0, 0)  # start position (row, col)
        self.goal:Position = (0, 0)  # goal position (row, col)
        self.cell_cache : Dict[Position, int] = {} # remember that is this state call explore function
        self.best_distance : Dict[Position, int] = {} #closed list : with better distance only
        self.zt_move_offsets: List[Position] = []

    def state_transition(self, current_position:Position, successor:Action)->Position|None:
        dr, dc = successor
        next_position = (current_position[0] + dr, current_position[1] + dc)

        # the column and row should start at (1, 1) and end with -1 because the given size includes the wall
        # shotcut circuit due to that the posibility of the next position is explored higher than wall
        if (next_position[0] <= 0) or (next_position[1] <= 0) or \
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
        self.visited.add(self.start)

    def dfs(self):
        """
        Executes Depth-First Search to find a solution path.
        Task #1
        """

        while len(self.fringe) > 0:
            position = self.fringe.pop(-1)
            temp_stack:List[Position] = list()
            
            for action in self.SUCCESSORS:
                next_position = self.state_transition(position, action)

                if next_position and (next_position not in self.visited):
                    self.visited.add(next_position) # prevent duplicated explore calls, due to that the node in fringe will not explore again
                    state = explore(next_position[0], next_position[1])
                    if state =="G":
                        return
                    elif state == "X":
                        continue
                    else:
                        # Do not use insert because it take O(n)
                        temp_stack.append(next_position)
            self.fringe.extend(temp_stack[::-1])

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
        self.visited.add(self.start)

    def bfs(self) -> None:
        """
        Executes Breadth-First Search to find a solution path.
        Task #2
        """
        while len(self.fringe) > 0:
            position = self.fringe.pop(0)
            
            for action in self.SUCCESSORS:
                next_position = self.state_transition(position, action)
                if next_position and (next_position not in self.visited):
                    self.visited.add(next_position) # prevent duplicated explore calls, due to that the node in fringe will not explore again
                    state=explore(next_position[0], next_position[1])
                    if state =="G":
                        return
                    elif state == "X":
                        continue
                    else:
                        self.fringe.append(next_position)

    def heuristic(self, position:Position)->int:
        dx = abs(position[0]-self.goal[0])
        dy = abs(position[1]- self.goal[1])
        return (dx + dy)*2

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

        self.fringe : List[Node] = list() # open list
        heapq.heappush(self.fringe, Node(self.start, 0, self.heuristic(self.start), False))

        self.cell_cache : Dict[Position, int] = {self.start: 0} # remember that is this state call explore function
        self.best_distance : Dict[Position, int] = {} #closed list : with better distance only
        # self.visited is used to preventing from re-expanding the node that already expand

        self.zt_move_offsets: List[Position] = [
            (dx * i, dy * i)
            for i in range(1, self.len_ZT + 1)
            for dx, dy in self.SUCCESSORS
        ]

        # self.heuristic_vals = {
        #     (row, col): self.heuristic((row, col))
        #     for row in range(1, m - 1)
        #     for col in range(1, n - 1)
        # }
        # but it takes too much memory and computation in the large map: due to we didn't need to visited all cell in the map

    def Astar(self)->int:
        """
        Executes A* Search to find the optimal path distance.
        Task #3
        """

        while len(self.fringe) > 0:
            node = heapq.heappop(self.fringe)
            node_key = node.get_key()
            if node.is_goal(self.goal):
                return node.distance
                #return node.distance, node
            elif node_key in self.visited:
                del(node) # prevent memory leak
                continue
            else:
                self.visited.add(node_key)
            # if node.position was pop from the queue then continue because it already pop the best node
            
            if node.is_ZT_used:
                self.expand_node(self.SUCCESSORS, node,  False, True)
            else:
                self.expand_node(self.SUCCESSORS, node,  False, False)
                if self.len_ZT > 0:
                    self.expand_node(self.zt_move_offsets, node, True, True)


    def expand_node(self, successors:List[Action], node:Node, use_ZT:bool, is_ZT_used:bool):
        for successor in successors:
            next_position = self.state_transition(node.position, successor)
            if  next_position:
                if (next_position, is_ZT_used) in self.best_distance and node.distance >= self.best_distance[(next_position, is_ZT_used)]:
                    continue   # worse path > reject, prevent from compute too much

                if use_ZT:
                    weight = 0
                elif next_position in self.cell_cache:
                    # if it in cache, no need to explore again -> {(1,1):"S"} is a constant-time average operation due to the underlying hash table implementation which equal to set structure.
                    weight = self.cell_cache[next_position]
                else:
                    state:str=explore(next_position[0], next_position[1])
                    if state == "X":
                        weight = None
                    elif state in {"S", "G"}:
                        weight = 0
                    else:
                        weight = int(state)
                    self.cell_cache[next_position] = weight

                # Compute g(n)
                if weight is None:
                    continue
                distance = node.distance + weight
                self.best_distance[(next_position, is_ZT_used)] = distance
                
                heuristic_val = self.heuristic(next_position) 
                # heapq.heappush(self.fringe, Node(next_position, distance, heuristic_val, is_ZT_used, node))
                heapq.heappush(self.fringe, Node(next_position, distance, heuristic_val, is_ZT_used))