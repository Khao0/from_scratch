# Name: Kwankhao Tangprasert
# Student ID: 653040165-6

## Answer
For this problem, movement action is restricted to the four directions (Up, Down, Left, Right) with cell costs ranging from 1 to 9. While the standard Manhattan distance is a theoretically admissible heuristic for this setup. However I found that it resulted in a large number of `explore()` calls.

To address this, I adjusted the heuristic by scaling the Manhattan distance by a factor of 2. This modification successfully reduced the number of exploration steps by approximately 6% comparing to the standard Manhattan distance. In addition, this weighted heuristic was still able to find the optimal path across all provided test sets (map_441_381_Astar, map_441_381_Astar, map_715_751_Astar, map_715_751_Astar, map_913_825_Astar,). 

```python
# This function demonstrate the answer herueristic function
def heuristic(self, position:Position)->int:
    dx = abs(position[0]-self.goal[0])
    dy = abs(position[1]- self.goal[1])
    return (dx + dy)*2
```

> **Experimental Result:** Scaling the Manhattan distance by a factor greater than 2 dramatically reduced the number of `explore()` calls. However, one test case failed to find the optimal path. This confirms that a factor over 2 makes the heuristic **inadmissible**, and increasing this factor further increases the probability of generating suboptimal paths.


## For other solution
I also considered to utilizing the Zanka no Tachi ability directly into the heuristic function. My idea was to subtract from the Manhattan distance by the length of the ZT jump when the ability hadn't been used yet. However, my experiments showed that this actually increased the number of exploration steps. The discounted heuristic reduced the estimated cost too much, which encouraged the algorithm to explore too many potential paths aggressively instead of focusing on the optimal one.

```python
def heuristic(self, position:Position, is_ZT_used:bool)->int:
    dx = abs(position[0]-self.goal[0])
    dy = abs(position[1]- self.goal[1])
    if not is_ZT_used:
        return dx + dy - self.len_ZT
    else:
        return dx + dy
```