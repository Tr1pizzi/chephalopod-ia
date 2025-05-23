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

    
def h(board_state, player):
    size     = board_state.size
    board    = board_state.board
    opponent = "Red" if player == "Blue" else "Blue"

    # conteggi base
    my_pieces = my_pips = op_pieces = op_pips = 0
    my_caps = op_caps = my_6 = op_6 = 0
    center_bonus = mobility = opp_mob = vulnerable = 0
    empty_cells  = []

    dirs = ((1,0), (-1,0), (0,1), (0,-1))

    # ---------- prima scansione ----------
    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell is None:
                empty_cells.append((r, c))
                continue

            owner, pip = cell
            if owner == player:
                my_pieces += 1
                my_pips   += pip
            else:
                op_pieces += 1
                op_pips   += pip

            if 1 <= r < size-1 and 1 <= c < size-1:
                center_bonus += 2 if owner == player else -2

            # mobilità
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and board[nr][nc] is None:
                    if owner == player:
                        mobility += 1
                    else:
                        opp_mob  += 1

    # ---------- catture potenziali da celle vuote ----------
    for (r, c) in empty_cells:
        adj = [board[r+dr][c+dc] for dr, dc in dirs
               if 0 <= r+dr < size and 0 <= c+dc < size and board[r+dr][c+dc]]

        for i in range(len(adj)):
            ai = adj[i]
            for j in range(i+1, len(adj)):
                aj = adj[j]
                ps = ai[1] + aj[1]
                if ps > 6:
                    continue

                if   ai[0] == aj[0] == player:   # mia cattura
                    my_caps += 1
                    if ps == 6: my_6 += 1
                elif ai[0] == aj[0] == opponent: # cattura avversaria
                    op_caps += 1
                    if ps == 6: op_6 += 1

    # ---------- vulnerabilità rapida ----------
    # se un mio dado ha ≥2 adiacenti avversari con somma ≤6 è vulnerabile
    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            if cell and cell[0] == player:
                enemy_vals = [board[r+dr][c+dc][1]
                              for dr, dc in dirs
                              if 0 <= r+dr < size and 0 <= c+dc < size and
                                 board[r+dr][c+dc] and board[r+dr][c+dc][0] == opponent]
                if len(enemy_vals) >= 2:
                    enemy_vals.sort()
                    if enemy_vals[0] + enemy_vals[1] <= 6:
                        vulnerable += 1

    # ---------- funzione di valutazione ----------
    score = (
              10 * (my_pieces - op_pieces) +
      3 * (my_pips   - op_pips)   +
     center_bonus                 +
      8 * (my_caps - op_caps)     +   
     13 * (my_6   - op_6)         +  
      3 * (mobility - opp_mob)    +   
     -4 * vulnerable                  
    )
    return score
