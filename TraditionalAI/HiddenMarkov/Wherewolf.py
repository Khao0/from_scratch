#####
#
# Name: Kwankhao Tangprasert
# Student ID: 653040165-6
#
#####

from typing import List, Literal

class Wherewolf:
    # state = {wolve, villager}
    def __init__(self,N,M,R,W_o,W_q,W_s,V_o,V_q,V_s,T):
        self.state =["Wolf", "Villager"]
        self.total = N+M
        self.wolf_trans_prob = T
        self.R = R
        self.remaining_N : int = N # wolves
        self.remaining_M : int = M # villagers
        self.remaining_player_idx = set(i for i in range(self.total))

        # hidden state prob dist
        init_wolf_prob = self.remaining_N/self.total
        self.wolf_prob_dist = self.get_prob_dist(init_wolf_prob)
        self.vill_prob_dist = self.get_prob_dist(1-init_wolf_prob)
        # self.accuse_dist = self.get_prob_dist()


        # Emission
        self.wolf_emission_model = {
            "O":W_o,
            "Q":W_q,
            "S":W_s
        }

        self.vill_emission_model = {
            "O":V_o,
            "Q":V_q,
            "S":V_s
        }


    def interrogation(self,hint:List[int])->None:
        """
        Observations Updated
        hint : List[int]
        len(hint) = N + M
        where the value of 0 mean the character stay quiet or the char is already removed
        example 
        - index = 2, value = 3 
        mean player 3 point at player 4
        note : player start from 1: N+M not 0 : N+M-1 but index start from 0
        """
        #? Q: does remaining wolve is effect to this
        #? Q: number of accusation
        # because we change value in the main list after it pointed, per one hint might have multiple chars point to the same char, which it will effect the pw and pv
        ori_wolf_dist = self.wolf_prob_dist[:]
        ori_vill_dist = self.vill_prob_dist[:]

        for i in self.remaining_player_idx:
            e = hint[i]
            if e == 0 :
                wolf_likelihood = self.wolf_emission_model["Q"]
                vill_likelihood = self.vill_emission_model["Q"]
            else:
                #pointed player prob
                j = e-1
                pw = ori_wolf_dist[j]  
                pv = ori_vill_dist[j]

                # prob that wolf/vill will point on the same and opp team
                wolf_likelihood = pw*self.wolf_emission_model["S"] + pv*self.wolf_emission_model["O"]
                vill_likelihood = pv*self.vill_emission_model["S"] + pw*self.vill_emission_model["O"]
            
            # update belief
            self.wolf_prob_dist[i] *= wolf_likelihood
            self.vill_prob_dist[i] *= vill_likelihood

            # normalize
            divider = self.wolf_prob_dist[i] + self.vill_prob_dist[i]
            self.wolf_prob_dist[i] /= divider
            self.vill_prob_dist[i] /= divider


    def deduction(self) -> int:

        max_wolf_score = -float("inf")
        max_idx = None

        for i in self.remaining_player_idx:
            wolf_prob = self.wolf_prob_dist[i]
            # vill_prob = self.vill_prob_dist[i]
            wolf_score = 2*wolf_prob - 1 # wolf_prob - vill_prob simplify
            if wolf_score > max_wolf_score:
                max_idx = i
                max_wolf_score = wolf_score

        # if max_idx is None:
        #     raise("there is no max wolf prob")
        self.remaining_player_idx.remove(max_idx)
        self.wolf_prob_dist[max_idx] = 0
        self.vill_prob_dist[max_idx] = 0
        return max_idx + 1
    
    def get_prob_dist(self, base_val:float=0) -> List[int]:
        return [base_val]*self.total

    def transition(self,revealed: Literal["W", "V"])->None:
        if revealed == "W":
            self.remaining_N -= 1
        else:
            self.remaining_M -= 1
            
        new_wolf_dist = self.get_prob_dist()
        new_vill_dist = self.get_prob_dist()

        right_idx = max(self.remaining_player_idx)
        prob_wolf_right = self.wolf_prob_dist[right_idx]
        for current_idx in self.remaining_player_idx:
            # print(f"curr idx {current_idx}, right index is {right_idx}")

            prob_wolf_curr = self.wolf_prob_dist[current_idx]
    
            #
            new_wolf = prob_wolf_curr*(1-self.wolf_trans_prob) + prob_wolf_right*self.wolf_trans_prob
            new_vill = 1 - new_wolf

            new_wolf_dist[current_idx] = new_wolf
            new_vill_dist[current_idx] = new_vill

            right_idx = current_idx
            prob_wolf_right = prob_wolf_curr

        # time updated
        self.wolf_prob_dist = new_wolf_dist
        self.vill_prob_dist = new_vill_dist

        # self.accuse_dist = self.get_prob_dist()
        

# TODO do particle filtering -> use iterative deepening