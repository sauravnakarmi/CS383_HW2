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
        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf

        if state.is_full():
            best_util = state.score()
            return best_util

        for move, state in state.successors():
            # print(move, state)
            util = self.minimax(state, None)
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

        # print("depth: ", depth)
        # print(state)

        """Determine the heuristically estimated minimax utility value of the given state.

        Args:
            state: a connect383.GameState object representing the current board
            depth: the maximum depth of the game tree that minimax should traverse before
                estimating the utility using the evaluation() function.  If depth is 0, no
                traversal is performed, and minimax returns the results of a call to evaluation().
                If depth is None, the entire game tree is traversed.

        Returns: the minimax utility value of the state
        """

        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf

        if state.is_full():
            best_util = state.score()
            # print("full")
            return best_util

        if depth == 0:
            best_util = self.evaluation(state)
            return best_util

        for move, state in state.successors():
            if depth is None:
                depth = None
                util = self.minimax(state, depth)
            else:
                util = self.minimax(state, depth-1)

            if nextp == 1:
                best_util = max(best_util, util)
            elif nextp == -1:
                best_util = min(best_util, util)

        # depth should only be decremented after all children are explored for a given state

        return best_util

    def evaluation(self, state):
        """Estimate the utility value of the game state based on features.

        N.B.: This method must run in O(1) time!

        Args:
            state: a connect383.GameState object representing the current board

        Returns: a heusristic estimate of the utility value of the state
        """
        # print("in eval function:")
        # print(state)

        p1_score = 0
        p2_score = 0

        for run in state.get_all_rows() + state.get_all_cols() + state.get_all_diags():
            # print("run",run)
            # if '0, 1' in str(run):  # checks for ' , x'
            #     print('0, 1')
            #     p1_score += 1
            # if '1, 0' in str(run):  # checks for 'x,  '
            #     print('1, 0')
            #     p1_score += 1
            # if '0, -1' in str(run):  # checks for ' , o'
            #     print('0, -1')
            #     p2_score += 1
            # if '-1, 0' in str(run):  # checks for 'o,  '
            #     print('-1, 0')
            #     p2_score += 1
            for elt, length, score in streaks_eval(run):
                if elt == 1:
                    p1_score += score
                if elt == -1:
                    p2_score += score
                if (elt == 1) and (length >= 3):
                    p1_score += length ** 2
                elif (elt == 1) and (length == 2):
                    p1_score += 5
                elif (elt == -1) and (length >= 3):
                    p2_score += length ** 2
                elif (elt == -1) and (length == 2):
                    p2_score += 5

        # print("p1_score :",p1_score)
        # print("p2_score :", p2_score)

        return p1_score - p2_score  # subtract util scores to determine util


def streaks_eval(lst):
    """Return the lengths of all the streaks of the same element in a sequence."""
    rets = []  # list of (element, length) tuples
    prev = lst[0]
    curr_len = 1
    score = 0
    for curr in lst[1:]:
        if curr == prev:
            curr_len += 1
        else:
            if curr == 0:
                score = curr_len * 5
            rets.append((prev, curr_len, score))
            prev = curr
            curr_len = 1
            score = 0
    rets.append((prev, curr_len, score))
    return rets


class PruneAgent(HeuristicAgent):
    """Smarter computer agent that uses minimax with alpha-beta pruning to select the best move."""

    def minimax(self, state, depth):
        return self.minimax_prune(state, depth)

    def minimax_prune(self, state, depth):

        # print("depth: ", depth)
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

        nextp = state.next_player()
        best_util = -math.inf if nextp == 1 else math.inf

        if state.is_full():
            best_util = state.score()
            return best_util

        # print("state :", state)
        if depth == 0 and depth is not None:
            # print("depth :", depth)
            best_util = HeuristicAgent.evaluation(self, state)
            return best_util

        for move, state in state.successors():
            if depth is None:
                depth = None
                util = self.minimax(state, depth)
            else:
                util = self.minimax(state, depth - 1)

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
            if nextp == 1:
                best_util = max(best_util, util)
            elif nextp == -1:
                best_util = min(best_util, util)

        return best_util
