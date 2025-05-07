import time
import random
from CephalopodGame import CephalopodGame
import playerExampleAlpha
import playerExampleGamma

def test_ai_vs_ai_random_choice():
    game = CephalopodGame(size=5, first_player="Blue")
    state = game.initial

    print("Inizio partita di test tra Alpha e Beta (scelta casuale ogni turno)\n")

    while not game.is_terminal(state):
        current_player = state.to_move
        print(f"\n--- Turno di {current_player} ---")

        # Alpha move
        start_alpha = time.time()
        move_alpha = playerExampleAlpha.playerStrategy(game, state)
        time_alpha = time.time() - start_alpha
        print(f"Alpha suggerisce: {move_alpha} (tempo: {time_alpha:.3f}s)")

        # Beta move
        start_beta = time.time()
        move_beta = playerExampleGamma.playerStrategy(game, state)
        time_beta = time.time() - start_beta
        print(f"Beta suggerisce:  {move_beta} (tempo: {time_beta:.3f}s)")

        # Scegli una delle due mosse casualmente
        chosen_move = random.choice([move_alpha, move_beta])
        print(f"👉 Mossa scelta: {chosen_move}")

        # Applica la mossa
        state = game.result(state, chosen_move)

    # Fine partita
    print("\n--- Fine partita ---")
    final_score = game.utility(state)
    winner = "Blue" if final_score == 1 else "Red"
    print(f"Vincitore: {winner}")

if __name__ == "__main__":
    test_ai_vs_ai_random_choice()