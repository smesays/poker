# add callamt / balance to not raise again
# prob to bluff, but only a very small chance to the detriment of balance
# each number is a random float choice
# depending on blind/balance, shift style?
# bet amt also random around algo number
# design stupid bot as baseline and compare smarter bots to stupid 
import pickle
import random
import numpy as np

class Agent():
    BOT_STYLE_MAP = {1:'aggressive', 2:'conservative', 3:'high_hater', 4:'random', 5:'all-in', 6:'multi-style'}

    # load dictionary to be used for all agents
    pkl_file = open('type_prob_dict.pkl', 'rb')
    type_prob_dict = pickle.load(pkl_file)
    pkl_file.close()

    def __init__(self, name, buy_in, style=None):
        self.name=name
        self.balance=buy_in
        self.allbets=0
        self.hole1=None
        self.hole2=None
        if style is None:
            self.style=random.choice( range(1, len(self.BOT_STYLE_MAP)+1) )
        else:
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
            if self.hole1.getSuit() == self.hole2.getSuit():
                return min(1, (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28 * 1.1)
            elif self.hole1.getRank() == self.hole2.getRank():
                return min(1, max(0.5, (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28))
            else:
                return (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28
        else:
            hand=Hand(self.hole1, self.hole2, card1, card2, card3, card4, card5)
#            print 'audit2c ', hand.hand_type
#            print 'audit2c ', self.type_prob_dict[hand.hand_type]
            return self.type_prob_dict[hand.hand_type]

    def style_aggressive(self, potsize, callamt, card1, card2, card3, card4, card5):
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
        call_ratio = callamt * 1.0 / (potsize - callamt)
        randfct =  max(1, int(np.random.normal(2,2))/2.0)
        if win_prob < .51: # high card only
            if call_ratio > 0.75:
                return 'f', 0
            elif call_ratio > 0.5: 
                return 'c', 0
            elif callamt > 0:
                return 'r', (potsize - callamt)*randfct
            else:
                return 'k', 0
        elif win_prob < .6: # one-pair
            if call_ratio > 1.2:
                return 'f', 0
            elif call_ratio > 1.0:
                return 'c', 0
            elif callamt > 0:
                return 'r', (potsize - callamt)*randfct
            else:
                return 'k', 0
        elif win_prob < .9: # 2-pair
            if call_ratio > 2:
                return 'f', 0
            elif call_ratio > 0.75:
                return 'c', 0
            elif callamt > 0:
                return 'r', int(potsize * 1.5)*randfct
            else:
                return 'b', potsize*randfct
        else: # better than 2-pair
            if callamt > 0:
                return 'a', 0
            elif win_prob > .97:
                return 'a', 0
            elif win_prob > .94:
                return 'b', int(potsize * 3)*randfct
            else:            
                return 'b', int(potsize * 2)*randfct

    def style_conservative(self, blind, potsize, callamt, card1, card2, card3, card4, card5):
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
        call_ratio = callamt * 1.0 / (potsize - callamt)
        bigblind_left = int((self.balance - callamt) / blind / 2)
        call_balpct = callamt / self.balance
        randfct =  max(0.75, int(np.random.normal(2,1.5))/2.0)

        holerank = 0
        if card5 is not None: # how to do this on turn?
            comm_hand = Hand(card1, card2, card3, card4, card5)
            hone_hand = Hand(self.hole1, card1, card2, card3, card4, card5)
            htwo_hand = Hand(self.hole2, card1, card2, card3, card4, card5)
            best_hand = Hand(self.hole1, self.hole2, card1, card2, card3, card4, card5)
            if comm_hand.hand_type == best_hand.hand_type:
                print 'holerank1 ', comm_hand.hand_type
                holerank = 0
                win_prob -= 0.5
            elif comm_hand.hand_type != hone_hand.hand_type or comm_hand.hand_type != htwo_hand.hand_type:
                print 'holerank2 ', comm_hand.hand_type, hone_hand.hand_type, htwo_hand.hand_type
                holerank = 1
            elif best_hand.hand_type != hone_hand.hand_type and comm_hand.hand_type != htwo_hand.hand_type:
                print 'holerank3 ', comm_hand.hand_type, hone_hand.hand_type, htwo_hand.hand_type, best_hand.hand_type
                holerank = 2
                win_prob += 0.05

        if bigblind_left < 3:
            if win_prob > 0.4:
                return 'a', 0
            elif callamt > 0:
                return 'f', 0
            else:
                return 'k', 0

        if bigblind_left < 7:
            print 'bigblindleft', win_prob, call_balpct
            if card1 is None and win_prob > .93:
                return 'r', int(win_prob/(1-win_prob+0.000000001) * potsize * 1.2)*randfct
            elif card1 is not None and win_prob > .97:
                return 'a', 0
            elif card1 is None and win_prob > .89 or card1 is not None and win_prob > .93:
                return 'r', int(win_prob/(1-win_prob+0.000000001) * potsize)*randfct
            elif call_balpct > .10:
                return 'f', 0
            elif callamt > 0:
                return 'c', 0
            else:
                return 'k', 0

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
            return 'r', (potsize - callamt)*randfct
        elif win_prob < .9: # 2-pair
            print 'win_prob < .9', win_prob
            if call_ratio > 1.5:
                return 'c', 0
            print 'win_prob < .9 r'
            return 'r', int(win_prob/(1-win_prob+0.000000001) * potsize)*randfct
        return 'a', 0 # better than 2-pair

    def style_high_hater(self, potsize, callamt, card1, card2, card3, card4, card5):
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
        call_ratio     = callamt * 1.0 / (potsize - callamt)
#### need to figure out how self.balance=0 gets in here
### for now, cheat
        if self.balance == 0:
            withdraw_ratio = 100
        else:
            withdraw_ratio = callamt * 1.0 / self.balance
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
#                print 'highhater r1', callamt
#                print 'highhater r1', max(callamt, potsize * 2)                 
                return 'r', max(callamt, potsize * 2)
            return 'c', 0
        else:
            if call_ratio > 5:
                return 'c', 0
#            print 'highhater r2', int(random.uniform(0,0.4)*self.balance)
            return 'r', min(potsize*5, int(random.uniform(0,0.4)*self.balance))

    def style_random(self, potsize, callamt):
        betamt = 0
        if callamt > 0:
            betact = random.choice(['a','r','c','f'])
            if betact == 'r':
                betamt = random.uniform(1,5)*callamt
        else:
            betact = random.choice(['k','b','a'])
            if betact == 'b':
                betamt = max( random.uniform(0.05,0.5), min(0.8,int(np.random.normal(0.05,0.2))) )*self.balance
        return betact, int(betamt)

    def style_all_in(self, blind, potsize, callamt, card1, card2, card3, card4, card5):
        print 'style all-in'
        rand = random.uniform(0,1)
        call_ratio = callamt * 1.0 / (potsize - callamt)
        bigblind_left = int((self.balance - callamt) / blind / 2)
        betact, betamt = self.style_conservative(blind, potsize, callamt, card1, card2, card3, card4, card5)
        if bigblind_left < 5 and rand < .8 or \
           betact == 'b' and rand < 0.2 or \
           betact == 'r' and rand < 0.4 or \
           betact == 'c' and call_ratio < 1.51 and rand < 0.65 or \
           betact == 'k' and rand < 0.1: 
            print 'style all-in change to a'
            betact = 'a'
            betamt = 0
        return betact, betamt

    def round_up_all_in(self, callamt, betact, betamt, pct_left):                            
        # if call amt is almost the entire balance, might as well go all-in
        if callamt * 1.0 / self.balance > (1-pct_left):
#            print 'respond1'
            if (betact == 'c') | (betact == 'r'):
#                print 'respond1a bef', betact, betamt
                betact = 'r'
                betamt = self.balance - callamt
#                print 'respond1a aft', betact, betamt
        elif betamt * 1.0 / self.balance > (1-pct_left):
#            print 'respond2'
            if betact == 'r':
#                print 'respond2a bef', betact, betamt
                betamt = self.balance
#                print 'respond2a aft', betact, betamt
        return betact, betamt

    def responds_base(self, blind, potsize, callamt, card1=None, card2=None, card3=None, card4=None, card5=None, style=None):
        if style is None:
            style = self.style

        # response: call, raise, all-in, or fold, and the amount to raise
        if self.BOT_STYLE_MAP[style] == 'aggressive':
            betact, betamt = self.style_aggressive(potsize, callamt, card1, card2, card3, card4, card5)
            betact, betamt = self.round_up_all_in(callamt, betact, betamt, 0.05)

        elif self.BOT_STYLE_MAP[style] == 'conservative':
            betact, betamt = self.style_conservative(blind, potsize, callamt, card1, card2, card3, card4, card5)
            betact, betamt = self.round_up_all_in(callamt, betact, betamt, 0.02)

        elif self.BOT_STYLE_MAP[style] == 'high_hater':
            betact, betamt = self.style_high_hater(potsize, callamt, card1, card2, card3, card4, card5)

        elif self.BOT_STYLE_MAP[style] == 'random':
            betact, betamt = self.style_random(potsize, callamt)

        elif self.BOT_STYLE_MAP[self.style] == 'all-in':
            print 'responds base all-in'
            betact, betamt = self.style_all_in(blind, potsize, callamt, card1, card2, card3, card4, card5)
            print 'responds base all-in', betact, betamt
        
        elif self.BOT_STYLE_MAP[style] == 'multi-style':
#            randstyle = random.choice(range(len(self.BOT_STYLE_MAP)))+1
# not sure why this fails with style 5
            randstyle = random.choice([1,2,3,4]) 
            print 'randomly selected style', randstyle
            betact, betamt = self.responds_base(blind, potsize, callamt, card1, card2, card3, card4, card5, randstyle)
            print 'randomly selected style', randstyle, betact, betamt

        elif self.BOT_STYLE_MAP[style] == 'stupid': # always call
            betact = 'c'
            betamt = 0 

        return betact, betamt

    # to ensure betting makes sense wrt rules and agent's balance
    def responds(self, blind, potsize, callamt, card1=None, card2=None, card3=None, card4=None, card5=None):
        betact, betamt = self.responds_base(blind, potsize, callamt, card1, card2, card3, card4, card5)

        if (betact == 'r') & (betamt == 0):
            betact = 'c'

        if betamt > self.balance: # raise over balance
#            print 'respond2 bet > self balance'
            print betamt, self.balance, callamt
            betamt = self.balance - callamt

        return betact, betamt
            
    def __str__(self):
        return "%s: $%d left." % (self.name, self.balance)
