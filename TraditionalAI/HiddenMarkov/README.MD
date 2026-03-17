# Name: Kwankhao Tangprasert
# Student ID: 653040165-6

In this assignment, I applied a simple Hidden Markov Model (HMM) to solve the "Werewolf" game. The HMM is suitable for this problem because the true roles of players (wolves or villagers) are hidden states, while their actions during the interrogation phase are observable. These observations allow us to iteratively update our belief about each player's role using probabilistic inference.

To evaluate the model, I designed an experimental framework that simulates the game 1,000 times. The performance is measured using two metrics: overall win rate and deduction accuracy.

During experimentation, I explored several enhancements, such as incorporating the number of remaining wolves and aggregating accusation counts to refine the belief updates. However, these modifications did not significantly improve performance based on the evaluation metrics.

The best results were achieved using the baseline HMM approach, which obtained approximately 84% win rate and 67% deduction accuracy.

For future work, I plan to improve the model by applying Particle Filtering to better capture the joint distribution of player roles. Additionally, I am interested in integrating iterative deepening strategies to enhance decision-making during the deduction phase.
