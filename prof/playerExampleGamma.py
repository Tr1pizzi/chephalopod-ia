import math
import itertools
import time
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
        actions = sorted(cal_actions(state), key=move_priority, reverse=True)

        v, move = -infinity, None
        for a in actions:
            v2, _ = min_value(result(state, a), alpha, beta, depth+1)
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

        actions = sorted(cal_actions(state), key=move_priority, reverse=True)
        for a in actions:
            v2, _ = max_value(result(state, a), alpha, beta, depth + 1)
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
    size = board_state.size
    board = board_state.board
    opponent = "Red" if player == "Blue" else "Blue"

    my_pieces = my_pips = op_pieces = op_pips = 0
    my_caps = op_caps = center_bonus = vulnerable = mobility = 0
    empty_cells = []
    adjacent_cache = {}  # cache per celle adiacenti

    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell is None:
                empty_cells.append((r, c))
            else:
                owner, pip = cell
                if owner == player:
                    my_pieces += 1
                    my_pips += pip
                else:
                    op_pieces += 1
                    op_pips += pip

                if 1 <= r < size - 1 and 1 <= c < size - 1:
                    center_bonus += 2 if owner == player else -2

                # Calcolo mobilità direttamente durante il primo passaggio
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] is None:
                        if owner == player:
                            mobility += 1

    # Catture potenziali
    for (r, c) in empty_cells:
        if (r, c) not in adjacent_cache:
            adjacent_cache[(r, c)] = get_adjacent_cells(r, c, size)
        adjacent = adjacent_cache[(r, c)]
        pairs = [(board[r2][c2], board[r3][c3])
                 for i in range(len(adjacent))
                 for j in range(i + 1, len(adjacent))
                 for (r2, c2), (r3, c3) in [(adjacent[i], adjacent[j])]]

        for a, b in pairs:
            if a and b:
                pip_sum = a[1] + b[1]
                if pip_sum <= 6:
                    if a[0] != player and b[0] != player:
                        my_caps += 1
                    if a[0] != opponent and b[0] != opponent:
                        op_caps += 1

    # Vulnerabilità: miei dadi adiacenti a coppie nemiche
    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell and cell[0] == player:
                if (r, c) not in adjacent_cache:
                    adjacent_cache[(r, c)] = get_adjacent_cells(r, c, size)
                enemies = [board[r2][c2] for (r2, c2) in adjacent_cache[(r, c)]
                           if board[r2][c2] and board[r2][c2][0] != player]
                for i in range(len(enemies)):
                    for j in range(i + 1, len(enemies)):
                        if enemies[i][1] + enemies[j][1] <= 6:
                            vulnerable += 1

    score = (
        10 * (my_pieces - op_pieces) +
        0.5 * (my_pips - op_pips) +
        center_bonus +
        6 * (my_caps - op_caps) +
        1 * mobility -
        3 * vulnerable
    )
    return score

def cal_actions(state):
    size = state.size
    board = state.board
    moves = []
    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    for r in range(size):
        for c in range(size):
            if board[r][c] is None:  # cella vuota
                adjacent = []
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        cell = board[nr][nc]
                        if cell is not None:
                            adjacent.append(((nr, nc), cell[1]))  # posizione + pip

                capture_moves = []
                if len(adjacent) >= 2:
                    for comb in itertools.combinations(adjacent, 2):
                        pip_sum = comb[0][1] + comb[1][1]
                        if 2 <= pip_sum <= 6:
                            positions = (comb[0][0], comb[1][0])
                            capture_moves.append(((r, c), pip_sum, positions))

                if capture_moves:
                    moves.extend(capture_moves)
                else:
                    moves.append(((r, c), 1, ()))  # mossa non catturante
    return moves
def result(state, move):
    (r, c), pip, captured = move
    new_board = [row[:] for row in state.board]
    new_board[r][c] = (state.to_move, pip)
    for (rr, cc) in captured:
        new_board[rr][cc] = None

    new_state = state.__class__(
        size=state.size,
        board=new_board,
        to_move="Red" if state.to_move == "Blue" else "Blue",
        last_move=((r, c), captured)
    )
    return new_state