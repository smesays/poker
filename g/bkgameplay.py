# fix raise all-in and loop.
# fix do not ask raise or check or ... when $0
# after last all-in raise, still need to call
class Gameplay():
    # when initializing, agents should be ordered so they go first alternately
    GAME_INDENT = 66    # number of spaces to indent the game messages

    def __init__(self, agent1, agent2, blind, prompt):
        '''
        prompt determines whether we need to prompt for human response 
        prompt = 0 is bots play
        prompt = 1 will prompt for responses from agent1, and similarly for 2
        '''
        self.agent1 = agent1
        self.agent1.clear_bets()
        self.agent2 = agent2
        self.agent2.clear_bets()
        self.blind = blind
        self.prompt = prompt

        self.pot = 0 # total amt of chips in the pot
        self.phase = 0 # track the phase of the game
        self.betidx = -1
        self.bet = [] # tuple (phase, betidx, agent, amt) is there a way to not store agent class? store 1 or 2 instead
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
        
#    def getCurrentBet(self):
#        return self.bet[-1][3]
    
    def bets(self, agent, amt, actname='b', blind='', printpot=1):
        # if have time, do minimum denom of $5, and progressively going up
        if amt > agent.balance:
            amt = agent.balance

        map_act = {'b':'bets', 'c':'calls', 'r':'raises'}
        self.betidx += 1
        agent.bets(amt)
        print '    %s %s%s $%d.' % (agent.name, map_act[actname], blind, amt), agent
        self.to_pot(amt)
        if (self.prompt != 0) & printpot == 1:
            print '  Pot has $%d' % self.pot
        self.bet.append((self.phase, self.betidx, agent, amt))

    def raiseamt_check(self, betagent, resagent, betact, raiseamt):
        print 'raisechk'
        print betact, raiseamt
        # by changing the raise amount due to opponent's balance, we are changing the betamt/balance=1 to something smaller.
        # might influence the NN model?
        if resagent.balance == 0:
            print 'raisechk 1'
            return 'c', 0
        elif raiseamt > resagent.balance:
            print 'raisechk 2'
            return betact, resagent.balance
        print 'raisechk 3'
        return betact, raiseamt

    def human_check(self, agent, callamt, betact, betamt):
        print "human check"
        if betact == 'r':
            print "human check r"
            if agent.balance == callamt:
                print " "*self.GAME_INDENT, "%s, you can only call going all-in." % (agent.name)
                return 'c', 0
        return betact, betamt
            
    def print_action_txt(self, agent):
        return 'Action to %s. (Hole: %s %s, $%d left)' % (agent.name, agent.hole1, agent.hole2, agent.balance)

    def print_call_option_txt(self, betagent, resagent, callamt):
        if (betagent.balance == 0) | (resagent.balance == 0):
            print 'print call option 1'
            return '> (C)all $%d, or (F)old? Enter c, or f: ' % callamt
        return '> (C)all $%d, (R)aise, (A)ll-in $%d, or (F)old? Enter c, r, a, or f: ' % (callamt, min(betagent.balance, resagent.balance))

    def betting(self): # last round bet should be all in and not leave amt smaller than next blind!
        if (self.agent1.balance == 0) | (self.agent2.balance == 0):
            return

        agent1_check = 0
        agent2_check = 0

        while (agent1_check == 0) | (agent2_check == 0):
            if self.agent1.allbets > self.agent2.allbets: # agent2 to respond
                print 'betting 1>2'
                callamt = self.agent1.allbets - self.agent2.allbets 
                if self.prompt == 2: # human agent2 to respond
                    print " "*self.GAME_INDENT, "%s" % self.print_action_txt(self.agent2)
#                    print ' '*self.GAME_INDENT, '> (C)all $%d, (R)aise, (A)ll-in $%d, or (F)old? Enter c, r, a, or f: ' % (callamt, min(self.agent1.balance, self.agent2.balance)),
                    print " "*self.GAME_INDENT, "%s" % self.print_call_option_txt(self.agent2, self.agent1, callamt),
                    betact = raw_input()
                    betact = betact.lower()
                    betamt = 0
                    if betact == 'r':
                        betamt = input('                                                                   > Enter the amount to raise: ')
                    betact, betamt = self.human_check(self.agent2, callamt, betact, betamt)
                else:
                    print 'betting 1>2 bot respond'
                    betact, betamt = self.agent2.responds(self.pot, callamt, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)

                if betact == 'c':
                    self.bets(self.agent2, callamt, 'c')
                    agent1_check = agent2_check = 1
                elif (betact == 'r') | (betact == 'a'):
                    print 'betting 1>2 r or a'
                    if betact == 'a':
                        betact = 'r'
                        betamt = self.agent2.balance - callamt
                    betact, betamt = self.raiseamt_check(self.agent2, self.agent1, betact, betamt)
                    print 'after raisechk'
                    print betact, betamt
                    if betact == 'c':
                        self.bets(self.agent2, callamt, 'c')
                        agent1_check = agent2_check = 1
                    else:
                        self.bets(self.agent2, callamt, 'c', printpot=0)
                        self.bets(self.agent2, betamt, 'r')
                        agent1_check = agent2_check = 0
                else:
                    self.agent2_fold = 1
                    agent1_check = agent2_check = 1                        

            elif self.agent1.allbets < self.agent2.allbets: # agent1 to respond
                print 'betting 1<2'
                callamt = self.agent2.allbets - self.agent1.allbets
                if self.prompt == 1: # human agent1 to respond
                    print " "*self.GAME_INDENT, "%s" % self.print_action_txt(self.agent1)
#                    print ' '*self.GAME_INDENT, '> (C)all $%d, (R)aise, (A)ll-in $%d, or (F)old? Enter c, r, a, or f: ' % (callamt, min(self.agent1.balance, self.agent2.balance)),
                    print " "*self.GAME_INDENT, "%s" % self.print_call_option_txt(self.agent2, self.agent1, callamt),
                    betact = raw_input('')
                    betact = betact.lower()
                    betamt = 0
                    if betact == 'r':
                        betamt = input('                                                                   > Enter the amount to raise: ')
                    betact, betamt = self.human_check(self.agent1, callamt, betact, betamt)
                else:
                    print 'betting 1<2 bot respond'
                    betact, betamt = self.agent1.responds(self.pot, callamt, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)
                    print betact, betamt

                if betact == 'c':
                    self.bets(self.agent1, callamt, 'c')
                    agent1_check = agent2_check = 1
                elif (betact == 'r') | (betact == 'a'):
                    print 'betting 1<2 r or a'
                    if betact == 'a':
                        betact = 'r'
                        betamt = self.agent1.balance - callamt
                    betact, betamt = self.raiseamt_check(self.agent1, self.agent2, betact, betamt)
                    print 'after raisechk'
                    print betact, betamt
                    if betact == 'c':
                        self.bets(self.agent1, callamt, 'c')
                        agent1_check = agent2_check = 1
                    else:
                        self.bets(self.agent1, callamt, 'c', printpot=0)
                        self.bets(self.agent1, betamt, 'r')
                        agent1_check = agent2_check = 0
                else:
                    self.agent1_fold = 1
                    agent1_check = agent2_check = 1

            else:
                print 'betting bal=bal'
                if self.prompt == 0: # for now, computers are dumb, always bet min and call
                    print 'betting bal=bal 1'
                    if 1 == 1: # evaluate hole cards
                        betamt = self.blind*2
                        self.bets(self.agent1, betamt) # amt determined by play style
                    if 1 == 1:
                        self.bets(self.agent2, self.agent1.allbets - self.agent2.allbets)
                    agent1_check = agent2_check = 1
                else:
                    print 'betting bal=bal 2'
                    if agent1_check == 0: # agent 1 to act
                        print 'betting bal=bal 2a'
                        if self.prompt == 1: # agent 1 is human
                            print " "*self.GAME_INDENT, "%s" % self.print_action_txt(self.agent1)
                            betact = raw_input('                                                                   > Chec(K), (B)et, or (A)ll-in? Enter k, b, or a: ')
                            betact = betact.lower()
                            if betact == 'b':
                                betamt = input('                                                                   > Enter the amount to bet: ')
                        else:
                            print 'betting 1=2 bot1 respond'
                            betact, betamt = self.agent1.responds(self.pot, 0, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)

                        if betact == 'k':                    
                            agent1_check = 1
                            print "    %s checks." % self.agent1.name
                        elif betact == 'a':
                            betact = 'r'
                            betamt = self.agent1.balance
                            betact, betamt = self.raiseamt_check(self.agent1, self.agent2, betact, betamt)
                            self.bets(self.agent1, betamt)
                        else:
                            self.bets(self.agent1, betamt)

                    elif agent2_check == 0: # agent 2 to act
                        print 'betting bal=bal 2b'
                        if self.prompt == 2: # agent 2 is human
                            print " "*self.GAME_INDENT, "%s" % self.print_action_txt(self.agent2)
                            betact = raw_input('                                                                   > Chec(K), (B)et, or (A)ll-in? Enter k, b, or a: ')
                            betact = betact.lower()
                            if betact == 'b':
                                betamt = input('                                                                   > Enter the amount to bet: ')
                        else:
                            print 'betting 1=2 bot2 respond'
                            betact, betamt = self.agent2.responds(self.pot, 0, card1=self.flop1, card2=self.flop2, card3=self.flop3, card4=self.turn, card5=self.river)

                        if betact == 'k':
                            agent2_check = 1
                            print "    %s checks." % self.agent2.name
                        elif betact == 'a':
                            betact = 'r'
                            betamt = self.agent2.balance
                            betact, betamt = self.raiseamt_check(self.agent2, self.agent1, betact, betamt)
                            self.bets(self.agent2, betamt)
                        else: 
                            self.bets(self.agent2, betamt)

    def fold_check(self):
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
        self.betting()
        if self.fold_check():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.flop1, self.flop2, self.flop3 = self.deck.deal3()
        print '  Flop is ***', self.flop1, self.flop2, self.flop3, '***'
        self.betting()
        if self.fold_check():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.turn = self.deck.deal1()
        if self.prompt == 0:
            print '  Turn is %s.  Community cards are: %s %s %s %s' % (self.turn, self.flop1, self.flop2, self.flop3, self.turn)
        else:
            print '  Turn is %s.  Community cards are: *** %s %s %s %s ***' % (self.turn, self.flop1, self.flop2, self.flop3, self.turn)
        self.betting()
        if self.fold_check():
            return

        self.phase += 1
        _ = self.deck.deal1() # burns a card from the deck
        self.river = self.deck.deal1()
        if self.prompt == 0:
            print '  River is %s. Community cards are: %s %s %s %s %s' % (self.river, self.flop1, self.flop2, self.flop3, self.turn, self.river)
        else:
            print '  River is %s. Community cards are: *** %s %s %s %s %s ***' % (self.river, self.flop1, self.flop2, self.flop3, self.turn, self.river)
        self.betting()
        if self.fold_check():
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
