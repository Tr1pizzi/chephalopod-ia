import math

def minimax_search(game, state):
    """Search game tree to determine best move; return (value, move) pair."""

    player = state.to_move

    def max_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        return v, move

    return max_value(state)

infinity = math.inf

def alphabeta_search(game, state):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    def max_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity)



def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}
    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped


def alphabeta_search_tt(game, state):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache1
    def max_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache1
    def min_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity)

def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d

def h_alphabeta_search(game, state, cutoff=cutoff_depth(2)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache1
    def max_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth+1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache1
    def min_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)

import math

# Funzioni di utilità per il Cephalopod
def get_adjacent_cells(r, c, size=5):
    adj = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            adj.append((nr, nc))
    return adj

def all_empty_cells(board, size=5):
    empties = []
    for r in range(size):
        for c in range(size):
            if board[r][c] is None:
                empties.append((r, c))
    return empties

# Euristica avanzata per Cephalopod
def evaluate_state(board, player):
    """
    board: matrice size x size con None o dict {'owner': "Blue"/"Red", 'pip': int}
    player: "Blue" o "Red"
    """
    opponent = "Red" if player == "Blue" else "Blue"
    score = 0
    size = len(board)

    # 1) Differenza pezzi e somma pip
    my_pieces = my_pips = 0
    op_pieces = op_pips = 0
    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell:
                if cell['owner'] == player:
                    my_pieces += 1
                    my_pips   += cell['pip']
                else:
                    op_pieces += 1
                    op_pips   += cell['pip']
    score += 10 * (my_pieces - op_pieces)
    score +=  1 * (my_pips   - op_pips)

    # 2) Controllo centro
    center_bonus = 0
    centers = [(i, j) for i in range(1, size-1) for j in range(1, size-1)]
    for r, c in centers:
        cell = board[r][c]
        if cell:
            center_bonus +=  2 if cell['owner'] == player else -2
    score += center_bonus

    # 3) Potenziale di cattura
    def can_capture(r, c, plyr):
        adjacent = get_adjacent_cells(r, c, size)
        for (r2, c2) in adjacent:
            for (r3, c3) in adjacent:
                if (r2, c2) < (r3, c3):
                    a = board[r2][c2]
                    b = board[r3][c3]
                    if a and b and a['owner'] != plyr and b['owner'] != plyr:
                        if a['pip'] + b['pip'] <= 6:
                            return True
        return False

    my_caps = sum(1 for (r, c) in all_empty_cells(board, size)
                  if can_capture(r, c, player))
    op_caps = sum(1 for (r, c) in all_empty_cells(board, size)
                  if can_capture(r, c, opponent))
    score += 5 * (my_caps - op_caps)

    return score

# Esempio di integrazione in playingStrategies:
def h(board_state, player):
    """
    board_state: istanza di Board con attributi .board e .size
    player: "Blue" o "Red"
    """
    # Estrai la matrice grezza dal Board
    size = board_state.size
    raw_board = board_state.board  # matrice size×size di None o (owner, pip)

    # Converti in formato atteso da evaluate_state
    board = [[None] * size for _ in range(size)]
    for r in range(size):
        for c in range(size):
            cell = raw_board[r][c]
            if cell is not None:
                owner, pip = cell
                board[r][c] = {'owner': owner, 'pip': pip}

    # Valuta lo stato convertito
    return evaluate_state(board, player)