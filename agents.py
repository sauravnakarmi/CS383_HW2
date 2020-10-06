import random
import math


BOT_NAME = "INSERT NAME FOR YOUR BOT HERE"

class Node:
    def __init__(self, depth):
        self.depth = depth


class RandomAgent:
    """Agent that picks a random available move.  You should be able to beat it."""
    def get_move(self, state, depth=None):
        return random.choice(state.successors())


class HumanAgent:
    """Prompts user to supply a valid move."""
    def get_move(self, state, depth=None):
        move__state = dict(state.successors())
        prompt = "Kindly enter your move {}: ".format(sorted(move__state.keys()))
        move = None
        while move not in move__state:
            try:
                move = int(input(prompt))
            except ValueError:
                continue
        return move, move__state[move]


class MinimaxAgent:
    """Artificially intelligent agent that uses minimax to optimally select the best move."""

    def get_move(self, state, depth=None):
        """Select the best available move, based on minimax value."""
        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf
        best_move = None
        best_state = None

        for move, state in state.successors():
            util = self.minimax(state, depth)
            if ((nextp == 1) and (util > best_util)) or ((nextp == -1) and (util < best_util)):
                best_util, best_move, best_state = util, move, state
        return best_move, best_state

    def minimax(self, state, depth):
        """Determine the minimax utility value of the given state.

        Args:
            state: a connect383.GameState object representing the current board
            depth: for this agent, the depth argument should be ignored!

        Returns: the exact minimax utility value of the state
        """
        """Determine the minimax utility value of the given state.

                Args:
                    state: a connect383.GameState object representing the current board
                    depth: for this agent, the depth argument should be ignored!

                Returns: the exact minimax utility value of the state
                """
        succs = state.successors
        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf

        if state.is_full():
            best_util = state.score()
            return best_util

        for move, board in succs():
            util = self.minimax(board, None)
            if nextp == 1:
                best_util = max(best_util, util)
            elif nextp == -1:
                best_util = min(best_util, util)
        # print(best_util)
        return best_util


class HeuristicAgent(MinimaxAgent):
    """Artificially intelligent agent that uses depth-limited minimax to select the best move."""

    def minimax(self, state, depth):
        return self.minimax_depth(state, depth)

    def minimax_depth(self, state, depth):

        print("depth: ", depth)


        """Determine the heuristically estimated minimax utility value of the given state.

        Args:
            state: a connect383.GameState object representing the current board
            depth: the maximum depth of the game tree that minimax should traverse before
                estimating the utility using the evaluation() function.  If depth is 0, no
                traversal is performed, and minimax returns the results of a call to evaluation().
                If depth is None, the entire game tree is traversed.

        Returns: the minimax utility value of the state
        """
        arr = []
        succs = state.successors
        # print(type(succs()))
        # arr.append(succs())
        # print(arr)

        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf

        if depth == 0:
            best_util = self.evaluation(state)
            return best_util

        if state.is_full():
            best_util = state.score()
            print("full")
            return best_util

        # print("successors: ")
        # for i in succs():
        #     print(i)
        # print("Len: ", len(succs()))
        # print("")
        for move, board in succs():
            util = self.minimax(board, depth-1)
            if nextp == 1:
                best_util = max(best_util, util)
            elif nextp == -1:
                best_util = min(best_util, util)

        # depth should only be decremented after all children are explored for a given state
        # print("depth: ", depth)
        # if depth != 0:
        #     depth = depth - 1

        return best_util

    def evaluation(self, state):
        """Estimate the utility value of the game state based on features.

        N.B.: This method must run in O(1) time!

        Args:
            state: a connect383.GameState object representing the current board

        Returns: a heusristic estimate of the utility value of the state
        """
        print("in eval function:")
        # print(state)
        nextp = state.next_player()
        # list of lists
        all_diags = state.get_all_diags()
        # generates a new state so wont work
        new_diags = [[elem if elem != 0 else 1 for elem in row] for row in all_diags]

        # counts the streak number not faster than score
        p1_score = 0
        p2_score = 0
        for run in state.get_all_rows() + state.get_all_cols() + state.get_all_diags():
            for elt, length in streaks(run):
                if (elt == 1) and (length >= 2):
                    p1_score += 1
                elif (elt == -1) and (length >= 2):
                    p2_score += 1
        return p1_score - p2_score

        # **** count the number of open spaces next to a x or an o

# prints length of streaks
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

class PruneAgent(HeuristicAgent):
    """Smarter computer agent that uses minimax with alpha-beta pruning to select the best move."""

    def minimax(self, state, depth):
        return self.minimax_prune(state, depth)

    def minimax_prune(self, state, depth):
        """Determine the minimax utility value the given state using alpha-beta pruning.

        The value should be equal to the one determined by ComputerAgent.minimax(), but the
        algorithm should do less work.  You can check this by inspecting the class variables
        GameState.p1_state_count and GameState.p2_state_count, which keep track of how many
        GameState objects were created over time.

        N.B.: When exploring the game tree and expanding nodes, you must consider the child nodes
        in the order that they are returned by GameState.successors().  That is, you cannot prune
        the state reached by moving to column 4 before you've explored the state reached by a move
        to to column 1.

        Args: see ComputerDepthLimitAgent.minimax() above

        Returns: the minimax utility value of the state
        """

        alpha = -math.inf  # setting alpha to worst possible case for maximizer
        beta = math.inf  # setting beta to worst possible case for minimizer

        succ = state.successors()
        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf

        if state.is_full():
            best_util = state.score()
            return best_util

        for move, board in succ:
            util = self.minimax(board, None)

            # pruning
            if nextp == -1 and util < alpha:
                return util
            if nextp == 1 and util > beta:
                return util

            # setting alpha and beta
            if nextp == -1 and util > alpha:
                alpha = util
            if nextp == 1 and util < beta:
                beta = util

            # minimax
            if (nextp == 1) and (util > best_util):
                best_util = max(best_util, util)
            elif (nextp == -1) and (util < best_util):
                best_util = min(best_util, util)

        return best_util