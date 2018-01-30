class Hand():
    def __init__(self, card1, card2, card3, card4, card5, card6=None, card7=None):
        # self.cards, self.suit, self.rank are in original order
        if card7 is not None:
            self.cards = [card1, card2, card3, card4, card5, card6, card7]
        elif card6 is not None:
            self.cards = [card1, card2, card3, card4, card5, card6]
        else:
            self.cards = [card1, card2, card3, card4, card5]
        self.suit = [i.getSuit() for i in self.cards]
        self.rank = [i.getRank() for i in self.cards]        
        # ordered rank
        self.orank = self.rank[:]
        self.orank.sort()
        # unique rank and unique suit
        self.urank = list(set(self.orank)) # not sure why .sort() here does not work
        self.urank.sort() # UniqueRANK do we need to sort again or is it guaranteed that the set won't mess with the order?
        self.usuit = list(set(self.suit)) # UniqueSUIT
        self.hand_rank = 0.0
        self.hand_type = ''
        self.hand_name = ''
        self.best_hand = []
        if len(self.cards) == 5:
            self.best_hand = self.cards 
        self.find_best_hand()

    def iden_pairs(self):
        # output format : # of pairs, highest pair card, second highest pair card output value : {0,1,2,3}, {2,...,14}, {2,...,14}
        num_pairs=0 # number of pairs
        pairh1_rank=None # highest pair
        pairh2_rank=None # second highest pair
        # this is just a bit faster by taking care of 1 pair right away?
        if len(self.orank) - len(self.urank) == 1: # 1 pair only
            num_pairs=1
            for i in range(2,len(self.orank)+1):
                if self.orank[i-2] == self.orank[i-1]:
                    pairh1_rank=self.orank[i-2]
        else:
            # this is very similar to 3 of a kind, can we condense?
            temp_ranks=self.orank[:]
            # for ease of coding, pad left and right of list so we can easily compare to find pairs
            temp_ranks.append(0) # add a value at the beginning
            temp_ranks.append(99)# add a value at the end
            temp_ranks.sort() # sort so the list is always [0, rank1, ..., rank7, 99]
            for i in range(2,len(self.orank)+1):
                if (temp_ranks[i-1] == temp_ranks[i]) & (temp_ranks[i-1] != temp_ranks[i-2]) & (temp_ranks[i] != temp_ranks[i+1]):
                    num_pairs += 1
                    if temp_ranks[i] > pairh1_rank:
                        if pairh1_rank > pairh2_rank:
                            pairh2_rank = pairh1_rank
                        pairh1_rank=temp_ranks[i]
                    elif temp_ranks[i] > pairh2_rank:
                        pairh2_rank=temp_ranks[i]
        return num_pairs, pairh1_rank, pairh2_rank

    def iden_3ofakind(self):
        # output format : # of 3-of-a-Kind, highest 3-of-a-Kind card, second highest 3-of-a-Kind card output value : {0,1,2}, {2,...,14}, {2,...,13}
        num_three=0
        threeh1_rank=None
        threeh2_rank=None
        temp_ranks=self.orank[:]
        # for ease of coding, pad left and right of list so we can easily compare to find pairs
        temp_ranks.append(0) # add a value at the beginning
        temp_ranks.append(99)# add a value at the end
        temp_ranks.sort() # sort so the list is always [0, rank1, ..., rank7, 99]
        for i in range(3,len(self.orank)+1):
            if (temp_ranks[i-2] == temp_ranks[i]) & (temp_ranks[i-2] != temp_ranks[i-3]) & (temp_ranks[i] != temp_ranks[i+1]):
                num_three += 1
                if temp_ranks[i] > threeh1_rank:
                    if threeh1_rank > threeh2_rank:
                        threeh2_rank = threeh1_rank
                    threeh1_rank=temp_ranks[i]
                elif temp_ranks[i] > threeh2_rank:
                    threeh2_rank=temp_ranks[i]
        return num_three, threeh1_rank, threeh2_rank
        
    def iden_fullhouse(self):
        # output format : 3-of-a-Kind yes or no, 3-of-a-Kind card, high pair card output value : {0,1}, {2,...,14}, {2,...,14}
        num_three, rank1_three, rank2_three = self.iden_3ofakind()
        if num_three == 2: # 2 3-of-a-Kind, lower 3-of-a-Kind becomes pair
            return 1, rank1_three, rank2_three
        elif num_three == 1:
            num_pairs, pairh1_rank, _ = self.iden_pairs()
            if num_pairs >= 1:
                return 1, rank1_three, pairh1_rank
        return 0, None, None
        
    def iden_4ofakind(self):
        # output format : 4-of-a-Kind yes or no, 4-of-a-Kind card, high card output value : {0,1}, {2,...,14}, {2,...,14}
        for i in range(4,len(self.orank)+1):
            temp4ranks=self.orank[i-4:i]
            if temp4ranks[0] == temp4ranks[-1]:
                urank=self.urank[:]
                urank.remove(temp4ranks[0])
                return 1, temp4ranks[0], max(urank)
        return 0, None, None

    def iden_straight(self):
        # output format : straight yes or no, high card, second high card output value : {0,1}, {6,...,14}, {5,...,13}
        if len(self.urank) < 5:
            return 0, None, None
        elif (self.urank[-1] == 14) & (self.urank[3] == 5): # wheel A2345
            return 1, 14, 5
        else:
            for i in range(len(self.urank),4,-1): # do reverse do identify the largest straight first
                temp5uranks=self.urank[i-5:i]
                if temp5uranks[-1] - temp5uranks[0] == 4:
                    return 1, temp5uranks[-1], temp5uranks[-2]
        return 0, None, None

    def iden_flush(self):
        # output format : Flush yes or no, flush suit, [5 highest flush cards] output value : {0,1}, {1,2,3,4}, [{6,...,14}, {5,...,13}, {4,...,12}, {3,...,11}, {2,...,10}]
        if len(self.usuit) == 4:
            return 0, 0, []
        else:
            suitcnt=[0,0,0,0] # suit's card count
            suitcards=[]
            for s in range(len(self.suit)):
                suitcnt[self.suit[s]-1]+=1 # count number of cards for each suit
            if max(suitcnt) < 5:
                return 0, 0, []
            for s in range(1,5):
                if suitcnt[s-1] >= 5:
                    for i in range(len(self.suit)):
                        if self.suit[i] == s:
                            suitcards.append(self.rank[i])
                        suitcards.sort(reverse=True)
                    return 1, s, suitcards[:5]
        return 0, 0, []

    def iden_straightflush(self):
        # output format : Straight Flush yes or no, high card, second high card output value : {0,1}, {6,...,14}, {5,...,13}
        has_flush, flush_suit, _ = self.iden_flush()
        if has_flush & self.iden_straight()[0]: # if exists straight and flush, then we might have straight flush
            suitcards=[]
            for i in range(len(self.rank)):
                if self.suit[i] == flush_suit:
                    suitcards.append(self.rank[i]) # put all cards of flush suit here
            suitcards.sort()
            if (suitcards[-1] == 14) & (suitcards[3] == 5): # wheel straight flush
                return 1, 14, 5
            else:
                for i in range(len(suitcards),4,-1): # do reverse to identify the largest straight flush first
                    temp5uranks=suitcards[i-5:i]
                    if temp5uranks[-1] - temp5uranks[0] == 4:
                        return 1, temp5uranks[-1], temp5uranks[-2]
        return 0, 0, 0

    # Royal Flush Straight Flush Four of a Kind Full House Flush Straight Three of a Kind Two Pairs One Pair we need to optimize this, find just a matrix of a few features and 
    # compare. if same rank then only compare in detail
    def find_best_hand(self):
        map_rank = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'J',12:'Q',13:'K',14:'A'}
        has_straightflush, straightflush_high1, straightflush_high2 = self.iden_straightflush()
        if has_straightflush:
            if straightflush_high2 == 13:
                self.hand_type = 'Royal Flush'
                self.hand_name = self.hand_type
                self.hand_rank = 10300.0
            else:
                self.hand_type = 'Straight Flush'
                self.hand_name = 'Straight Flush %s %s' % (map_rank[straightflush_high1], map_rank[straightflush_high2])
                self.hand_rank = 10200 + straightflush_high1 + straightflush_high2/15.0
        else:
            has_fourkind, fourkind, fourkind_high = self.iden_4ofakind()
            if has_fourkind:
                self.hand_type = 'Four-of-a-Kind'
                self.hand_name = 'Four-of-a-Kind %s with %s' % (map_rank[fourkind], map_rank[fourkind_high])
                self.hand_rank = 10100 + fourkind + fourkind_high/15.0
            else:
                has_fullhouse, fullhouse3, fullhouse2 = self.iden_fullhouse()
                if has_fullhouse:
                    self.hand_type = 'Full House'
                    self.hand_name = 'Full House %s full of %s' % (map_rank[fullhouse3], map_rank[fullhouse2])
                    self.hand_rank = 10000 + fullhouse3 + fullhouse2/15.0
                else:
                    has_flush, _, flushranks = self.iden_flush()
                    if has_flush:
                        self.hand_type = 'Flush'
                        self.hand_name = 'Flush %s %s %s %s %s' % (map_rank[flushranks[0]], map_rank[flushranks[1]], map_rank[flushranks[2]], map_rank[flushranks[3]], map_rank[flushranks[4]])
                        self.hand_rank = 6000 + flushranks[0]*15*15 + flushranks[1]*15 + flushranks[2] + flushranks[3]/15.0 + flushranks[4]/15.0/15.0
                    else:
                        has_straight, straight_high1, straight_high2 = self.iden_straight()
                        if has_straight:
                            self.hand_type = 'Straight'
                            self.hand_name = 'Straight %s %s' % (map_rank[straight_high1], map_rank[straight_high2])
                            self.hand_rank = 5500 + straight_high1 + straight_high2/15.0
                        else:
                            num_threekind, threekind1, _ = self.iden_3ofakind()
                            if num_threekind == 1:
                                threekind_high=self.urank[:]
                                threekind_high.remove(threekind1)
                                self.hand_type = 'Three-of-a-Kind'
                                self.hand_name = 'Three-of-a-Kind %s with High Cards %s %s' % (map_rank[threekind1], map_rank[threekind_high[-1]], map_rank[threekind_high[-2]])
                                self.hand_rank = 5000 + threekind1*15 + threekind_high[-1] + threekind_high[-2]/15.0
                            else:
                                num_pairs, pairs_high1, pairs_high2 = self.iden_pairs()
                                if num_pairs >= 2:
                                    twopairs_high=self.urank[:]
                                    twopairs_high.remove(pairs_high1) # how come we can't chain .remove?
                                    twopairs_high.remove(pairs_high2)
                                    self.hand_type = 'Two Pairs'
                                    self.hand_name = 'Two Pairs %s %s with %s' % (map_rank[pairs_high1], map_rank[pairs_high2], map_rank[twopairs_high[-1]])
                                    self.hand_rank = 4500 + pairs_high1*15 + pairs_high2 + twopairs_high[-1]/15.0
                                elif num_pairs == 1:
                                    onepair_high=self.urank[:]
                                    onepair_high.remove(pairs_high1)
                                    self.hand_type = 'One Pair'
                                    self.hand_name = 'One Pair %s with High Cards %s %s %s' % (map_rank[pairs_high1], map_rank[onepair_high[-1]], map_rank[onepair_high[-2]], map_rank[onepair_high[-3]])
                                    self.hand_rank = 4000 + pairs_high1*15 + onepair_high[-1] + onepair_high[-2]/15.0 + onepair_high[-3]/15.0/15.0
                                else:
                                    self.hand_type = 'High Card'
                                    self.hand_name = 'High Cards %s %s %s %s %s' % (map_rank[self.urank[-1]], map_rank[self.urank[-2]], map_rank[self.urank[-3]], map_rank[self.urank[-4]], map_rank[self.urank[-5]])
                                    self.hand_rank = 0 + self.urank[-1]*15*15 + self.urank[-2]*15 + self.urank[-3] + self.urank[-4]/15.0 + self.urank[-5]/15.0/15.0

    def __str__(self):
        temp=''
        for i in self.cards:
            temp = temp + i.show() + ' '
        return "%s" % temp
