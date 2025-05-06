import math
import multiprocessing
from multiprocessing import Manager
# The moves of player have the form (x,y), where y is the column number and x the row number (starting with 0)
infinity = math.inf

def playerStrategy(game, state):
    cutoff = 2
    manager = Manager()
    shared_cache = manager.dict()
    _, move = h_alphabeta_search(game, state, cutoff, shared_cache)
    return move

def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}
    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped
def max_value(game, state, alpha, beta, depth, cutoff, fi, cache):
    player = state.to_move
    key = (state, depth, "max")
    if key in cache:
        fi.send(cache[key])
        fi.close()
        return

    if game.is_terminal(state):
        val = game.utility(state, player)
        result = (val, None)
        cache[key] = result
        fi.send(result)
        fi.close()
        return

    if depth > cutoff:
        val = h(state, player)
        result = (val, None)
        cache[key] = result
        fi.send(result)
        fi.close()
        return

    best_val, best_move = -infinity, None
    children = []

    for a in game.actions(state):
        new_state = game.result(state, a)
        parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
        proc = multiprocessing.Process(
            target=min_value, args=(game, new_state, alpha, beta, depth + 1, cutoff, child_conn, cache)
        )
        proc.start()
        children.append((a, proc, parent_conn))

    for a, proc, conn in children:
        v, _ = conn.recv()
        conn.close()
        proc.join()
        if v > best_val:
            best_val, best_move = v, a
            alpha = max(alpha, best_val)
        if best_val >= beta:
            # Pruning: chiudi tutti i processi restanti
            for _, p2, _ in children:
                if p2.is_alive():
                    p2.terminate()
                p2.join()
            break

    result = (best_val, best_move)
    cache[key] = result
    fi.send(result)
    fi.close()

def min_value(game, state, alpha, beta, depth, cutoff, fi, cache):
    player = state.to_move
    key = (state, depth, "min")
    if key in cache:
        fi.send(cache[key])
        fi.close()
        return

    if game.is_terminal(state):
        val = game.utility(state, player)
        result = (val, None)
        cache[key] = result
        fi.send(result)
        fi.close()
        return

    if depth > cutoff:
        val = h(state, player)
        result = (val, None)
        cache[key] = result
        fi.send(result)
        fi.close()
        return

    best_val, best_move = +infinity, None
    children = []

    for a in game.actions(state):
        new_state = game.result(state, a)
        parent_conn, child_conn = multiprocessing.Pipe(duplex=False)
        proc = multiprocessing.Process(
            target=max_value, args=(game, new_state, alpha, beta, depth + 1, cutoff, child_conn, cache)
        )
        proc.start()
        children.append((a, proc, parent_conn))

    for a, proc, conn in children:
        v, _ = conn.recv()
        conn.close()
        proc.join()
        if v < best_val:
            best_val, best_move = v, a
            beta = min(beta, best_val)
        if best_val <= alpha:
            # Pruning: chiudi tutti i processi restanti
            for _, p2, _ in children:
                if p2.is_alive():
                    p2.terminate()
                p2.join()
            break

    result = (best_val, best_move)
    cache[key] = result
    fi.send(result)
    fi.close()
 

def h_alphabeta_search(game, state, cutoff, cache):
    pa, fi = multiprocessing.Pipe()
    process = multiprocessing.Process(target=max_value, args=(game, state, -infinity, +infinity, 0, cutoff, fi, cache))
    process.start()
    process.join()
    print("totale")
    v, move= pa.recv()
    return v, move

# Funzioni di utilità per il Cephalopod
def get_adjacent_cells(r, c):
    """
    Restituisce le celle adiacenti per una griglia 5x5 hardcoded.
    """
    adj = []
    # Controlla sopra, sotto, sinistra, destra
    if r > 0:  # sopra
        adj.append((r - 1, c))
    if r < 4:  # sotto
        adj.append((r + 1, c))
    if c > 0:  # sinistra
        adj.append((r, c - 1))
    if c < 4:  # destra
        adj.append((r, c + 1))
    return adj

    
# Esempio di integrazione in playingStrategies:
def h(board_state, player):
    """
    board_state: istanza di Board con attributi .board e .size
    player: "Blue" o "Red"
    """
    # Estrai la matrice grezza dal Board
    size = board_state.size
    board = board_state.board  # matrice size×size di None o (owner, pip)
    """
    board: matrice size x size con None o dict {'owner': "Blue"/"Red", 'pip': int}
    player: "Blue" o "Red"
    """
    opponent = "Red" if player == "Blue" else "Blue"
    my_caps = op_caps = center_bonus = my_pieces = my_pips = op_pieces = op_pips = 0
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
        adjacent = get_adjacent_cells(r, c)
        for (r2, c2) in adjacent:
            for (r3, c3) in adjacent:
                if (r2, c2) < (r3, c3):
                    a = board[r2][c2]
                    b = board[r3][c3]
                    if a and b:
                        if a[0] != player and b[0] != player and a[1] + b[1] <= 6:
                            my_caps += 1
                        if a[0] != opponent and b[0] != opponent and a[1] + b[1] <= 6:
                            op_caps += 1
    score = (
        10 * (my_pieces - op_pieces) +
         1 * (my_pips   - op_pips) +
        center_bonus +
         5 * (my_caps - op_caps)
    )
    return score