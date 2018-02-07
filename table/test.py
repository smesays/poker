execfile('../g/card.py')
execfile('../g/hand.py')
import pickle

# reading mapping file to map rank to 4-digit integer
pkl_file = open('rank_map_dict.pkl', 'rb')
rank_map_dict = pickle.load(pkl_file)
pkl_file.close()
pkl_file = open('hand7_prob_2pct_old.pkl', 'rb')
hand7_cnt_dict = pickle.load(pkl_file)
pkl_file.close()
print len(hand7_cnt_dict)

'''
ranklist=[]
for key, value in rank_map_dict.iteritems():
    ranklist.append((key,value))
print len(ranklist)
#print ranklist
for i in sorted(ranklist):
    print i
'''

flop1=Card(6)
flop2=Card(2)
flop3=Card(3)
turn =Card(4)
river=Card(5)

hole1=Card(20)
hole2=Card(34)


def map_handrank(hand):
    if hand.hand_rank < 10000:
        handrank = rank_map_dict['0%10.4f'%hand.hand_rank]
    else:
        handrank = rank_map_dict['%10.4f'%hand.hand_rank]
    return handrank

hand5=Hand(flop1,flop2,flop3,turn,river)
hand7=Hand(flop1,flop2,flop3,turn,river,hole1,hole2)
print hand5, map_handrank(hand5), hand5.hand_name
print hand7, map_handrank(hand7), hand7.hand_name

hand7_list = hand7_cnt_dict[map_handrank(hand5)]
print hand7_list

'''
better_hole_cnt = 0
for (key,value) in sorted(hand7_list, reverse=True):
    if map_handrank(hand7) < key:
        better_hole_cnt += value

win_prob = 1.0 - better_hole_cnt * 1.0 / 1081
'''
