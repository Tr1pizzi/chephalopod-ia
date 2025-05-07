import math
# The moves of player have the form (x,y), where y is the column number and x the row number (starting with 0)
infinity = math.inf
def playerStrategy(game, state):
    # Conta quante pedine sono presenti sulla board
    pieces_on_board = sum(1 for row in state.board for cell in row if cell is not None)
    # Cutoff dinamico in base alla densità della board
    if pieces_on_board < 17:
        depth = 4  # early game
    elif pieces_on_board < 19:
        depth = 5  # mid game
    elif pieces_on_board < 22:
        depth = 6  # mid game
    else:
        depth = 8  # late game

    # Chiamata all'alpha-beta search
    value, move = h_alphabeta_search(game, state, cutoff_depth(depth))
    return move

def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}
    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped

def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d

def h_alphabeta_search(game, state, cutoff=cutoff_depth(4)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache1
    def max_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player), None
        
        def move_priority(a):
            (r, c), pip, captured = a
            center_bonus = (1 <= r < 4 and 1 <= c < 4)
            return len(captured) * 10 + center_bonus
        actions = sorted(game.actions(state), key=move_priority, reverse=True)

        v, move = -infinity, None
        for a in actions:
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
        def move_priority(a):
            (r, c), pip, captured = a
            center_bonus = (1 <= r < 4 and 1 <= c < 4)
            return len(captured) * 10 + center_bonus

        actions = sorted(game.actions(state), key=move_priority, reverse=True)
        for a in actions:
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)

# Funzioni di utilità per il Cephalopod
def get_adjacent_cells(r, c, size=5):
    adj = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            adj.append((nr, nc))
    return adj

    
# Esempio di integrazione in playingStrategies:
def h(board_state, player):
    # Estrai la matrice grezza dal Board
    size = board_state.size
    board = board_state.board  # matrice size×size di None o (owner, pip)
    opponent = "Red" if player == "Blue" else "Blue"
    
    my_caps = op_caps = center_bonus = my_pieces = my_pips = op_pieces = op_pips = my_6 = op_6 = 0
    empty_cells = []
    # Converti in formato atteso da evaluate_state / Differenza pezzi e somma pip
    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell is None:
                empty_cells.append((r,c))
            else:
                """"
                valutazione in base ai pezzi
                """
                if cell[0] == player:
                    my_pieces += 1
                    my_pips   += cell[1]
                else:
                    op_pieces += 1
                    op_pips   += cell[1]

                """"
                controllo centro
                """
                if 1 <= r < size - 1 and 1 <= c < size - 1:
                    center_bonus +=  2 if cell[0] == player else -2

                """"
                cattura
                """
    
    for (r, c) in empty_cells:
        adjacent = get_adjacent_cells(r, c, size)
        for (r2, c2) in adjacent:
            for (r3, c3) in adjacent:
                if (r2, c2) < (r3, c3):
                    a = board[r2][c2]
                    b = board[r3][c3]
                    if a and b and a[0] != player and b[0] != player:
                        val = a[1] + b[1]
                        if val <= 6:
                            my_caps+=1
                            if val == 6:
                                my_6 += 1
                    if a and b and a[0] != opponent and b[0] != opponent:
                        val = a[1] + b[1]
                        if val <= 6:
                            op_caps+=1
                            if val == 6:
                                op_6 += 1

    score = (
        10 * (my_pieces - op_pieces) +
         3 * (my_pips   - op_pips) +
        center_bonus +
         5 * (my_caps - op_caps)+ 
         5 * (my_6-op_6)

    )
    return score