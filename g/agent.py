# add callamt / balance to not raise again
# prob to bluff, but only a very small chance to the detriment of balance
# each number is a random float choice
# depending on blind/balance, shift style?
# bet amt also random around algo number
# design stupid bot as baseline and compare smarter bots to stupid 
import pickle
class Agent():
    # load dictionary to be used for all agents
    pkl_file = open('type_prob_dict.pkl', 'rb')
    type_prob_dict = pickle.load(pkl_file)
    pkl_file.close()

    def __init__(self, name, buy_in, style):
        self.name=name
        self.balance=buy_in
        self.allbets=0
        self.hole1=None
        self.hole2=None
        self.style=style
        
    def clear_bets(self):
        self.allbets=0
        
    def bets(self,amt):
        self.balance -= amt
        self.allbets += amt

    def wins(self,amt):
        self.balance += amt

    def eval_hand(self, card1=None, card2=None, card3=None, card4=None, card5=None):
        if card1 is None:
            if self.hole1.getSuit() == self.hole1.getSuit():
                return min(1, (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28 * 1.1)
            elif self.hole1.getRank() == self.hole1.getRank():
                return min(1, max(0.5, (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28))
            else:
                return (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28
        else:
            hand=Hand(self.hole1, self.hole2, card1, card2, card3, card4, card5)
#            print 'audit2c ', hand.hand_type
#            print 'audit2c ', self.type_prob_dict[hand.hand_type]
            return self.type_prob_dict[hand.hand_type]
                            
    def responds_base(self, potsize, callamt, card1=None, card2=None, card3=None, card4=None, card5=None):
        # response: call, raise, all-in, or fold, and the amount to raise
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
 #       print 'win_prob', win_prob
        call_ratio     = callamt * 1.0 / (potsize - callamt)
        withdraw_ratio = callamt * 1.0 /self.balance
 #       print 'call_ratio', call_ratio
        if self.style == 'aggressive':
            if win_prob < .51: # high card only
#                print 'respondbase1a'
                if call_ratio > 0.75:
                    return 'f', 0
                elif call_ratio > 0.5: 
                    return 'c', 0
                elif callamt > 0:
                    return 'r', potsize - callamt
                else:
                    return 'k', 0
            elif win_prob < .6: # one-pair
#                print 'respondbase1b'
                if call_ratio > 1.5:
                    return 'f', 0
                elif call_ratio > 1.0:
                    return 'c', 0
                elif callamt > 0:
                    return 'r', potsize - callamt
                else:
                    return 'k', 0
            elif win_prob < .9: # 2-pair
#                print 'respondbase1c'
                if callamt > 0:
                    return 'r', int(potsize * 1.5)
                else:
                    return 'b', potsize
            else: # better than 2-pair
#                print 'respondbase1d'
                if callamt > 0:
                    return 'a', 0
                elif win_prob > .97:
                    return 'a', 0
                elif win_prob > .94:
                    return 'b', int(potsize * 3)
                else:
                    return 'b', int(potsize * 2)
        elif self.style == 'conservative':
            if win_prob < .51: # high card only
                if call_ratio > 0.5:
                    return 'f', 0
                elif call_ratio >= 0.3:
                    return 'c', 0
                return 'r', potsize - callamt
            elif win_prob < .6: # one-pair
                if call_ratio > 1:
                    return 'f', 0
                elif call_ratio >= 0.8:
                    return 'c', 0
                return 'r', potsize - callamt
            elif win_prob < .9: # 2-pair
                if call_ratio > 1.5:
                    return 'c', 0
                return 'r', int(potsize * 1.5)
            # better than 2-pair
            return 'a', 0            
        elif self.style == 'defensive':
            return 'f', 0
        elif self.style == 'stupid':
            return 'c', 0 # always call

        elif self.style == 'high_hater':

            if callamt == 0:
                return 'k', 0

            elif win_prob <= .5011: # high card only
                if call_ratio > 0.05:
                    return 'f', 0
                else:
                    return 'c', 0

            elif win_prob < .9:
                if call_ratio > 1 or withdraw_ratio > 4:
                    return 'f', 0
                elif withdraw_ratio < 0.1:
                    return 'r', max(callamt, potsize * 2)
                return 'c', 0
            else:
                if call_ratio > 5:
                    return 'c', 0
                return 'r', min(int(potsize*5, rm.randint(0, 4)), self.balance)

    # to ensure betting makes sense wrt rules and agent's balance
    def responds(self, potsize, callamt, card1=None, card2=None, card3=None, card4=None, card5=None):
        betact, betamt = self.responds_base(potsize, callamt, card1, card2, card3, card4, card5)

        # if call amt is almost the entire balance, might as well go all-in
        if callamt * 1.0 / self.balance > 0.95:
#            print 'respond1'
            if (betact == 'c') | (betact == 'r'):
#                print 'respond1a'
                betact = 'r'
                betamt = self.balance - callamt

        if (betact == 'r') & (betamt == 0):
            betact = 'c'

        if betamt > self.balance: # raise over balance
#            print 'respond2 bet > self balance'
            print betamt, self.balance
            betamt = self.balance - callamt

        return betact, betamt
            
    def __str__(self):
        return "%s: $%d left." % (self.name, self.balance)
