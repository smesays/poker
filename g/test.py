#execfile("hand.py")
#execfile("card.py")
#a.append(tuple([2, 3, ]+list(dodo())+list(dodo())+list(dodo()) ))
import numpy as np
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])
c = np.concatenate((a, b), axis=1)
print c

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
