#execfile("hand.py")
#execfile("card.py")
#a.append(tuple([2, 3, ]+list(dodo())+list(dodo())+list(dodo()) ))

import time
import numpy as np
for i in range(30):
#    print time.time()
    print int(time.time()*np.random.uniform(0,1)/10000)

#hand1=Hand(Card(1),Card(14),Card(40),Card(13),Card(51))

''' Figure out if hole card is in the best hand
if Card(3) in hand1.cards:
    print 'Try: Yes'
else:
    print 'Try: No'
print 'Answer is No'

for i in range(len(hand1.cards)):
    if Card(3) == hand1.cards[i]:
        print 'Try %d : Yes'
    else:
        print 'Try %d : No'

print hand1.hand_name
print hand1.hand_type
print hand1.hand_rank
'''
