execfile('../g/card.py')
execfile('../g/hand.py')
from collections import defaultdict
import pickle
import time

begtime=time.time()

hand_imp_dict={}
start=1
end=52
holebeg=1
holeend=52
for a in range(start,end+1):
    for b in range(start,end+1):
        if a < b:
            for c in range(start,end+1):
                if b < c:
                    for d in range(start,end+1):
                        if c < d:
                            for e in range(start,end+1):
                                if d < e:
                                    hand5=Hand(Card(a),Card(b),Card(c),Card(d),Card(e))
                                    rank_dict=defaultdict(int)
                                    if '%.4f' % hand5.hand_rank not in hand_imp_dict:
                                        holecnt=0
                                        for h1 in range(holebeg,holeend+1):
                                            if h1 != a and h1 != b and h1 != c and h1 != d and h1 != e:
                                                for h2 in range(holebeg,holeend+1):
                                                    if h1 < h2 and h2 != a and h2 != b and h2 != c and h2 !=d and h2 !=e:
                                                        holecnt+=1
                                                        hand7=Hand(Card(h1),Card(h2),Card(a),Card(b),Card(c),Card(d),Card(e))
#                                                        if '%.4f' % hand5.hand_rank != '%.4f' % hand7.hand_rank:
                                                        rank_dict['%.4f' % hand7.hand_rank] += 1
                                    if holecnt != 1081:
                                        print hand5.hand_rank, 'holecnt ne 1081'
                                    hand_imp_dict['%.4f' % hand5.hand_rank]=rank_dict

                                    output = open('../table/hand7_cnt_dict.pkl', 'a')
                                    pickle.dump(hand_imp_dict, output)
                                    output.close()

print len(hand_imp_dict)
print 'search took (min)', int((time.time() - begtime)/60)

'''
begtime=time.time()
# write dict to file
output = open('../table/hand7_cnt_dict.pkl', 'wb')
pickle.dump(hand_imp_dict, output)
output.close()
print 'saving took (min)', int((time.time() - begtime)/60)
'''
