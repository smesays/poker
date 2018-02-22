# Code      : card.py
# Written by: LIU, Jiun Ee (G)
# Purpose   : This class is used to represent a single card in a deck of cards

class Card(object):
    ''' Values of card attribute
         1-13: Ace to K for spades
        14-26: Ace to K for hearts
        27-39: Ace to K for clubs
        40-52: Ace to K for diamonds
    '''
    map_rank = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'10',11:'J',12:'Q',13:'K',14:'A'}
    map_suit = {1:'S',2:'H',3:'C',4:'D'}
    
    def __init__(self,card):
        self.card=card
        
    def getSuit(self):
        if 1 <= self.card <= 13:
            return 1
        elif 14 <= self.card <= 26:
            return 2
        elif 27 <= self.card <= 39:
            return 3
        return 4
        
    def getRank(self):
        if self.card in (13,26,39,52):
            return 13
        elif self.card in (1,14,27,40):
            return 14
        return self.card % 13
        
    def show(self):
        return self.map_rank[self.getRank()] + self.map_suit[self.getSuit()]
        
    def __str__(self):
        return "%s" % (self.show())
