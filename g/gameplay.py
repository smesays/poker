# Code      : gameplay.py
# Written by: LIU, Jiun Ee (G); TANG, Chit Long (Steven)
# Purpose   : This class is used to represent a single game within a tournament of multiple games and rounds
# Notes     : Each game is dealt from a newly shuffled deck of cards, has its own blinds requirement, one set
#               of community cards, etc.

import sys
import pickle

class Gameplay():
    # when initializing, agents should be ordered so they go first alternately
    GAME_INDENT = 66    # number of spaces to indent the game messages

    pkl_file = open('../table/type_prob_dict.pkl', 'rb')
    type_prob_dict = pickle.load(pkl_file)
    pkl_file.close()

    def __init__(self, gamenum, agent1, agent2, blind, minchip, prompt):
        '''
        prompt determines whether we need to prompt for human response 
        prompt = 0 is for bots play
        prompt = 1 will prompt for responses from agent1, and similarly for 2
        '''
        self.gamenum = gamenum
        self.agent1 = agent1
        self.agent1.clear_bets()
        self.agent2 = agent2
        self.agent2.clear_bets()
        self.blind = blind
        self.minbet = blind * 2 # minimum bet is big blind
        self.minchip = minchip  # all bets should be in multiples of smallest chip denomination
        self.prompt = prompt
        self.elapsed = 0    # track elapsed time in seconds so we can increase blind after 30 minutes

        self.pot = 0    # total amt of chips in the pot
        self.phase = 0  # track the phase of the game
        self.betidx = -1
        self.betlog = [] # tuple (phase, betidx, agent, amt) is there a way to not store agent class? store 1 or 2 instead
        self.agent1_fold = 0
        self.agent2_fold = 0

        self.deck = Deck()
        self.flop1 = None
        self.flop2 = None
        self.flop3 = None
        self.turn = None
        self.river = None
        
    def to_pot(self, amt):
        self.pot += amt
        
    def log_card(self, card):
        if card is None:
            return 0, 0
        else:
            return card.getRank(), card.getSuit()

    def log_comm_cards(self):
        return tuple(list(self.log_card(self.flop1)) + list(self.log_card(self.flop2)) + list(self.log_card(self.flop3)) + list(self.log_card(self.turn)) + list(self.log_card(self.river)))

    def log_hole_cards(self, agent):
        return tuple(list(self.log_card(agent.hole1)) + list(self.log_card(agent.hole2)))

    # same method from agent.py
    # this is inserted here so that we can output the winning probability of the hand to the log for analysis later
    def eval_hand(self, agent, card1=None, card2=None, card3=None, card4=None, card5=None):
        if card1 is None:
            if agent.hole1.getSuit() == agent.hole2.getSuit():
                return min(1, (agent.hole1.getRank() + agent.hole2.getRank()) * 1.0 / 28 * 1.1)
            elif agent.hole1.getRank() == agent.hole2.getRank():
                return min(1, max(0.5, (agent.hole1.getRank() + agent.hole2.getRank()) * 1.0 / 28))
            else:
                return (agent.hole1.getRank() + agent.hole2.getRank()) * 1.0 / 28
        else:
            hand=Hand(agent.hole1, agent.hole2, card1, card2, card3, card4, card5)
            return self.type_prob_dict[hand.hand_type]

    # amount needs to be divisible by the smallest denomination of chip
    # if style algorithm returns an amount that is not divisible, round down
    def minchip_audit(self, amt):
        return int(amt / self.minchip) * self.minchip

    # Purpose   : Bet, raise, or call, all involve money moving from player to the pot. This method 
    #               does the accounting of the "betting action"
    def bets(self, agent, amt, betact='b', blind='', printpot=1, callamt=0):
    # parameter amt is callamt if callamt is 0
    # parameter amt is raiseamt if callamt > 0
        if betact == 'r' and callamt > agent.balance:
            betact, amt, callamt = 'c', agent.balance, 0
        if amt > agent.balance:
            amt = agent.balance

        map_act = {'b':'bets', 'c':'calls', 'r':'raises'}
        self.betidx += 1
        agent.bets(amt+callamt)
        print '    %s %s%s $%d.' % (agent.name, map_act[betact], blind, amt), agent
        self.to_pot(amt+callamt)
        if (self.prompt != 0) & printpot == 1:
            print '  Pot has $%d' % self.pot
        if blind != '':
            self.elapsed += 5
        elif betact == 'r':
            self.elapsed += 25
        elif betact == 'c':
            self.elapsed += 15
        else:
            self.elapsed += 10
        if self.phase != 0:
            self.betlog.append(tuple([self.gamenum, self.phase, self.betidx, agent.name, agent.style, betact, amt+callamt, self.blind, agent.balance, self.pot] + \
                                     list(self.log_comm_cards()) + list(self.log_hole_cards(agent)) + \
                                     [self.eval_hand(agent, self.flop1, self.flop2, self.flop3, self.turn, self.river)] ))

    # ensure that the raise action and the raise amount make sense
    def raiseamt_audit(self, betagent, resagent, betact, raiseamt):
        if resagent.balance == 0:
            return 'c', 0
        elif raiseamt > resagent.balance:
            return betact, resagent.balance
        return betact, self.minchip_audit(raiseamt)
    
    # ensure that the response action and the amount make sense
    def res_audit(self, betagent, callamt, resagent, resact, resamt):
        if resact == 'a':
            resact, resamt = 'r', min(betagent.balance, resagent.balance - callamt)
            
        if resact == 'r':
            if resamt < callamt:
                resact, resamt = 'c', 0

            if resagent.balance == callamt:
                resact, resamt = 'c', 0

            if resamt > resagent.balance - callamt:
                resamt = resagent.balance - callamt
            elif resamt == resagent.balance or resamt == betagent.balance:
                pass    # raise all-in
            elif resamt < self.minbet:
                resact, resamt = 'c', 0
        return resact, self.minchip_audit(resamt)

    # ensure that the bet action and the amount make sense
    def bet_audit(self, betagent, betact, betamt, resagent):
        if betact == 'b' or betact == 'r':
            if betamt > resagent.balance: # cannot bet more than opponent's balance
                betamt = resagent.balance
                
            if betamt < self.minbet:
                betact, betamt = 'k', 0
                
        if betamt > 0:
            betamt = self.minchip_audit(betamt)
            if betamt == 0:
                betact, betamt = 'k', 0
        return betact, betamt
            
    def print_action_txt(self, agent):
        return 'Action to %s. (Hole: %s %s, $%d left)' % (agent.name, agent.hole1, agent.hole2, agent.balance)

    # opening the action with bet or check
    def opening(self, betagent, resagent, prompt): 
        betagent_check = 0
        betact, betamt = '', 0
        if self.prompt == prompt:
            print " "*self.GAME_INDENT, "%s" % self.print_action_txt(betagent)
            while betact not in ('k','b','a'):
                print " "*self.GAME_INDENT, '> Chec(K), (B)et, or (A)ll-in? Enter k, b, or a:',
                betact = raw_input().lower()
            if betact == 'b':
                while betamt < self.minbet:
                    print " "*self.GAME_INDENT, '> Enter the amount to bet: (min $%d)' % self.minbet,
                    tempin = raw_input()
                    if tempin.isdigit():
                        betamt = int(tempin)
        else:
            betact, betamt = betagent.responds(self.blind, self.pot, 0, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)
            
        betact, betamt = self.bet_audit(betagent, betact, betamt, resagent)

        if betact == 'k':
            betagent_check = 1 
            print "    %s checks." % betagent.name
            self.elapsed += 10
            if self.phase != 0:
                self.betlog.append(tuple([self.gamenum, self.phase, self.betidx, betagent.name, betagent.style, betact, betamt, self.blind, betagent.balance, self.pot] + \
                                         list(self.log_comm_cards()) + list(self.log_hole_cards(betagent)) + \
                                         [self.eval_hand(betagent, self.flop1, self.flop2, self.flop3, self.turn, self.river)] ))
        elif betact == 'a':
            betact = 'r'
            betamt = betagent.balance
            betact, betamt = self.raiseamt_audit(betagent, resagent, betact, betamt)
            self.bets(betagent, betamt)
        else: 
            self.bets(betagent, betamt)

        return betagent_check

    # responding to a bet
    def responding(self, betagent, resagent, prompt): 
        callamt = betagent.allbets - resagent.allbets 
        betact, betamt = '', 0
        if self.prompt == prompt: 
            print " "*self.GAME_INDENT, "%s" % self.print_action_txt(resagent)
            if (betagent.balance == 0) | (resagent.balance == 0) | (resagent.balance == callamt):
                while betact not in ['c','f']:
                    print " "*self.GAME_INDENT, '> (C)all $%d, or (F)old? Enter c, or f:' % callamt,
                    betact = raw_input().lower()
            else:
                while betact not in ['c','r','a','f']:
                    print " "*self.GAME_INDENT, '> (C)all $%d, (R)aise, (A)ll-in $%d, or (F)old? Enter c, r, a, or f:' % (callamt, min(betagent.balance, resagent.balance)),
                    betact = raw_input().lower()
                if betact == 'r':
                    while betamt < max(self.minbet, callamt):
                        print ' '*self.GAME_INDENT, '> Enter the amount to raise (min $%d):' % max(self.minbet, callamt),
                        tempin = raw_input()
                        if tempin.isdigit():
                            betamt = int(tempin)
        else:
            betact, betamt = resagent.responds(self.blind, self.pot, callamt, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)
            if betamt < 0:
                print 'what is this1?'
                resagent.balance = 0
        betact, betamt = self.res_audit(betagent, callamt, resagent, betact, betamt)

        foldflag = 0
        if betact == 'c':
            self.bets(resagent, callamt, 'c')
            checkflag = 1
        elif (betact == 'r') | (betact == 'a'):
            if betact == 'a':
                betact = 'r'
                betamt = resagent.balance - callamt
            betact, betamt = self.raiseamt_audit(resagent, betagent, betact, betamt)
            if betact == 'c':
                self.bets(resagent, callamt, 'c')
                checkflag = 1
            else:
                self.bets(resagent, betamt, 'r', callamt=callamt)
                checkflag = 0
        else:
            foldflag = 1
            checkflag = 1                        
            # when we log for the fold action, we need to include the callamt because callamt / potsize is the ratio that has meaning
            # and can cause the player to fold
            self.elapsed += 10
            if self.phase != 0:
                self.betlog.append(tuple([self.gamenum, self.phase, self.betidx, resagent.name, resagent.style, betact, callamt, self.blind, resagent.balance, self.pot] + \
                                         list(self.log_comm_cards()) + list(self.log_hole_cards(resagent))  + \
                                         [self.eval_hand(resagent, self.flop1, self.flop2, self.flop3, self.turn, self.river)] ))

        return checkflag, checkflag, foldflag

    # Purpose   : The players take turn to take action and resolve any bets that need to be called
    # Note      : Utilize the player object's allbets attribute to track whether there is any imbalance. If so,
    #               then the other player needs to respond.    
    def bet_phase(self): 
        if (self.agent1.balance == 0) | (self.agent2.balance == 0):
            return

        agent1_check = 0 # this is just a flag to indicate that agent1's action is over
        agent2_check = 0
        loop_cnt = 0 # prevent infinite loop

        while (agent1_check == 0) | (agent2_check == 0):
            loop_cnt += 1
            if self.agent1.allbets > self.agent2.allbets: # agent2 to respond
                agent1_check, agent2_check, self.agent2_fold = self.responding(self.agent1, self.agent2, 2)

            elif self.agent1.allbets < self.agent2.allbets: # agent1 to respond
                agent1_check, agent2_check, self.agent1_fold = self.responding(self.agent2, self.agent1, 1)

            else:
                if agent1_check == 0: # agent 1 to act
                    agent1_check = self.opening(self.agent1, self.agent2, 1)
                elif agent2_check == 0: # agent 2 to act
                    agent2_check = self.opening(self.agent2, self.agent1, 2)

            if loop_cnt > 100:
                print 'ERROR: break loop'
                sys.exit(1)

    # if someone folds, then resolve the game and the other player wins the pot
    def fold_audit(self):
        if (self.agent1_fold == 1) | (self.agent2_fold == 1):
            if self.agent1_fold == 1:
                self.agent2.wins(self.pot)
                print '  Result: %s folds.' % self.agent1.name, '%s wins $%d' % (self.agent2.name, self.pot)
            else:
                self.agent1.wins(self.pot)
                print '  Result: %s folds.' % self.agent2.name, '%s wins $%d' % (self.agent1.name, self.pot)
            print self.agent1
            print self.agent2
            print " "
            return 1
        return 0

    # Purpose   : This method plays out the entire game, from players paying the blinds, shuffling the deck and 
    #               dealing hole cards, to betting and dealing the community cards in each phase and resolving the 
    #               game to find the winner
    def play(self):
        self.elapsed += 45  # collecting and shuffling the deck
        self.bets(self.agent2, self.blind, blind=' small blind', printpot=0)# bet small blind
        self.bets(self.agent1, self.blind*2, blind=' big blind')            # bet big blind

        self.phase += 1
        self.agent2.hole1 = self.deck.deal1()
        self.agent1.hole1 = self.deck.deal1()
        self.agent2.hole2 = self.deck.deal1()
        self.agent1.hole2 = self.deck.deal1()
        self.elapsed += 5
        if self.prompt == 0: 
            print '   ', self.agent1.name, 'gets hole cards', self.agent1.hole1, self.agent1.hole2 
            print '   ', self.agent2.name, 'gets hole cards', self.agent2.hole1, self.agent2.hole2
        elif self.prompt == 1:
            print '   ', self.agent1.name, 'gets hole cards ***', self.agent1.hole1, self.agent1.hole2, '***'
            print '   ', self.agent2.name, 'gets hole cards XX XX'
        else:
            print '   ', self.agent1.name, 'gets hole cards XX XX' 
            print '   ', self.agent2.name, 'gets hole cards ***', self.agent2.hole1, self.agent2.hole2, '***'
        self.bet_phase()
        if self.fold_audit():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.flop1, self.flop2, self.flop3 = self.deck.deal3()
        self.elapsed += 15
        print '  Flop is ***', self.flop1, self.flop2, self.flop3, '***'
        self.bet_phase()
        if self.fold_audit():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.turn = self.deck.deal1()
        self.elapsed += 7
        if self.prompt == 0:
            print '  Turn is %s.  Community cards are: %s %s %s %s' % (self.turn, self.flop1, self.flop2, self.flop3, self.turn)
        else:
            print '  Turn is %s.  Community cards are: *** %s %s %s %s ***' % (self.turn, self.flop1, self.flop2, self.flop3, self.turn)
        self.bet_phase()
        if self.fold_audit():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.river = self.deck.deal1()
        self.elapsed += 7
        if self.prompt == 0:
            print '  River is %s. Community cards are: %s %s %s %s %s' % (self.river, self.flop1, self.flop2, self.flop3, self.turn, self.river)
        else:
            print '  River is %s. Community cards are: *** %s %s %s %s %s ***' % (self.river, self.flop1, self.flop2, self.flop3, self.turn, self.river)
        self.bet_phase()
        if self.fold_audit():
            return

        print " "
        agent1_hand = Hand(self.agent1.hole1, self.agent1.hole2, self.flop1, self.flop2, self.flop3, self.turn, self.river)
        print "  %s's hand " % self.agent1.name, agent1_hand, "is a %s" % agent1_hand.hand_name
        agent2_hand = Hand(self.agent2.hole1, self.agent2.hole2, self.flop1, self.flop2, self.flop3, self.turn, self.river)
        print "  %s's hand " % self.agent2.name, agent2_hand, "is a %s" % agent2_hand.hand_name
        if agent1_hand.hand_rank > agent2_hand.hand_rank:
            self.agent1.wins(self.pot)
            print '  Result: %s wins $%d with %s' % (self.agent1.name, self.pot, agent1_hand.hand_name)
        elif agent2_hand.hand_rank > agent1_hand.hand_rank:
            self.agent2.wins(self.pot)
            print '  Result: %s wins $%d with %s' % (self.agent2.name, self.pot, agent2_hand.hand_name)
        else:
            print '  Result: Draw. '
            self.agent1.wins(self.pot/2)
            self.agent2.wins(self.pot/2)
        print self.agent1
        print self.agent2
        print " "
        self.elapsed += 45
