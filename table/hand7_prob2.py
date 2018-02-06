execfile('../g/card.py')
execfile('../g/hand.py')
from collections import defaultdict
import pickle
import time

begtime=time.time()

start=1
end=52
holebeg=1
holeend=52

hand_imp_dict={}
for a in range(1,4):
    for b in range(7,8):
        if a < b:
            for c in range(10,11):
                if b < c:
                    for d in range(21,22):
                        if c < d:
                            for e in range(50,51):
                                if d < e:
                                    hand5=Hand(Card(a),Card(b),Card(c),Card(d),Card(e))
                                    if hand5.hand_rank >= 10000:
                                        hand5_shortrank='%.5f' % hand5.hand_rank
                                    else:
                                        hand5_shortrank='0%.4f' % hand5.hand_rank
                                    if hand5_shortrank not in hand_imp_dict:
                                        rank_dict=defaultdict(int)
                                        holecnt=0
                                        for h1 in range(holebeg,holeend+1):
                                            if h1 != a and h1 != b and h1 != c and h1 != d and h1 != e:
                                                for h2 in range(holebeg,holeend+1):
                                                    if h1 < h2 and h2 != a and h2 != b and h2 != c and h2 !=d and h2 !=e:
                                                        holecnt+=1
                                                        hand7=Hand(Card(h1),Card(h2),Card(a),Card(b),Card(c),Card(d),Card(e))
                                                        if hand7.hand_rank >= 10000:
                                                            hand7_shortrank='%.5f' % hand7.hand_rank
                                                        else:
                                                            hand7_shortrank='0%.4f' % hand7.hand_rank
                                                        rank_dict[hand7_shortrank] += 1

                                    if holecnt != 1081:
                                        print hand5.hand_rank, 'holecnt ne 1081'

                                    rank_list = []
                                    for key, value in rank_dict.iteritems():
                                        rank_list.append((key,value))

                                    cumcnt = 0
                                    prob_list = []
                                    prevcnt = 0
                                    for rl in sorted(rank_list):
                                        cumcnt += rl[1]
#                                        print rl[0], rl[1], cumcnt, prevcnt
                                        # store the actual count instead lf probability to save space.
                                        # we know there are 1081 combinations of hole cards to divide and get probability.
                                        if int(cumcnt*100/1081) - int(prevcnt*100/1081) >= 4: # only output every time there is an increment of 2% in probability, to cut down size
                                            prob_list.append((rl[0],cumcnt))
                                            prevcnt = cumcnt
#                                        prob_list.append((rl[0],cumcnt)) 
#                                        prob_list.append((rl[0],cumcnt/1081.0))

                                    hand_imp_dict[hand5_shortrank]=prob_list

print len(hand_imp_dict)
#print hand_imp_dict
print 'search took (min)', int((time.time() - begtime)/60)

begtime=time.time()
# write dict to file
output = open('../table/hand7_cnt_dict2.pkl', 'wb')
pickle.dump(hand_imp_dict, output)
output.close()
print 'saving took (min)', int((time.time() - begtime)/60)
