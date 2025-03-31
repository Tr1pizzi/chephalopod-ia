import random

def generate_cephalopod_problem(filename="cephalopod_problem.pddl"):
    grid_size = 5
    players = ["umano", "avversario AI"]
    num_dice_per_player = 3  # Ogni giocatore parte con 3 dadi
    
    # Inizializza la griglia con dadi assegnati ai due giocatori
    posizione_dadi = {}
    for player in players:
        for _ in range(num_dice_per_player):
            x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
            while (x, y) in posizione_dadi:  # Evita celle duplicate
                x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
            posizione_dadi[(x, y)] = (random.randint(1, 6), player)
    
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
        for (x, y) in posizione_dadi:
            f.write(f"    dado-{x}-{y} - dado\n")
        for v in range(1, 7):
            f.write(f"    valore-{v} - valore\n")
        f.write("  )\n")
        
        # Stato iniziale
        f.write("  (:init\n")
        for (x, y), (value, owner) in posizione_dadi.items():
            f.write(f"    (occupata cella-{x}-{y})\n")
            f.write(f"    (dado_appartiene_a dado-{x}-{y} {owner})\n")
            f.write(f"    (valore_dado dado-{x}-{y} valore-{value})\n")
        f.write("    (turno umano)\n")  # Il giocatore umano inizia sempre
        f.write("  )\n")
        
        # Obiettivo: almeno un dado sulla griglia alla fine
        f.write("  (:goal (exists (?c - cella) (occupata ?c)))\n")
        f.write(")\n")
    
    print(f"File {filename} generato con successo!")

# Esegui lo script per generare il file problema
generate_cephalopod_problem()
