import random
import time
from Wherewolf import Wherewolf

num_players = random.randint(10, 20)
N = 0
M = 0
roles = ["-"] * (num_players)
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
total_time = 0

t_start = time.time()
mygame = Wherewolf(N, M, R, W_o, W_q, W_s, V_o, V_q, V_s, T)
t_stop = time.time()
total_time += (t_stop - t_start)

while N != 0 and M != 0:
    print("Sneak peek at roles:", roles)
    # Interrogation
    print("-----Interrogation Phase-----")
    for r in range(R):
        hint = [0] * num_players
        for i in range(num_players):
            lf = "S"
            if roles[i] == "W":
                u = random.random()
                if u < W_o:  # point to other team
                    lf = "V"
                elif u < W_o + W_s:  # point to same team
                    lf = "W"
            elif roles[i] == "V":
                u = random.random()
                if u < V_o:  # point to other team
                    lf = "W"
                elif u < V_o + V_s:  # point to same team
                    lf = "V"
            l = []
            if roles[i] != "-" and lf != "S":
                for j in range(num_players):
                    if i != j and roles[j] == lf:
                        l.append(j)
                if len(l) != 0:
                    hint[i] = l[random.randint(0, len(l) - 1)] + 1
        print("Provided Hint: " + str(hint))
        t_start = time.time()
        mygame.interrogation(hint)
        t_stop = time.time()
        total_time += (t_stop - t_start)
    # Deduction
    print("-----Deduction Phase-----")
    t_start = time.time()
    suspect = mygame.deduction()
    t_stop = time.time()
    total_time += (t_stop - t_start)
    if total_time > 5:
        print("Timed out.")
        print("The game stops.")
        exit()
    print("Total time used since last deduction:", total_time, "seconds")
    total_time = 0
    print("Your deduction: " + str(suspect))
    if suspect < 1 or suspect > num_players or roles[suspect - 1] == '-':
        print("Invalid answer.")
        print("The game stops.")
        exit()
    revealed = roles[suspect - 1]
    roles[suspect - 1] = "-"
    # Transition
    print("-----Transition Phase-----")
    role = "Wolf" if revealed == "W" else "Villager"
    print("The suspect is revealed as " + role)
    t_start = time.time()
    mygame.transition(revealed)
    t_stop = time.time()
    total_time += (t_stop - t_start)
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
                        j = j - 1
                        if j < 0:
                            j += num_players
                    tmp = roles[j]
                    roles[j] = roles[i]
                    roles[i] = tmp
    print("########## End of iteration ##########")
endgame_message = "There is no villager left. You lose." if M == 0 else "There is no wolf left. You win!"
print(endgame_message)
