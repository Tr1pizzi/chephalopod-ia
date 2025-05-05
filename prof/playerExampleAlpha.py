import math
import multiprocessing
from functools import partial
# The moves of player have the form (x,y), where y is the column number and x the row number (starting with 0)
infinity = math.inf

def playerStrategy(game, state):
    cutoff = 4
    _, move = h_alphabeta_search(game, state, cutoff)
    return move

def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}
    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]
    return wrapped

def max_value(game, state, alpha, beta, depth, cutoff, fi):
    player = state.to_move
    if game.is_terminal(state):
        fi.send((game.utility(state, player), None))
        fi.close()
        return
    print(depth)
    if depth>cutoff:
        fi.send((h(state, player), None))
        fi.close()
        return 
    v, move = -infinity, None
    for a in game.actions(state):
        new_state = game.result(state, a) 
        pa1, fi1 = multiprocessing.Pipe()
        process = multiprocessing.Process(target=min_value, args=(game, new_state, alpha, beta, depth + 1, cutoff, fi1))
        process.start()
        process.join()
        v2, _ = pa1.recv()
        print("ricevuto")
        print(a)
        print(depth)
        if v2 > v:
            v, move = v2, a
            alpha = max(alpha, v)
        if v >= beta:
            fi.send((v, move))
            fi.close()
            return 
    fi.send((v, move))
    fi.close()
    return 


def min_value(game, state, alpha, beta, depth, cutoff, fi):
    player = state.to_move
    if game.is_terminal(state):
        fi.send((game.utility(state, player), None))
        fi.close()
        return
    if depth>cutoff:
        fi.send((h(state, player), None))
        fi.close()
        return 
    v, move = +infinity, None
    for a in game.actions(state):
        new_state = game.result(state, a)
        pa1, fi1 = multiprocessing.Pipe()
        process = multiprocessing.Process(target=max_value, args=(game, new_state, alpha, beta, depth + 1, cutoff, fi1))
        process.start()
        process.join()
        v2, _ = pa1.recv()
        print("ricevuto")
        print(a)
        print(depth)
        if v2 < v:
            v, move = v2, a
            beta = min(beta, v)
        if v <= alpha:
            fi.send((v, move))
            fi.close()
            return 
    fi.send((v, move))
    fi.close()
    return 

def h_alphabeta_search(game, state, cutoff):
    pa, fi = multiprocessing.Pipe()
    print(0)
    process = multiprocessing.Process(target=max_value, args=(game, state, -infinity, +infinity, 0, cutoff, fi))
    process.start()
    process.join()
    v, move= pa.recv()
    print("ricevuto finale")
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