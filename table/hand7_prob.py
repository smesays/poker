execfile('../g/card.py')
execfile('../g/hand.py')
from collections import defaultdict
import pickle
import time

# reading mapping file to map rank to 4-digit integer
pkl_file = open('rank_map_dict.pkl', 'rb')
rank_map_dict = pickle.load(pkl_file)
pkl_file.close()

begtime=time.time()

start=1
end=52
holebeg=1
holeend=52

hand_imp_dict={}
hand_imp_dictkey={}
rankcnt=0
#output = open('hand7_prob.pkl', 'a+b')
for a in range(start,13+1): # performing first card search for 1 suit. other suits are redundant
    print 'first card ', a
    for b in range(start,end+1):
        if a < b:
            for c in range(start,end+1):
                if b < c:
                    for d in range(start,end+1):
                        if c < d:
                            for e in range(start,end+1):
                                if d < e:
#                                    hand_imp_dict={}                                    
                                    hand5=Hand(Card(a),Card(b),Card(c),Card(d),Card(e))
                                    if hand5.hand_rank < 10000:
                                        hand5_shortrank=rank_map_dict['0%10.4f' % hand5.hand_rank]
                                    else:
                                        hand5_shortrank=rank_map_dict['%10.4f' % hand5.hand_rank]
                                    if hand5_shortrank not in hand_imp_dictkey:
                                        rankcnt+=1
                                        print rankcnt
                                        rank_dict=defaultdict(int)
                                        holecnt=0
                                        for h1 in range(holebeg,holeend+1):
                                            if h1 != a and h1 != b and h1 != c and h1 != d and h1 != e:
                                                for h2 in range(holebeg,holeend+1):
                                                    if h1 < h2 and h2 != a and h2 != b and h2 != c and h2 !=d and h2 !=e:
                                                        holecnt+=1
                                                        hand7=Hand(Card(h1),Card(h2),Card(a),Card(b),Card(c),Card(d),Card(e))
                                                        if hand7.hand_rank < 10000:
                                                            hand7_shortrank=rank_map_dict['0%10.4f' % hand7.hand_rank]
                                                        else:
                                                            hand7_shortrank=rank_map_dict['%10.4f' % hand7.hand_rank]
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
                                        # store the actual count instead of probability to save space.
                                        # we know there are 1081 combinations of hole cards to divide and get probability.
                                        # only output every time there is an increment of 2% in probability, to cut down size
                                        if int(cumcnt*100/1081) - int(prevcnt*100/1081) >= 2:
                                            if hand5_shortrank != rl[0]:    # only store ranks that improved from the community cards
                                                prob_list.append((rl[0],cumcnt))
                                            prevcnt = cumcnt
                                    hand_imp_dictkey[hand5_shortrank] = 1
                                    hand_imp_dict[hand5_shortrank] = prob_list
#                                    print hand_imp_dict
                                    # this will serially dump into separate dictionaries, and have to read them 7462 times
#                                    pickle.dump(hand_imp_dict, output)
output = open('hand7_prob_2pct.pkl', 'wb')
pickle.dump(hand_imp_dict, output)
output.close()
#                                    print hand_imp_dict
#                                    f = open("hand7_prob.txt", "a")
#                                    f.write(str(hand_imp_dict[0]))
#                                    f.write(',')
#                                    f.write(str(hand_imp_dict[1]))
#                                    f.write("\n")
#                                    f.close()
#print len(hand_imp_dict)
#print hand_imp_dict
print 'search took (min)', int((time.time() - begtime)/60)
