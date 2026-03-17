import random
import time
from Wherewolf import Wherewolf
from tqdm import tqdm


NUM_GAMES = 1000

wins = 0
total_rounds = 0
total_runtime = 0
correct_deductions = 0
total_deductions = 0

random.seed(42)


for g in tqdm(range(NUM_GAMES), total=NUM_GAMES):

    num_players = random.randint(10, 20)

    N = 0
    M = 0
    roles = ["-"] * num_players

    for i in range(num_players):
        if random.random() < 0.5:
            roles[i] = "W"
            N += 1
        else:
            roles[i] = "V"
            M += 1

    R = random.randint(2, 5)

    W_o = random.random()
    W_q = random.random() * (1 - W_o)
    W_s = 1 - W_o - W_q

    V_o = random.random()
    V_q = random.random() * (1 - V_o)
    V_s = 1 - V_o - V_q

    T = random.random()

    mygame = Wherewolf(N, M, R, W_o, W_q, W_s, V_o, V_q, V_s, T)

    rounds = 0
    game_start = time.time()

    while N != 0 and M != 0:

        # ----- Interrogation -----
        for r in range(R):

            hint = [0] * num_players

            for i in range(num_players):

                lf = "S"

                if roles[i] == "W":
                    u = random.random()
                    if u < W_o:
                        lf = "V"
                    elif u < W_o + W_s:
                        lf = "W"

                elif roles[i] == "V":
                    u = random.random()
                    if u < V_o:
                        lf = "W"
                    elif u < V_o + V_s:
                        lf = "V"

                l = []

                if roles[i] != "-" and lf != "S":
                    for j in range(num_players):
                        if i != j and roles[j] == lf:
                            l.append(j)

                    if len(l) != 0:
                        hint[i] = l[random.randint(0, len(l) - 1)] + 1

            mygame.interrogation(hint)

        # ----- Deduction -----
        suspect = mygame.deduction()

        total_deductions += 1

        if roles[suspect - 1] == "W":
            correct_deductions += 1

        revealed = roles[suspect - 1]
        roles[suspect - 1] = "-"

        # ----- Transition -----
        mygame.transition(revealed)

        if revealed == "W":
            N -= 1
        else:
            M -= 1

        if N + M >= 1:
            for i in range(num_players):
                if roles[i] == "W":
                    if random.random() < T:
                        j = i - 1
                        if j < 0:
                            j += num_players

                        while roles[j] == "-":
                            j -= 1
                            if j < 0:
                                j += num_players

                        roles[j], roles[i] = roles[i], roles[j]

        rounds += 1

    game_end = time.time()

    total_rounds += rounds
    total_runtime += (game_end - game_start)

    if N == 0:
        wins += 1


print("===== Evaluation Results =====")
print("Games played:", NUM_GAMES)
print("Win rate:", wins / NUM_GAMES)
print("Average rounds:", total_rounds / NUM_GAMES)
print("Deduction accuracy:", correct_deductions / total_deductions)
print("Average runtime per game:", total_runtime / NUM_GAMES)