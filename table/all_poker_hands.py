# Code      : all_poker_hands.py
# Written by: LIU, Jiun Ee (G)
# Purpose   : DFS search of all possible 5-card poker hands, and categorize them to unique 5-card hand names
# Notes     : Rely on hand.py to return the rank of the poker hand
#             Resulting combinations and their corresponding hand ranks enable us to calculate winning probabilities

execfile('../code/card.py') 
execfile('../code/hand.py') 
from collections import defaultdict 
import pickle 

rank_cnt=defaultdict(int)
type_cnt=defaultdict(int)
start=1 
end=52

for a in range(start,end+1):
    for b in range(start,end+1):
        if a < b:
            for c in range(start,end+1):
                if b < c:
                    for d in range(start,end+1):
                        if c < d:
                            for e in range(start,end+1):
                                if d < e:
                                    hand=Hand(Card(a),Card(b),Card(c),Card(d),Card(e))
                                    type_cnt[hand.hand_type] += 1
                                    if hand.hand_rank < 10000:
                                        ranktxt = '0%10.4f' % hand.hand_rank
                                    else:
                                        ranktxt = '%10.4f' % hand.hand_rank
                                    rank_cnt[ranktxt] += 1

# write dict to file
output = open('rank_count_dict.pkl', 'wb') 
pickle.dump(rank_cnt, output) 
output.close()

output = open('type_count_dict.pkl', 'wb')
pickle.dump(type_cnt, output)
output.close()
