#execfile("hand.py")
#execfile("card.py")
#a.append(tuple([2, 3, ]+list(dodo())+list(dodo())+list(dodo()) ))

dict={1:'a', 2:'b', 3:'d'}
print len(dict)
import random
for i in range(10):
    print random.choice(range(1,len(dict)+1))

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
