# Connect4

For detailed reading, refer [here](https://github.com/shikha-16/Connect4/blob/main/Report.pdf)

## Introduction
In this study, we design the game of Connect-4, implement 2 reinforcement learning agents and observe the results as they play against each other with varying parameters. Reinforcement algorithms have an agent that finds itself in various situations, or states. The agent performs an action to go to the next state. A policy is the strategy of choosing which action to take, given a state, in expectation of better outcomes. After the transition, the agent receives a reward (positive or negative) in return. This is how the agent learns.
The game of Connect 4 has a special property - there is an exponential increase in the number of possible actions that can be played. To combat this we have used 2 methods of reinforcement learning, namely Monte Carlo Tree Search (MCTS) and Q-Learning with the concept of afterstates. Monte Carlo Tree Search constructs a 'game tree' and performs a number of simulations to predict the next move that should be taken by the player. Q-Learning estimates values for each state of the game and learns this value (Q-value) by convergence after training through many episodes. Then the state with the best Q value is selected. Let us study these in detail in the next sections.

## Game Implementation
A smaller version (5 columns × 6 rows) of Connect 4 game has been implemented using a class 'Board'. (Table 1) The class describes the current state of the board as a 2D grid. The 'state' is represented as a board object in MCTS, and as a 2D integer matrix in Q-learning. On their turn, a 'Player' object (Table 2) evaluates all the empty positions available in the board (actions) using the method getEmptyPositions(), the MCTS or Q-Learning algorithm helps them decide which move to play, and then the play() method is called to execute the move, and the next state of the board is returned. After every move, the checkWinner() method is called to evaluate if any player has won. 


## Monte Carlo Tree Search Algorithm
The Monte Carlo Tree Search algorithm is a popular algorithm that figures out the best move out of a set of moves for a player. We construct a game tree with a root node, and then we keep expanding it using simulations. Each node represents the state of the board in the game. (Table 4) The edges between the nodes represent the actions taken to reach that state. In the process, we maintain visit count and win count for each node. This method is repeated for a number of playouts and then we select the node with the most promising value for the next move. There are 4 main steps to an MCTS algorithm. (Figure 1) (Table 3)
Step 1: Selection - We use tree policy to construct a path from root to the most promising leaf node. Each node has an associated value and during selection, we always chose the child node with the highest value.
Step 2: Expansion - We randomly pick an unexplored child of the leaf node.
Step 3: Simulation - We play out one or more simulations of the game after the expanded child node, until a winner is reached. The action selection policy here is random, such that it is fast to execute.
Step 4: Backpropagation - In this step, after we have a winner, we trace back the path we came through to reach the expanded child node, and update the visit and win values of all the nodes on this path.

### Implementation
Two versions of Monte Carlo Tree Search (MCTS) algorithm have been implemented for playing the Connect 4 game. Version MC40 uses 40 simulations (playouts) before picking an action, and version MC200 uses 200 simulations before picking an action. The two versions maintain separate game trees and run the MCTS algorithm with their respective number of playouts to select the next move.
The state space is each board object generated when a player plays. Each player has their own separate state space. The action space is the positions in the board (i, j) that can be played. The value of each state is evaluated by the number of wins/number of playouts from that particular state. The tree selection policy used is Upper Confidence Bound Selection, giving more preference to those actions whose values are uncertain.

## Q-Learning Algorithm
Q-Learning is a reinforcement learning algorithm that estimates values for each state of the game and learns this value (Q-value) by convergence after training through many episodes. Every time the Q-learning agent encounters a state visited before, it incrementally updates the action it previously took based on whether its previous action earned a positive or negative reward.

### Implementation
The Q-learning algorithm has been implemented for playing the simplified Connect-4 game with the number of rows ranging from 2 to 4.
The state space is each 2D integer matrix board generated when a player plays. The action space is the positions in the board (i, j) that can be played. The rewards are +2 if the agent wins, -2 if the agent loses, +0.5 in case of a draw and 0 otherwise.
Since there are many possible values of state-action pairs in a game like Connect-4, the concept of afterstates is used. This gives us a Q value for each state after a move and the incremental updating of the values is done by the Q-Learning equation.
 
 
## Conclusion
The MCTS agent takes a lot more playouts to learn than the Q learning agent, but the learning is a lot faster, as the Q learning agent takes very long for convergence. Connect 4 has a large number of possible states, which means that probably every game ever played is unique. We see that as the number of rows increase, the number of states increase and then the MCTS algorithm starts performing much better than the Q-learning algorithm, due to the convergence factor.
Both the agents learn to generalize and play well. The Q learning agent learns to generalize by learning similarities between different states and the MCTS agent learns to take the best path statistically. Both of these are promising methods for gameplay and are widely used in RL.

