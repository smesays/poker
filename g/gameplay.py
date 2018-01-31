# add logic to ensure minimum raise, re-raise and bet
# fix raise all-in and loop.
# fix do not ask raise or check or ... when $0
# after last all-in raise, still need to call
import sys

class Gameplay():
    # when initializing, agents should be ordered so they go first alternately
    GAME_INDENT = 66    # number of spaces to indent the game messages

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
        self.minchip = minchip # all bets should be in multiples of smallest chip denomination
        self.prompt = prompt

        self.pot = 0 # total amt of chips in the pot
        self.phase = 0 # track the phase of the game
        self.betidx = -1
        self.betlog = [] # tuple (phase, betidx, agent, amt) is there a way to not store agent class? store 1 or 2 instead
        self.agent1_fold = 0
        self.agent2_fold = 0
        self.stop = 0

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

    def bets(self, agent, amt, betact='b', blind='', printpot=1):
        # if have time, do minimum denom of $5, and progressively going up
        if amt > agent.balance:
            amt = agent.balance

        map_act = {'b':'bets', 'c':'calls', 'r':'raises'}
        self.betidx += 1
        agent.bets(amt)
        print '    %s %s%s $%d.' % (agent.name, map_act[betact], blind, amt), agent
        self.to_pot(amt)
        if (self.prompt != 0) & printpot == 1:
            print '  Pot has $%d' % self.pot
        self.betlog.append(tuple([self.gamenum, self.phase, self.betidx, agent.name, agent.style, betact, amt, self.blind, agent.balance, self.pot] + \
                                 list(self.log_comm_cards()) + list(self.log_hole_cards(agent)) ))

# how to figure out when to reveal hole cards to the log?
    def raiseamt_audit(self, betagent, resagent, betact, raiseamt):
#        print 'raisechk', betact, raiseamt
        # by changing the raise amount due to opponent's balance, we are changing the betamt/balance=1 to something smaller.
        # might influence the NN model?
        if resagent.balance == 0:
#            print 'raisechk 1'
            return 'c', 0
        elif raiseamt > resagent.balance:
#            print 'raisechk 2'
            return betact, resagent.balance
#        print 'raisechk 3'
        return betact, raiseamt
    
    def res_audit(self, resagent, callamt, resact, resamt):
#        print "res audit"
        if resact == 'r' or resact == 'a':
#            print "res audit bef", resact, resamt
            if resagent.balance == callamt:
                print " "*self.GAME_INDENT, "%s, you can't raise, only call by going all-in." % (resagent.name)
                return 'c', 0
        return resact, resamt

    def bet_audit(self, betagent, betact, betamt, resagent):
        if betact == 'b' or betact == 'r':
#            print 'bet audit bef', betact, betamt
            if betamt > resagent.balance: # cannot bet more than opponent's balance
                betamt = resagent.balance
#            print 'bet audit aft', betact, betamt
        return betact, betamt
            
    def print_action_txt(self, agent):
        return 'Action to %s. (Hole: %s %s, $%d left)' % (agent.name, agent.hole1, agent.hole2, agent.balance)

    def print_call_option_txt(self, betagent, resagent, callamt):
        if (betagent.balance == 0) | (resagent.balance == 0) | (resagent.balance == callamt):
#            print 'print call option 1'
            return '> (C)all $%d, or (F)old? Enter c, or f: ' % callamt
        return '> (C)all $%d, (R)aise, (A)ll-in $%d, or (F)old? Enter c, r, a, or f: ' % (callamt, min(betagent.balance, resagent.balance))

    def opening(self, betagent, resagent, prompt): # opening with betting or checking
        betagent_check = 0
        if self.prompt == prompt:
            print " "*self.GAME_INDENT, "%s" % self.print_action_txt(betagent)
            betact = raw_input('                                                                   > Chec(K), (B)et, or (A)ll-in? Enter k, b, or a: ').lower()
            betamt = 0
            if betact == 'b':
                betamt = input('                                                                   > Enter the amount to bet: ')
        else:
            betact, betamt = betagent.responds(self.blind, self.pot, 0, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)
#        print 'opening ', betact, betamt
        betact, betamt = self.bet_audit(betagent, betact, betamt, resagent)
#        print 'after betaudit ', betact, betamt

        if betact == 'k':
            betagent_check = 1 
            print "    %s checks." % betagent.name
            self.betlog.append(tuple([self.gamenum, self.phase, self.betidx, betagent.name, betagent.style, betact, betamt, self.blind, betagent.balance, self.pot] + \
                                     list(self.log_comm_cards()) + list(self.log_hole_cards(betagent)) ))
        elif betact == 'a':
# logic here is a bit of a mess because of using the same agent.responds .... see if can tighten it up
            betact = 'r'
            betamt = betagent.balance
#            print 'before raiseamt audit', betact, betamt
            betact, betamt = self.raiseamt_audit(betagent, resagent, betact, betamt)
#            print 'after raiseamt audit', betact, betamt
            self.bets(betagent, betamt)
        else: 
            self.bets(betagent, betamt)

        return betagent_check

    def responding(self, betagent, resagent, prompt): # responding to a bet
        callamt = betagent.allbets - resagent.allbets 
        if self.prompt == prompt: # human agent2 to respond
            print " "*self.GAME_INDENT, "%s" % self.print_action_txt(resagent)
            print " "*self.GAME_INDENT, "%s" % self.print_call_option_txt(resagent, betagent, callamt),
            betact = raw_input().lower()
#            while betact != 'c' and betact != 'r' and betact != 'a' and betact != 'f'
            betamt = 0
            if betact == 'r':
                betamt = input('                                                                   > Enter the amount to raise: ')
        else:
#            print 'betting 1 ne 2 bot respond'
            betact, betamt = resagent.responds(self.blind, self.pot, callamt, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)
            if betamt < 0:
                print 'what is this1?'
                resagent.balance = 0
#            print betact, betamt
        betact, betamt = self.res_audit(resagent, callamt, betact, betamt)

        foldflag = 0
        if betact == 'c':
            self.bets(resagent, callamt, 'c')
            checkflag = 1
        elif (betact == 'r') | (betact == 'a'):
#            print 'betting 1 ne 2 r or a'
            if betact == 'a':
                betact = 'r'
                betamt = resagent.balance - callamt
            betact, betamt = self.raiseamt_audit(resagent, betagent, betact, betamt)
#            print 'after raisechk'
            if betact == 'c':
                self.bets(resagent, callamt, 'c')
                checkflag = 1
            else:
                self.bets(resagent, callamt, 'c', printpot=0)
                self.bets(resagent, betamt, 'r')
                checkflag = 0
        else:
            foldflag = 1
            checkflag = 1                        
            # when we log for the fold action, we need to include the callamt because callamt / potsize is the ratio that is meaning
            # to cause a player to fold
            self.betlog.append(tuple([self.gamenum, self.phase, self.betidx, resagent.name, resagent.style, betact, callamt, self.blind, resagent.balance, self.pot] + \
                                     list(self.log_comm_cards()) + list(self.log_hole_cards(resagent)) ))

        return checkflag, checkflag, foldflag

    def bet_phase(self): # last round bet should be all in and not leave amt smaller than next blind!
        if (self.agent1.balance == 0) | (self.agent2.balance == 0):
            return

        agent1_check = 0 # this is just a flag to indicate that agent1's action is over
        agent2_check = 0
        loop_cnt = 0 # prevent infinite loop

        while (agent1_check == 0) | (agent2_check == 0):
            loop_cnt += 1
            if self.agent1.allbets > self.agent2.allbets: # agent2 to respond
#                print 'betting 1>2'
                agent1_check, agent2_check, self.agent2_fold = self.responding(self.agent1, self.agent2, 2)

            elif self.agent1.allbets < self.agent2.allbets: # agent1 to respond
#                print 'betting 1<2'
                agent1_check, agent2_check, self.agent1_fold = self.responding(self.agent2, self.agent1, 1)

            else:
#                print 'betting bal=bal'
                if agent1_check == 0: # agent 1 to act
                    agent1_check = self.opening(self.agent1, self.agent2, 1)
                elif agent2_check == 0: # agent 2 to act
                    agent2_check = self.opening(self.agent2, self.agent1, 2)

            if loop_cnt > 20:
                print 'ERROR: break loop'
                sys.exit(1)

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

    def play(self):
#        print '  Deck is:', self.deck
        self.bets(self.agent2, self.blind, blind=' small blind', printpot=0)# bet small blind
        self.bets(self.agent1, self.blind*2, blind=' big blind')            # bet big blind

        self.phase += 1
        self.agent2.hole1 = self.deck.deal1()
        self.agent1.hole1 = self.deck.deal1()
        self.agent2.hole2 = self.deck.deal1()
        self.agent1.hole2 = self.deck.deal1()
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
        print '  Flop is ***', self.flop1, self.flop2, self.flop3, '***'
        self.bet_phase()
        if self.fold_audit():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.turn = self.deck.deal1()
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
            print '  Result: ', self.agent1.name, 'wins $', self.pot, 'with', agent1_hand.hand_name
        elif agent2_hand.hand_rank > agent1_hand.hand_rank:
            self.agent2.wins(self.pot)
            print '  Result: ', self.agent2.name, 'wins $', self.pot, 'with', agent2_hand.hand_name
        else:
            print '  Result: Draw. '
            self.agent1.wins(self.pot/2)
            self.agent2.wins(self.pot/2)
        print self.agent1
        print self.agent2
        print " "
