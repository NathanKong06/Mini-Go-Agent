from copy import deepcopy

class GO:
    def __init__(self, n):
        """
        Go game.

        :param n: size of the board n*n
        """
        self.size = n
        #self.previous_board = None # Store the previous board
        self.X_move = True # X chess plays first
        self.died_pieces = [] # Intialize died pieces to be empty
        self.n_move = 0 # Trace the number of moves
        self.max_move = n * n - 1 # The max movement of a Go game
        self.komi = n/2 # Komi rule
        self.verbose = False # Verbose only when there is a manual player

    def init_board(self, n):
        '''
        Initialize a board with size n*n.

        :param n: width and height of the board.
        :return: None.
        '''
        board = [[0 for x in range(n)] for y in range(n)]  # Empty space marked as 0
        # 'X' pieces marked as 1
        # 'O' pieces marked as 2
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        '''
        Initialize board status.
        :param previous_board: previous board state.
        :param board: current board state.
        :return: None.
        '''

        # 'X' pieces marked as 1
        # 'O' pieces marked as 2

        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        # self.piece_type = piece_type
        self.previous_board = previous_board
        self.board = board

    def compare_board(self, board1, board2):
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        Detect all the neighbors of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        '''
        Detect the neighbor allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        '''
        Using DFS to search for all allies of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        '''
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_died_pieces(self, piece_type):
        '''
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        '''
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        '''
        Remove the stones of certain locations.

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        '''
        Place a chess stone in the board.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        # self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        self.n_move += 1
        return True

    def valid_place_check(self, i, j, piece_type, test_check=False):
        '''
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''   
        board = self.board
        verbose = self.verbose
        if test_check:
            verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(len(board) - 1))
            return False
        
        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False
        
        # Copy the board for testing
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        # If not, remove the died pieces of opponent and check again
        test_go.remove_died_pieces(3 - piece_type)
        if not test_go.find_liberty(i, j):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            if self.died_pieces and self.compare_board(self.previous_board, test_go.board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True
        
    def update_board(self, new_board):
        '''
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''   
        self.board = new_board

    def visualize_board(self):
        '''
        Visualize the board.

        :return: None
        '''
        board = self.board

        print('-' * len(board) * 2)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * len(board) * 2)

    def game_end(self, piece_type, action="MOVE"):
        '''
        Check if the game should end.

        :param piece_type: 1('X') or 2('O').
        :param action: "MOVE" or "PASS".
        :return: boolean indicating whether the game should end.
        '''

        # Case 1: max move reached
        if self.n_move >= self.max_move:
            return True
        # Case 2: two players all pass the move.
        if self.compare_board(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):
        '''
        Get score of a player by counting the number of stones.

        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the game should end.
        '''

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt          

    def judge_winner(self):
        '''
        Judge the winner of the game by number of pieces for each player.

        :param: None.
        :return: piece type of winner of the game (0 if it's a tie).
        '''        

        cnt_1 = self.score(1)
        cnt_2 = self.score(2)
        if cnt_1 > cnt_2 + self.komi: return 1
        elif cnt_1 < cnt_2 + self.komi: return 2
        else: return 0
        
    def check_corners_first(self,available_spots):
        if len(available_spots) == 0 or len(available_spots) == 1:
            return available_spots
        new_list = []
        corners = [(0,0),(0,4),(4,0),(4,4)]
        for corner in corners:
            if corner in available_spots:
                new_list.append(corner)
        for spot in available_spots:
            if spot not in corners:
                new_list.append(spot)
        return new_list

    def minimax_decision(self,piece_type, depth, alpha, beta):
        if self.game_end(piece_type):
            winner = self.judge_winner()
            if winner == 1: #Black wins
                return 100
            elif winner == 2: #White wins
                return -100
            elif winner == 0: #Tie
                return 0
        
        if piece_type == 1: #Black Maximizes
            value = -1000000 #Low initial value
            available_spots = [(i,j) for i in range (5) for j in range(5) if self.board[i][j] == 0] #Find all empty spots
            available_spots = self.check_corners_first(available_spots)
            for spot in available_spots:
                copy_self = self.copy_board() #Create copy at this moment
                if self.place_chess(spot[0],spot[1],1): #Place piece if legal
                    self.died_pieces = self.remove_died_pieces(3 - piece_type) #Remove all dead pieces from piece placement
                    value = max(value,self.minimax_decision(2,depth+1,alpha,beta)) #Find value of this move
                    self = copy_self #Undo the move by resetting state
                    alpha = max(alpha,value)
                    if alpha >= beta:
                        break
            copy_self = self.copy_board()
            value = max(value,self.minimax_decision(2,depth+1,alpha,beta)) #Find value from passing
            self = copy_self
            return value
        elif piece_type == 2:
            value = 1000000 #High intitial value
            available_spots = [(i,j) for i in range (5) for j in range(5) if self.board[i][j] == 0] #Find all empty spots
            available_spots = self.check_corners_first(available_spots)
            for spot in available_spots:
                copy_self = self.copy_board() #Create copy at this moment
                if self.place_chess(spot[0],spot[1],2): #Place piece if legal
                    self.died_pieces = self.remove_died_pieces(3 - piece_type) #Remove all dead pieces from piece placement
                    value = min(value,self.minimax_decision(1,depth+1,alpha,beta)) #Find value of this move
                    self = copy_self #Undo the move by resetting state
                    beta = min(beta,value)
                    if beta <= alpha:
                        break
            copy_self = self.copy_board()
            value = max(value,self.minimax_decision(2,depth+1,alpha,beta)) #Find value from passing
            self = copy_self
            return value
        else:
            print("Error")

    def minimax_move(self,piece_type):
        if piece_type == 1: #Black Maximizes
            best_value = -1000000 #Low intitial value
            best_move = None
            available_spots = [(i,j) for i in range (5) for j in range(5) if self.board[i][j] == 0] #Find all empty spots
            available_spots = self.check_corners_first(available_spots)
            for spot in available_spots: 
                copy_self = self.copy_board() #Create copy at this moment
                if self.place_chess(spot[0],spot[1],1): #Place piece if legal
                    self.died_pieces = self.remove_died_pieces(3 - piece_type) #Remove all dead pieces from piece placement
                    value = self.minimax_decision(piece_type,0,-1000000,1000000) #Find value of this move
                    self = copy_self #Undo the move by resetting state
                    if value > best_value: #Keep track of best move
                        best_value = value
                        best_move = spot
            copy_self = self.copy_board()
            value = self.minimax_decision(piece_type,0,-1000000,1000000)  #Find value from passing
            self = copy_self
            if value > best_value:
                return "PASS"
            return best_move
        elif piece_type == 2: #White Minimizes
            best_value = 1000000 #High intitial value
            best_move = None
            available_spots = [(i,j) for i in range (5) for j in range(5) if self.board[i][j] == 0] #Find all empty spots
            available_spots = self.check_corners_first(available_spots)
            for spot in available_spots:
                copy_self = self.copy_board()
                if self.place_chess(spot[0],spot[1],2): #Place piece if legal
                    self.died_pieces = self.remove_died_pieces(3 - piece_type) #Remove all dead pieces from piece placement
                    value = self.minimax_decision(piece_type,0,-1000000,1000000) #Find value of this move
                    self = copy_self #Undo the move by resetting state
                    if value < best_value: #Keep track of best move
                        best_value = value
                        best_move = spot
            copy_self = self.copy_board()
            value = self.minimax_decision(piece_type,0,-1000000,1000000) #Find value from passing
            self = copy_self
            if value < best_value:
                return "PASS"
            return best_move
        else:
            print("Error")

def read_input(n, path="init/input.txt"):

    with open(path, 'r') as f:
        lines = f.readlines()

        piece_type = int(lines[0])

        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]

        return piece_type, previous_board, board

def write_output(result, path="init/output.txt"):
    res = ""
    if result == "PASS":
        res = "PASS"
    else:
        res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)

def write_pass(path="init/output.txt"):
    with open(path, 'w') as f:
        f.write("PASS")

if __name__ == "__main__":
    N = 5
    go = GO(N)
    piece_type, previous_board, board = read_input(N) #Takes Input
    go.set_board(piece_type, previous_board, board)
    next_move = go.minimax_move(piece_type)
    if next_move != "PASS": #Writes Output
        write_output(next_move)
    else:
        write_pass()