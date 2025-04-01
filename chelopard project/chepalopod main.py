import random

def generate_cephalopod_problem(filename="cephalopod_problem.pddl"):
    grid_size = 5
    players = ["human", "ai"]
    num_dice_per_player = 24  # Ogni giocatore ha 24 dadi disponibili
    
    # Creazione del file PDDL
    with open(filename, "w") as f:
        f.write("(define (problem cephalopod-instance)\n")
        f.write("  (:domain chephalopod_domain)\n")
        
        # Dichiarazione degli oggetti
        f.write("  (:objects\n")
        for x in range(grid_size):
            for y in range(grid_size):
                f.write(f"    cella-{x}-{y} - cella\n")
        for p in players:
            f.write(f"    {p} - giocatore\n")
        for i in range(num_dice_per_player):
            f.write(f"    dado-umano-{i} - dado\n")
            f.write(f"    dado-ai-{i} - dado\n")
        for v in range(1, 7):
            f.write(f"    valore-{v} - valore\n")
        f.write("  )\n")
        
        # Stato iniziale con scacchiera vuota
        f.write("  (:init\n")
        for x in range(grid_size):
            for y in range(grid_size):
                f.write(f"    (not (occupata cella-{x}-{y}))\n")
        f.write("    (turno human)\n")  # Il giocatore umano inizia sempre
        f.write("  )\n")
        
        # Obiettivo: almeno un dado sulla griglia alla fine
        f.write("  (:goal (exists (?c - cella) (occupata ?c)))\n")
        f.write(")\n")
    
    print(f"File {filename} generato con successo!")

# Implementazione dell'euristica Min-Max con Alpha-Beta Pruning
def evaluate_state(stato):
    """ Valuta lo stato attuale del gioco con una funzione più avanzata """
    punteggio = 0
    for cella, poss_dado in stato.items():
        if poss_dado == "ai":
           punteggio += 10  # Ogni dado IA sulla scacchiera vale 10 punti
           x, y = map(int, cella.split('-')[1:])
           if 1 <= x <= 3 and 1 <= y <= 3:  # Celle centrali
                score += 5  # Più punti per il controllo del centro
            # Controllo catture
           for cella_adiacente in get_adjacent_cells(cella):
                if stato.get(cella_adiacente) == "human":  # Se vicino c'è un dado avversario
                    score += 20  # Premia la possibilità di cattura
        elif poss_dado == "human":
            score -= 10  # Penalizza i dadi avversari sulla scacchiera
    return score

import random

def minimax(state, depth, alpha, beta, maximizing_player):
    """ Algoritmo Minimax con Alpha-Beta Pruning """
    
    # 1️⃣ Condizione di terminazione: fine gioco o profondità massima
    if depth == 0 or is_terminal(state):
        return evaluate_state(state), None

    best_move = None  

    if maximizing_player:  # 💡 Turno dell'IA (massimizza)
        max_eval = float('-inf')  
        
        for move in get_possible_moves(state, "ai"):
            new_state = apply_move(state, move, "ai")  # Simula la mossa
            
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, False)  # Turno umano
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Alpha-Beta Pruning

        return max_eval, best_move

    else:  # 🧑‍💻 Turno dell'umano (minimizza)
        min_eval = float('inf')
        
        for move in get_possible_moves(state, "human"):
            new_state = apply_move(state, move, "human")  # Simula la mossa

            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, True)  # Torna all'IA
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-Beta Pruning
        
        return min_eval, best_move


def is_terminal(stato):
    """ Controlla se lo stato è terminale (es. nessuna mossa possibile) """
    return not any(get_possible_moves(stato,"ai"))and not any(get_possible_moves(stato,"human"))

def get_possible_moves(stato, player):
    """ Restituisce tutte le mosse possibili per un giocatore """
    mosse = []
    for cell, occupata in stato.items():
        if not occupata:
            mosse.append(cell)
    return mosse

def apply_move(stato, move, player):
    """ Applica una mossa e cattura eventuali dadi avversari """
    new_state = stato.copy()
    new_state[move] = player

    # Controlla se ci sono dadi avversari catturabili
    for adj_cell in get_adjacent_cells(move):
        if stato.get(adj_cell) and stato[adj_cell] != player:
            if get_dice_value(move) >= get_dice_value(adj_cell):
                new_state[adj_cell] = player  # Cattura il dado avversario
    
    return new_state

def get_adjacent_cells(cella):
    """ Restituisce le celle adiacenti valide """
    x, y = map(int, cella.split('-')[1:])
    adiacenti = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: #verifica che vi siano delle celle a [nord sud est e ovest rispetto alla cella di cui vogliamo andare a verificare le adiacenza possibili]
        nx, ny = x + dx, y + dy #somma le coordinate alle nostre correnti in maniera iterativa
        if 0 <= nx < 5 and 0 <= ny < 5:# se la somma non da vita ad una cordianta il cui valore supera il numero di righe o colonne presenti all'interno della nostra scacchiera 
            adiacenti.append(f"cella-{nx}-{ny}")#aggiunta la cella all'array contenenti le celli adiacenti alla cella presa in esame e passata  come parametro della funzione 
    return adiacenti #ritorno l'array

def get_dice_value(stato, cella):
    """ Restituisce il valore effettivo del dado in una cella, se esiste """
    if cella in stato and stato[cella] is not None: #verifica che la cella esiste all'interno della schacchiera altrimenti si verifica un key-error se cosi fosse allora verifica ulteriormente che non sia vuota 
        return stato[cella]["valore"]  # Restituisce il valore effettivo del dado
    return None  # Nessun dado in quella cella


# Esegui lo script per generare il file problema
generate_cephalopod_problem()
