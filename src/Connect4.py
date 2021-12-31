import random
import math
import copy
import gzip
import shutil

class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.columns = cols
        self.board = [[0 for i in range(self.columns)] for j in range(self.rows)] #board[i][j] = 0 if no one has played yet, 1 if player1 has their chip, 2 if player 2 has their chip.

    def play(self, playerNo, position):
        #takes a move and player as input, returns the new board after playing, and the column played
        self.board[position[0]][position[1]] = playerNo
        return self, position[1]+1

    def getEmptyPositions(self):
        #takes the current board, and returns possible positions for next chip
        ans = []
        for j in range(self.columns):
            i = self.rows - 1
            while i >= 0 and self.board[i][j] != 0:
                i -= 1
            if i >= 0:
                ans.append((i,j))
        return ans

    def checkWinner(self):
        #takes the current board and checks if anyone has won yet, and returns the player who has won.
        flag = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if j < self.columns - 3 and self.board[i][j] ==  self.board[i][j+1] == self.board[i][j+2] == self.board[i][j+3] != 0:
                    return self.board[i][j]
                
                if i < self.rows - 3 and self.board[i][j] ==  self.board[i+1][j] == self.board[i+2][j] == self.board[i+3][j] != 0:
                    return self.board[i][j]

                if i < self.rows - 3 and j < self.columns - 3 and self.board[i][j] ==  self.board[i+1][j+1] == self.board[i+2][j+2] == self.board[i+3][j+3] != 0:
                    return self.board[i][j]
                
                if i >= 3 and j < self.columns - 3 and self.board[i][j] ==  self.board[i-1][j+1] == self.board[i-2][j+2] == self.board[i-3][j+3] != 0:
                    return self.board[i][j]

                if self.board[i][j] == 0:
                    flag = 1
        if flag == 0:
            return 0

        return -1
    
    def deepcopy(self):
        newobj = Board(self.rows, self.columns)
        newobj.board = copy.deepcopy(self.board)
        return newobj
    
    def printBoard(self):
        #prints the current board
        for i in range(self.rows):
            for j in range(self.columns):
                print(self.board[i][j], end = " ")
            print()


class Node:
    #each node is a state, which is basically a representation of a board state
    def __init__(self, board, player, col=0, parent=None):
        self.board = board
        self.col = col
        self.children = [] 
        self.parent = parent
        self.player = player
        self.playouts = 0 
        self.wins = 0 
    
    def deepcopy(self):
        newobj = Node(copy.deepcopy(self.board), self.player, self.col, self.parent)
        newobj.children = self.children
        newobj.playouts = self.playouts
        newobj.wins = self.wins
        return newobj


class Player:
    def __init__(self, playerNo, n=0, opp=None):
        self.playerNo = playerNo
        self.playouts = n
        self.opponent = opp


class MonteCarloTreeSearch:

    def __init__(self, player, c=math.sqrt(2)):
        self.player = player
        self.playouts = player.playouts
        self.tree = None
        self.c = c

    def select(self):
        #returns leaf of tree after repeatedly applying uct
        node = self.tree
        while node.children:
            node = self.uct(node)
        return node

    def uct(self, node):
        #takes in a node, and returns the child node with maximum ucb value.
        next = node
        max_ucb = 0
        for child in node.children:
            if node.playouts == 0 or child.playouts == 0:
                ucb = math.inf
            else:
                ucb = child.wins/child.playouts + self.c * math.sqrt(math.log(node.playouts)/child.playouts)

            if ucb >= max_ucb:
                max_ucb =  ucb
                next = child
        return next

    def expand(self, leaf):
        #takes in a leaf node, evaluates all possible actions from it, picks a random action and returns a new node created in the tree with this action.
        possibilities = leaf.board.getEmptyPositions()
        if not possibilities:
            return leaf

        for p in possibilities:
            newBoard = leaf.board.deepcopy()
            newBoard, col = newBoard.play(leaf.player.opponent.playerNo, p)
            expandedNode = Node(newBoard, leaf.player.opponent, col, leaf)
            leaf.children.append(expandedNode)
        return random.choice(leaf.children)

    def simulate(self, node):
        #takes in a node, and simulates a playout from it until someone wins, or its a draw.

        trial = node.deepcopy()
        person = trial.player.opponent
        while trial.board.checkWinner() == - 1:
            possibilities = trial.board.getEmptyPositions()
            if not possibilities:
                return 0
            move = random.choice(possibilities)
            trial.board.play(person.playerNo, move)
            person = person.opponent
        return trial.board.checkWinner()
    
    def back_propagate(self, result, node):
        #takes in a winner and the expandedNode, then updates theresults accordingly in the game tree.
        while node:
            if node.player.playerNo == result:
                node.wins += 1
            node.playouts += 1
            node = node.parent

    def nextState(self, board):
        #takes the current state and evaluates the best action using MCTS algorithm, returns the next node selected,
        self.tree = Node(board, self.player.opponent)

        n = self.playouts
        while n > 0:
            leaf = self.select()
            child = self.expand(leaf)
            result = self.simulate(child)
            self.back_propagate(result, child)
            n -= 1
            
        #returning next state with the highest number of playouts
        max_playouts = 0
        nextnode = self.tree
        for child in self.tree.children:
            if child.playouts > max_playouts:
                max_playouts = child.playouts
                nextnode = child
        return nextnode


class QLearning:
    
    def __init__(self, player, epsilon=0.3, alpha=0.5, gamma=0.9):
        self.player = player
        self.q = {}
        self.epsilon = epsilon 
        self.alpha = alpha 
        self.gamma = gamma
        
    def getQ(self, state):
        #Fetches q-value of a state. If it is accessed for the first time, initializes the q value to 1 (to encourage exploration).
        x = tuple(map(tuple, state.board))
        if x not in self.q:
            self.q[x] = 1.0
        return self.q[x]
    
    def getReward(self, state):
        #Checks if the current state is a terminal state and returns reward values accordingly
        game_results = state.checkWinner()
        if game_results == 0:
            reward = 0.5
        elif game_results == self.player.playerNo:
            reward = 2.0
        elif game_results == self.player.opponent.playerNo:
            reward = -2.0
        else:
            reward = 0.0
        return reward

    def nextAction(self, state, actions):
        #Chooses an action based on the ε-greedy policy

        #exploration
        if random.random() < self.epsilon: 
            action = random.choice(actions)
            return action

        #greedy
        maxQ = -3
        action = None
        for a in actions:
            simulate = state.deepcopy()
            simulate, col = simulate.play(self.player.playerNo, a)
            if self.getQ(simulate) > maxQ:
                maxQ = self.getQ(simulate)
                action = a
        return action
    
    def updateTable(self, prevState, maxQ):
        #Updates values in the q-table by using the q-learning equation.

        if not prevState.getEmptyPositions():
            x = tuple(map(tuple, prevState.board))
            self.q[x] = self.getReward(prevState)

        else:
            x = tuple(map(tuple, prevState.board))
            self.q[x] = self.getQ(prevState) + self.alpha * ((self.getReward(prevState) + self.gamma * maxQ) - self.getQ(prevState))
            self.alpha = self.alpha/2
            # self.epsilon += 0.01

    def nextState(self, board):
        #Calls appropriate functions to return the next state of the board after playing a move.
        actions = board.getEmptyPositions()
        action = self.nextAction(board, actions)
        board, col = board.play(self.player.playerNo, action)
        x = tuple(map(tuple, board.board))
        return board, col


def trainQLearning(qlearn, player2, rows):
    #MCTS as Player 1, Qlearning as Player 2

    winners = {1: 0, 2: 0, 0: 0}

    while winners[2] <= 5000:

        n = random.randint(0, 25)
        player1 = Player(1, n) #MCTS Player
        mcts = MonteCarloTreeSearch(player1, 2)

        player1.opponent = player2
        player2.opponent = player1

        game = Board(rows, 5)
        prevState = game.deepcopy()

        while(True):
            #MCTS move
            nextnode = mcts.nextState(game)
            game = nextnode.board

            winner = game.checkWinner()
            if winner != -1:
                winners[winner] += 1
                if winner == 0:
                    x = tuple(map(tuple, prevState.board))
                    qlearn.q[x] = 0.5
                else:
                    x = tuple(map(tuple, prevState.board))
                    qlearn.q[x] = -2.0
                break
            
            #Q-learning move
            game, col = qlearn.nextState(game)
            winner = game.checkWinner()

            if winner != -1:
                winners[winner] += 1
                if winner == 0:
                    x = tuple(map(tuple, game.board))
                    qlearn.q[x] = 0.5
                else:
                    x = tuple(map(tuple, game.board))
                    qlearn.q[x] = 2.0
                qlearn.updateTable(prevState, qlearn.getQ(game))
                break

            qlearn.updateTable(prevState, qlearn.getQ(game))
            prevState = game.deepcopy()

    with open('my_file.csv', 'w') as f:
        [f.write('"{0}",{1}\n'.format(key, value)) for key, value in qlearn.q.items()]

def readValuesTrain(qlearn):

    with gzip.open('2019A7PS0063G_SHIKHA.dat.gz', 'rb') as f_in:
        with open('2019A7PS0063G_SHIKHA.dat', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    datContent = [i.strip().split('"') for i in open('2019A7PS0063G_SHIKHA.dat').readlines()]
    for x, key, value in datContent:
        key = tuple(int(num) for num in key.replace('(', '').replace(')', '').replace('...', '').split(', '))
        qlearn.q[key] = float(value[1:])

'''
Assignment Questions
'''
def partA():
    player1 = Player(1, 200)
    player2 = Player(2, 40)

    player1.opponent = player2
    player2.opponent = player1

    mcts1 = MonteCarloTreeSearch(player1)
    mcts2 = MonteCarloTreeSearch(player2)

    game = Board(6, 5)
    game.printBoard()

    moves = 0

    while(True):

        #MC200 move
        nextnode = mcts1.nextState(game)
        game = nextnode.board
        moves += 1

        print("Player 1 (MCTS 200)")
        print("Action selected:", nextnode.col)
        print('Total playouts for next state:', nextnode.playouts)
        print('Value of next state according to MCTS :', nextnode.wins/nextnode.playouts)
        game.printBoard()

        winner = game.checkWinner()
        if winner != -1:
            print("Player", winner, "won the game!")
            print("Total number of moves = ", moves)
            break
        
        #MC40 move
        nextnode = mcts2.nextState(game)
        game = nextnode.board
        moves += 1

        print("Player 2 (MCTS 40)")
        print("Action selected:", nextnode.col)
        print('Total playouts for next state:', nextnode.playouts)
        print('Value of next state according to MCTS :', nextnode.wins/nextnode.playouts)
        game.printBoard()

        winner = game.checkWinner()
        if winner != -1:
            print("Player", winner,"won the game!")
            print("Total number of moves = ", moves)
            break


def partC():

    print("MC25 vs Q-Learning in a 4 x 5 board of Connect 4. Let's go!")

    player1 = Player(1, 25)
    player2 = Player(2)

    player1.opponent = player2
    player2.opponent = player1

    mcts = MonteCarloTreeSearch(player1, 2)
    qlearn = QLearning(player2, epsilon=0, alpha=0.5, gamma=1)

    readValuesTrain(qlearn)

    game = Board(4, 5)
    game.printBoard()
    moves = 0

    prevState = game.deepcopy()
    while(True):

        #MCTS move
        nextnode = mcts.nextState(game)
        game = nextnode.board
        moves += 1

        print("Player 1 (MCTS 25)")
        print("Action selected:", nextnode.col)
        print('Total playouts for next state:', nextnode.playouts)
        print('Value of next state according to MCTS :', nextnode.wins/nextnode.playouts)
        game.printBoard()

        winner = game.checkWinner()
        if winner != -1:
            
            if winner == 0:
                x = tuple(map(tuple, prevState.board))
                qlearn.q[x] = 0.5
            else:
                x = tuple(map(tuple, prevState.board))
                qlearn.q[x] = -2.0

            print("Player", winner,"won the game!")
            print("Total number of moves = ", moves)
            break
        
        #Q-learning move
        game, col = qlearn.nextState(game)
        moves += 1

        print("Player 2 (Q Learning)")
        print("Action selected:", col)
        x = tuple(map(tuple, game.board))
        print('Value of next state according to Q-Learning :', qlearn.q[x])
        game.printBoard()

        winner = game.checkWinner()
        if winner != -1:
            if winner == 0:
                x = tuple(map(tuple, game.board))
                qlearn.q[x] = 0.5
            else:
                x = tuple(map(tuple, game.board))
                qlearn.q[x] = 2.0
            qlearn.updateTable(prevState, qlearn.getQ(game))

            print("Player", winner,"won the game!")
            print("Total number of moves = ", moves)
            break

        qlearn.updateTable(prevState, qlearn.getQ(game))
        prevState = game.deepcopy()



def main():

    print("Which game would you like to see?")
    print("1. MC200 vs MC40")
    print("2. MC25 vs Q-Learning")
    print("Enter option here.")

    n = int(input())

    if n == 1:
        partA()
    elif n == 2:
        partC()
    else:
        print("Please enter valid input.")
        exit()
    
    print("Hope you enjoyed!")
        
if __name__=='__main__':
    main()
