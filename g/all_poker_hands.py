execfile('card.py') 
execfile('hand.py') 
from collections import defaultdict 
import pickle 
hand_name=[]
hand_type=[]
name_cnt=defaultdict(int)
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
                                        counttemp = '0%.4f ' % hand.hand_rank + hand.hand_name
                                    else:
                                        counttemp = '%.4f ' % hand.hand_rank + hand.hand_name
                                    name_cnt[counttemp] += 1
                                    nametemp = '%s' % hand
                                    hand_name.append((nametemp, counttemp))
                                    hand_type.append((nametemp, hand.hand_type))

# write dict to file
output = open('hand_name_dict.pkl', 'wb') 
pickle.dump(hand_name, output) 
output.close()

output = open('hand_type_dict.pkl', 'wb')
pickle.dump(hand_type, output)
output.close()

output = open('hand_count.pkl', 'wb') 
pickle.dump(name_cnt, output) 
output.close()

output = open('type_count.pkl', 'wb')
pickle.dump(type_cnt, output)
output.close()
