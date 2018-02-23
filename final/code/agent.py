# Code      : /code/agent.py
# Written by: LIU, Jiun Ee (G)
# Purpose   : This class is used to represent the players in the Texas Hold'em game
# Notes     : There are 8 styles of players implemented within this class. Each style has its own method, and the 
#               method dictates how that style of player responds to the game environment, what action to take,
#               and the amount to bet.

import pickle
import random
import math
import numpy as np

class Agent():
    BOT_STYLE_MAP = {1:'aggressive', 2:'conservative', 3:'high_hater', 4:'random', 5:'all-in', 6:'multi-style', 7:'feign', 8:'bluff'}

    # load probability dictionaries to be used by all agent types
    pkl_file = open('../table/type_prob_dict.pkl', 'rb')
    type_prob_dict = pickle.load(pkl_file)
    pkl_file.close()

    pkl_file = open("../table/decision_table_preflop.pkl", 'rb')
    pf_table = pickle.load(pkl_file)
    pkl_file.close()

    pkl_file = open("../table/decision_table_flop.pkl", 'rb')
    flop_table = pickle.load(pkl_file)
    pkl_file.close()

    def __init__(self, name, buy_in, style=None):
        self.name=name
        self.balance=buy_in
        self.allbets=0      # this is used to keep track of all the bets in a single game
                            # this way, by comparing the other agent's self.allbets, we know the diff is the amt to call 
        self.hole1=None     # hole card 1
        self.hole2=None     # hole card 2
        if style is None:
            self.style=random.choice( range(1, len(self.BOT_STYLE_MAP)+1) )
        else:
            self.style=style
        
    # zero out the bet amts from the previous game, and start a new amt tally for the new game
    def clear_bets(self):
        self.allbets=0
        
    def bets(self,amt):
        self.balance -= amt
        self.allbets += amt

    def wins(self,amt):
        self.balance += amt

    # Purpose   : Evaluate current hand and return the probability of winning
    # Input     : community cards: card1 - card5 parameters
    #             hole cards     : from self object
    # Output    : probability of winning
    def eval_hand(self, card1=None, card2=None, card3=None, card4=None, card5=None):
        if card1 is None:   # evaluate hole cards (pre-flop)
            # this is a simple algorithm by adding up the rank of the 2 hole cards (max 14 + 14 = 28) and divide by 28
            # if the 2 hole cards are suited, increase the probability by 10%
            # if the 2 hole cards have the same rank, set min prob = 50% (anecdotally pair of 2s have about 50% chance of winning)
            if self.hole1.getSuit() == self.hole2.getSuit():
                return min(1, (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28 * 1.1)
            elif self.hole1.getRank() == self.hole2.getRank():
                return min(1, max(0.5, (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28))
            else:
                return (self.hole1.getRank() + self.hole2.getRank()) * 1.0 / 28
        else:   # evaluate best hand so far with given community cards
            # do a probability lookup based on the 10 types of poker hands 
            hand=Hand(self.hole1, self.hole2, card1, card2, card3, card4, card5)
            return self.type_prob_dict[hand.hand_type]

    # aggressive - tends to bet or raise a higher $
    # written by: G
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

    # conservative - try to protect $ balance
    # written by: G
    def style_conservative(self, blind, potsize, callamt, card1, card2, card3, card4, card5):
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
        call_ratio = callamt * 1.0 / (potsize - callamt)
        bigblind_left = int((max(self.balance, 1e-5) - callamt) / blind / 2)
        call_balpct = callamt / self.balance
        randfct =  max(0.75, int(np.random.normal(2,1.5))/2.0)

        holerank = 0
        if card5 is not None: # how to do this on turn?
            comm_hand = Hand(card1, card2, card3, card4, card5)
            hone_hand = Hand(self.hole1, card1, card2, card3, card4, card5)
            htwo_hand = Hand(self.hole2, card1, card2, card3, card4, card5)
            best_hand = Hand(self.hole1, self.hole2, card1, card2, card3, card4, card5)
            if comm_hand.hand_type == best_hand.hand_type:
#                print 'holerank1 ', comm_hand.hand_type
                holerank = 0
                win_prob -= 0.5
            elif comm_hand.hand_type != hone_hand.hand_type or comm_hand.hand_type != htwo_hand.hand_type:
#                print 'holerank2 ', comm_hand.hand_type, hone_hand.hand_type, htwo_hand.hand_type
                holerank = 1
            elif best_hand.hand_type != hone_hand.hand_type and comm_hand.hand_type != htwo_hand.hand_type:
#                print 'holerank3 ', comm_hand.hand_type, hone_hand.hand_type, htwo_hand.hand_type, best_hand.hand_type
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
#            print 'bigblindleft', win_prob, call_balpct
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
#            print 'win_prob < .9', win_prob
            if call_ratio > 1.5:
                return 'c', 0
#            print 'win_prob < .9 r'
            return 'r', int(win_prob/(1-win_prob+0.000000001) * potsize)*randfct
        return 'a', 0 # better than 2-pair

    # feign - likes to hide the true strength of the hand
    # written by: Steven
    def style_feign(self, blind, potsize, callamt, *args):
        status_list = [card for card in list(args) if card != None]
        cards = list(args)
        status = 5 - len(status_list) # 5 pre-flop 2 flop 1 turn 0 river
        max_pay = self.balance
        act , amt = ['f', 0]

        if status == 5: 
            card_info = [[card.getSuit(), card.getRank()] for card in status_list+[self.hole1]+[self.hole2]]
            card_info.sort(key = lambda i: (i[1], i[0]), reverse = False)
            suit = [card_info[i][0] for i in range(len(card_info))]
            rank = [card_info[i][1] for i in range(len(card_info))]
            iden_pf = rank[1]*(10**4) + rank[0]*(10**2) + suit[1]*(10) + suit[0]
            des_prob = self.pf_table[iden_pf]
            factor = math.exp((des_prob - 0.5)*20)*blind*10
            max_pay = factor if des_prob != 1 else blind*10
            max_pay = min(int(max_pay), self.balance)

            if potsize < blind*100:

                if callamt <= blind*2:   
                    if factor <= blind*3:
                        act, amt = ['k', 0 ] if callamt == 0 else ['c', 0]
                    else:
                        act, amt = ['r', int(max_pay/2.0)]
                    return act, amt

                elif callamt <= max_pay:
                    return 'c', 0

            return 'f', 0

        elif status == 2:
            win_prob = self.eval_hand(cards[0] , cards[1], cards[2], None, None)
            card_info = [[card.getSuit(), card.getRank()] for card in status_list+[self.hole1]+[self.hole2]]
            card_info.sort(key = lambda i: (i[1], i[0]), reverse = False)
            suit = [card_info[i][0] for i in range(len(card_info))]
            rank = [card_info[i][1] for i in range(len(card_info))]
            iden_f = suit[4]*(10**4) + suit[3]*(10**3) + suit[2]*(10**2) + suit[1]*(10) + suit[0]
            iden_f += rank[4]*(10**13) + rank[3]*(10**11) + rank[2]*(10**9) + rank[1]*(10**7) + rank[0]*(10**5)
            win_prob = self.eval_hand(cards[0], cards[1], cards[2], cards[3], cards[4])
            
            if win_prob < 0.58: # one pair or less
                if potsize < blind*150:
                    des_prob = self.flop_table[iden_f]
                    max_pay = min(int(des_prob*blind*20), max_pay)

                    if max_pay == 0:
                        act, amt = ['k', 0] if callamt == 0 else ['f', 0]
                    elif callamt <= max_pay:
                        act, amt = ['c', 0] if callamt != 0 else ['r', int(max_pay)]
                return act, amt
            else: 

                if callamt <= max_pay:

                    act, amt = ['r', int(max_pay*0.3)] if callamt*2 <= max_pay*0.3 else ['c', 0]

                return act, amt

        else:
            win_prob = self.eval_hand(cards[0], cards[1], cards[2], cards[3], cards[4])
            max_pay = math.exp((win_prob - 0.9)*80)*blind*5 if win_prob < 0.58 else self.balance

            if win_prob < 0.58: # one pair or less
                if callamt == 0: return 'k', 0
                elif callamt <= max_pay:
                    act, amt = ['r', int(max_pay)] if callamt*2 <= int(max_pay) else ['c', 0]

            else:
                if callamt <= max_pay:
                    act, amt = ['r', int(max_pay*0.5)] if callamt*2 <= int(max_pay)*0.5 else ['c', 0]

        return act, amt

    # bluff - likes to pretend a stronger hand strength
    # written by: Steven
    def style_bluff(self, blind, potsize, callamt, *args):
        status_list = [card for card in list(args) if card != None]
        cards = list(args)
        status = 5 - len(status_list) # 5 pre-flop 2 flop 1 turn 0 river
        max_pay = self.balance
        call_ratio = callamt * 1.0 / (potsize - callamt)
        act, amt = ['f', 0]

        if status == 5: 
            win_prob = self.eval_hand(None, None, None, None, None)
            lie = 0.1 if random.random > 0.4 and win_prob < 0.52 else 1.0
            card_info = [[card.getSuit(), card.getRank()] for card in status_list+[self.hole1]+[self.hole2]]
            card_info.sort(key = lambda i: (i[1], i[0]), reverse = False)
            suit = [card_info[i][0] for i in range(len(card_info))]
            rank = [card_info[i][1] for i in range(len(card_info))]
            iden_pf = rank[1]*(10**4) + rank[0]*(10**2) + suit[1]*(10) + suit[0]
            des_prob = self.pf_table[iden_pf]
            factor = math.exp((des_prob - 0.5)*30*lie)*blind*20
            max_pay = factor if des_prob != 1 else blind*20
            max_pay = min(max_pay, self.balance)

            if potsize < blind*100:
                if callamt <= max_pay:
                    if max_pay <= blind*3:
                        act, amt = ['k', 0 ] if callamt == 0 else ['c', 0]
                    else:
                        act, amt = ['r', int(max_pay/2.0)]
                return act, amt

        elif status == 2:
            card_info = [[card.getSuit(), card.getRank()] for card in status_list+[self.hole1]+[self.hole2]]
            card_info.sort(key = lambda i: (i[1], i[0]), reverse = False)
            suit = [card_info[i][0] for i in range(len(card_info))]
            rank = [card_info[i][1] for i in range(len(card_info))]
            iden_f = suit[4]*(10**4) + suit[3]*(10**3) + suit[2]*(10**2) + suit[1]*(10) + suit[0]
            iden_f += rank[4]*(10**13) + rank[3]*(10**11) + rank[2]*(10**9) + rank[1]*(10**7) + rank[0]*(10**5)
            win_prob = self.eval_hand(cards[0] , cards[1], cards[2], None , None)
            lie = 0.1 if random.random > 0.4 and win_prob < 0.52 else 1.0
            win_prob = win_prob/(lie*7) if win_prob < 0.52 else win_prob

            if win_prob < 0.54:
                if potsize < blind*150:
                    des_prob = self.flop_table[iden_f]
                    max_pay = min(des_prob*blind*20, self.balance)
                else: return 'f', 0
            else:
                max_pay = min(blind*150, self.balance)
                max_pay = max_pay*win_prob if win_prob < 0.9 else max_pay

            if callamt <= max_pay:
                if callamt == 0: return 'r', int(max_pay*0.8)
                elif callamt <= max_pay*0.5: return 'r', int(max_pay*0.5)
                else: return 'c', 0
                
            return 'f', 0

        else:
            win_prob = self.eval_hand(cards[0] , cards[1], cards[2], cards[3] , cards[4])
            lie = 0.1 if random.random > 0.4 and win_prob < 0.52 else 1.0
            win_prob = win_prob/(lie*9) if win_prob < 0.5 else win_prob
            max_pay = int(math.exp((win_prob - 0.9)*4)*self.balance) if win_prob < 0.9 else self.balance

            if callamt == 0:
                return 'k', 0
            elif callamt > max_pay:
                return 'f', 0

            elif callamt < max_pay:
                return 'r', max_pay
            else:
                return 'c', 0
                
        return 'f', 0

    # high hater - hate hands with only high cards
    # written by: Steven
    def style_high_hater(self, potsize, callamt, card1, card2, card3, card4, card5):
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
        call_ratio = callamt * 1.0 / (potsize - callamt)
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
                return 'r', max(callamt, potsize * 2)
            return 'c', 0
        else:
            if call_ratio > 5:
                return 'c', 0
            return 'r', min(potsize*5, int(random.uniform(0,0.4)*self.balance))

    # random - random play
    # written by: G
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

    # all in - tends to go all-in
    # written by: G
    def style_all_in(self, blind, potsize, callamt, card1, card2, card3, card4, card5):
        rand = random.uniform(0,1)
        call_ratio = callamt * 1.0 / (potsize - callamt)
        bigblind_left = int((self.balance - callamt) / blind / 2)
        betact, betamt = self.style_conservative(blind, potsize, callamt, card1, card2, card3, card4, card5)
        if bigblind_left < 5 and rand < .8 or \
           betact == 'b' and rand < 0.2 or \
           betact == 'r' and rand < 0.4 or \
           betact == 'c' and call_ratio < 1.51 and rand < 0.65 or \
           betact == 'k' and rand < 0.1: 
            betact, betamt = 'a', 0
        return betact, betamt

    # if call amt is almost the entire balance, might as well go all-in        
    def round_up_all_in(self, callamt, betact, betamt, pct_left):                            
        if self.balance == 0:
            betact, betamt = ['k', 0] if callamt == 0 else ['f', 0]
        else:    
            if callamt * 1.0 / self.balance > (1-pct_left):
                if (betact == 'c') | (betact == 'r'):
                    betact, betamt = 'r', self.balance - callamt
            elif betamt * 1.0 / self.balance > (1-pct_left):
                if betact == 'r':
                    betamt = self.balance
        return betact, betamt

    # Purpose   : Depending on the style of player, determine what action to take (check, call, raise, all-in, or fold), 
    #               and the amount to bet or raise
    # Input     : blind amount, pot size, amt to call, community cards, style of play (and agent's own hole cards)
    # Output    : action to be taken and the corresponding amt
    def responds_base(self, blind, potsize, callamt, card1=None, card2=None, card3=None, card4=None, card5=None, style=None):
        if style is None:
            style = self.style
        
        if self.BOT_STYLE_MAP[style] == 'aggressive':
            betact, betamt = self.style_aggressive(potsize, callamt, card1, card2, card3, card4, card5)
            betact, betamt = self.round_up_all_in(callamt, betact, betamt, 0.05)

        elif self.BOT_STYLE_MAP[style] == 'conservative':
            betact, betamt = self.style_conservative(blind, potsize, callamt, card1, card2, card3, card4, card5)
            betact, betamt = self.round_up_all_in(callamt, betact, betamt, 0.02)

        elif self.BOT_STYLE_MAP[style] == 'feign':
            betact, betamt = self.style_feign(blind, potsize, callamt, card1, card2, card3, card4, card5)
            betact, betamt = self.round_up_all_in(callamt, betact, betamt, 0.02)

        elif self.BOT_STYLE_MAP[style] == 'bluff':
            betact, betamt = self.style_bluff(blind, potsize, callamt, card1, card2, card3, card4, card5)
            betact, betamt = self.round_up_all_in(callamt, betact, betamt, 0.02)

        elif self.BOT_STYLE_MAP[style] == 'high_hater':
            betact, betamt = self.style_high_hater(potsize, callamt, card1, card2, card3, card4, card5)

        elif self.BOT_STYLE_MAP[style] == 'random':
            betact, betamt = self.style_random(potsize, callamt)

        elif self.BOT_STYLE_MAP[style] == 'all-in':
            betact, betamt = self.style_all_in(blind, potsize, callamt, card1, card2, card3, card4, card5)
        
        elif self.BOT_STYLE_MAP[style] == 'multi-style':
            randstyle = random.choice(range(len(self.BOT_STYLE_MAP)))+1
            print 'randomly selected style', randstyle
            betact, betamt = self.responds_base(blind, potsize, callamt, card1, card2, card3, card4, card5, randstyle)
            print 'randomly selected style', randstyle, betact, betamt

        return betact, betamt

    # to ensure betting makes sense wrt rules and agent's balance
    def responds(self, blind, potsize, callamt, card1=None, card2=None, card3=None, card4=None, card5=None):
        betact, betamt = self.responds_base(blind, potsize, callamt, card1, card2, card3, card4, card5)

        if (betact == 'r') & (betamt == 0):
            betact = 'c'

        if betamt > self.balance: # raise over balance
            betamt = self.balance - callamt

        return betact, betamt
            
    def __str__(self):
        return "%s: $%d left." % (self.name, self.balance)
