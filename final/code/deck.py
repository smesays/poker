# Code      : /code/deck.py
# Written by: LIU, Jiun Ee (G)
# Purpose   : This class is used to represent a deck of 52 cards

import time
import numpy.random as random 

class Deck():
    def __init__(self):
        self.counter = -1
        self.deck=[]
        for i in range(1,53):
            self.deck.append(Card(i))
        self.shuffle(int(time.time()*random.uniform(0,1)/10000))

    def shuffle(self,seed): # shuffle the deck by providing a seed number
        random.seed(seed)
        random.shuffle(self.deck)
        
    def deal1(self): # deal next card
        self.counter += 1
        return self.deck[self.counter]
        
    def deal3(self): # deal next 3 cards (for flop)
        return self.deal1(), self.deal1(), self.deal1()

    def __str__(self):
        temp=''
        for i in self.deck:
            temp = temp + i.show() + ' '
        return "%s" % temp
