execfile("hand.py")
execfile("card.py")
hand1=Hand(Card(1),Card(14),Card(40),Card(13),Card(51))

val='a'
temptxt=' '*10, 'this is bad %s' % val
a=raw_input(temptxt)
print a

print ' '*10, 'this is bad %s' % val,
a = raw_input('> ')
print a


'''
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
