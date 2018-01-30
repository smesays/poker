import random 

class Deck():
    def __init__(self):
        self.counter = -1
        self.deck=[]
        for i in range(1,53):
            self.deck.append(Card(i))
        self.shuffle(random.choice([4,5,6,7,8,9,10,11,42,25,476,5,58])) # change this later to timestamp based

    def shuffle(self,seed): # shuffle the deck by providing a seed number
        random.seed(seed)
        random.shuffle(self.deck)
        
    def __str__(self):
        temp=''
        for i in self.deck:
            temp = temp + i.show() + ' '
        return "%s" % temp
# does declaring __iter__ and next makes it generic for other codes because it's consistent with regular container?
#    def __iter__(self):
#        return self
    def deal1(self): # deal next card
        self.counter += 1
        return self.deck[self.counter]
        
    def deal3(self): # deal flop
        return self.deal1(), self.deal1(), self.deal1()
