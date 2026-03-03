# Name: Kwankhao Tangprasert
# Student ID: 653040165-6

## Heuristic Function (Strategies)

Using Cubic Weights Instead of Exponential
I use a cubic function (k³) for scoring instead of exponential values.
Since this algorithm is designed for Connect-N (not only Connect-4), exponential values can grow too fast when N becomes large, causing the score to explode and making the evaluation unstable.
Cubic growth increases steadily and generalizes better for different board sizes.

Win Score × 10 (Highest Priority)
If the algorithm detects a winning state, the score is multiplied by 10.
This ensures that winning moves are always prioritized over other heuristic patterns.

Threaten N-1 and N-2
The heuristic also checks:

If the opponent has N-1 in a row (almost winning)

If the opponent has N-2 in a row

This creates a strong bias toward blocking dangerous positions.
Additionally, the algorithm checks whether there is an empty space that actually allows the opponent to complete the connection. This prevents unnecessary blocking in situations where the opponent cannot win anyway.

Otherwise: Use Cubic Weight
For normal patterns that are not immediate threats or wins, the score is calculated using the cubic weight function.

## Base Case in Recursive Function
The base case helps the algorithm prefer immediate rewards instead of delaying them.

````
For example, if the current state already guarantees a win, the algorithm should choose that move immediately instead of selecting another move that might lead to a win in the future.
````

This prevents situations where the algorithm ignores a direct winning move and searches deeper unnecessarily.

## Valid Move Ordering

Valid moves are organized in a specific order (for example, center-first).
This improves the efficiency of Alpha-Beta Pruning, due to
- Strong moves are evaluated earlier.
- Alpha and Beta values are updated faster.
More branches can be pruned, leading to the search becomes significantly faster.