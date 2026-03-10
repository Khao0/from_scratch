#####
#
# Name: Kwankhao Tangprasert
# Student ID: 653040165-6
#
#####

class Wherewolf:
    def __init__(self,N,M,R,W_o,W_q,W_s,V_o,V_q,V_s,T):
        self.total = N+M
        self.current = 0

    def interrogation(self,hint):
        pass

    def deduction(self):
        self.current += 1
        return self.current

    def transition(self,revealed):
        pass

