import sys
import argparse
from agents import RandomAgent, HumanAgent, MinimaxAgent, HeuristicAgent, PruneAgent
import test_boards


class GameState:
    """Class representing a single state of a Connect4-esque game.

    For details on the game, see: https://en.wikipedia.org/wiki/Connect_Four

    Once created, a game state object should usually not be modified; instead, use the successors()
    function to generate reachable states.

    The board is stored as a 2D list, containing 1's representing Player 1's pieces and -1's
    for Player 2 (unused spaces are 0).
    """
    
    state_count = 0  # bookkeeping to help track how efficient agents' search methods are running
    
    def __init__(self, nrows=6, ncols=7):
        """Constructor for Connect4 state.

        Args:
            nrows: number of rows in the board
            ncols: number of columns in the board
            nwin: the number of tokens each player must get in a row to win
        """
        self.num_rows = nrows
        self.num_cols = ncols
        self.board = [ [ 0 for x in range(ncols) ] for y in range(nrows) ]

    def copy(self):
        """Create a duplicate of this game state."""
        clone = GameState(self.num_rows, self.num_cols)
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                clone.board[r][c] = self.board[r][c]
        return clone

    def next_player(self):
        """Determines who's move it is based on the board state.

        Returns: 1 if Player 1 goes next, -1 if it's Player 2's turn
        """
        return 1 if sum(sum(self.board, [])) == 0 else -1  # 1 for Player 1, -1 for Player 2

    def create_successor(self, col):
        """Create the successor state that follows from a given move."""
        player = self.next_player()
        successor = self.copy()
        row = 0
        while (successor.board[row][col] != 0) and (row < successor.num_rows-1):
            row += 1
        successor.board[row][col] = player
        GameState.state_count += 1  # bookkeeping, 
        return successor

    def successors(self):
        """Generates successor state objects for all valid moves from this board.

        Returns: a _sorted_ list of (move, state) tuples
        """
        move_states = []
        for col in range(self.num_cols):
            if self.board[self.num_rows-1][col] == 0:
                move_states.append((col, self.create_successor(col)))        
        return move_states

    # These accessor methods might be useful for calculation an agent's evaluation method!

    def get_row(self, r):
        """Gets the current values for any row in the board."""
        return self.board[r]

    def get_col(self, c):
        """Gets the current values for any column in the board as a list."""
        return [ self.board[r][c] for r in range(self.num_rows) ]
        
    def get_cell(self, r, c):
        """Gets the current value for any cell in the board as a list."""
        return self.board[r][c]

    def get_diags(self, cross_r, cross_c):
        """Returns the values for the diagonals crossing at any particular cell as two lists."""
        diag_up = []
        diag_down = []
        for c in range(self.num_cols):
            # "up" diagonal
            r = cross_r - (cross_c - c)
            if (0 <= r) and (r < self.num_rows):
                diag_up.append(self.board[r][c]) 

            # "down" diagonal
            r = cross_r + (cross_c - c)
            if (0 <= r) and (r < self.num_rows):
                diag_down.append(self.board[r][c]) 
        return diag_up, diag_down

    # Below are based on:
    # https://stackoverflow.com/questions/6313308/get-all-the-diagonals-in-a-matrix-list-of-lists-in-python
    
    def get_all_rows(self):
        """Return a list of rows for the board."""
        return [[c for c in r] for r in self.board]

    def get_all_cols(self):
        """Return a list of columns for the board."""
        return list(zip(*self.board))

    def get_all_diags(self):
        """Return a list of all the diagonals for the board."""
        b = [None] * (len(self.board) - 1)
        grid_forward = [b[i:] + r + b[:i] for i, r in enumerate(self.get_all_rows())]
        forwards = [[c for c in r if c is not None] for r in zip(*grid_forward)]
        grid_back = [b[:i] + r + b[i:] for i, r in enumerate(self.get_all_rows())]
        backs = [[c for c in r if c is not None] for r in zip(*grid_back)]
        return forwards + backs

    def score(self):
        """Calculate the score for each player.
        
        Players are awarded points for each streak (horizontal, vertical, or diagonal) of length 3
        or greater equal to the square of the length (e.g., 4-in-a-row scores 16 points).        
        """
        p1_score = 0
        p2_score = 0
        for run in self.get_all_rows() + self.get_all_cols() + self.get_all_diags():
            for elt, length in streaks(run):
                if (elt == 1) and (length >= 3):
                    p1_score += length**2
                elif (elt == -1) and (length >= 3):
                    p2_score += length**2
        return p1_score - p2_score

    def is_full(self):
        """Checks to see if there are available moves left."""
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.board[r][c] == 0:
                    return False
        return True

    def winner(self):
        s = self.score()

        if s == 0:
            return s
        else:
            return s/abs(s)
   

    def __str__(self):
        symbols = { -1: "O", 1: "X", 0: "-" }
        s = ""
        for r in range(self.num_rows-1, -1, -1):
            s += "\n"
            for c in range(self.num_cols):
                s += "  " + symbols[self.board[r][c]]

        s += "\n  " + "." * (self.num_cols * 3 - 2) + "\n"
        for c in range(self.num_cols):
            s += "  " + str(c)
        s += "\n"
        return s


def streaks(lst):
    """Return the lengths of all the streaks of the same element in a sequence."""
    rets = []  # list of (element, length) tuples
    prev = lst[0]
    curr_len = 1
    for curr in lst[1:]:
        if curr == prev:
            curr_len += 1
        else:
            rets.append((prev, curr_len))
            prev = curr
            curr_len = 1
    rets.append((prev, curr_len))
    return rets


def play_game(player1, player2, state, depth=None):
    """Run a Connect383 game.

    Player objects can be of any class that defines a get_move(state, depth) method that returns
    a move, state tuple.
    """
    print(state)

    turn = 0
    score = 0
    p1_state_count, p2_state_count = 0, 0
    state_count_prev = 0
    while not state.is_full():
        player_next = player1 if state.next_player() == 1 else player2
        move, state = player_next.get_move(state, depth)
        print("Turn {}: Player {} moves {}".format(turn, 1 if state.next_player() == -1 else 2, move))
        print(state)
        score = state.score()
        print("Current score is:", score)

        new_states_created = GameState.state_count - state_count_prev
        if state.next_player() == -1:  # "reversed" since the state has been overwritten above!
            p1_state_count += new_states_created
        else:
            p2_state_count += new_states_created        
        state_count_prev = GameState.state_count

        turn += 1

    score = state.score()
    if score == 0:
        print("It's a tie.")
    elif score >= 1:
        print("Player 1 wins! By", score, "points")
    elif score <= -1:
        print("Player 2 wins! By", -score, "points")
    print("Player 1 generated {} states".format(p1_state_count))
    print("Player 2 generated {} states".format(p2_state_count))

    return score


#############################################

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('p1', choices=['r','h','c','p'])
    parser.add_argument('p2', choices=['r','h','c','p'])
    parser.add_argument('nrows', type=int)
    parser.add_argument('ncols', type=int)
    parser.add_argument('--depth', type=int, nargs=1)
    parser.add_argument('--board', choices=test_boards.boards.keys(), nargs=1)
    args = parser.parse_args()

    agent_codes = { 'r': RandomAgent,
                    'h': HumanAgent,
                    'c': MinimaxAgent,
                    'p': PruneAgent }

    if args.depth:  # if we gave it a depth limit, switch the the heuristic agent
        agent_codes['c'] = HeuristicAgent
        args.depth = args.depth[0]

    play1 = agent_codes[args.p1]()
    play2 = agent_codes[args.p2]()

    if args.board:
        board = list(test_boards.boards[args.board[0]])
        start_state = GameState(len(board), len(board[0]))
        start_state.board = board
    else:
        start_state = GameState(args.nrows, args.ncols)

    play_game(play1, play2, start_state, args.depth)

