# Code      : /table/hand_type_prob.py
# Written by: LIU, Jiun Ee (G)
# Purpose   : Calculate winning probabilities of a 5-card poker hand

from collections import defaultdict
import pickle 

HAND_COMBO = 2598960	# 52 pick 5

# construct win probability for the 10 hand types 
pkl_file = open('type_count_dict.pkl', 'rb')
type_cnt = pickle.load(pkl_file)
pkl_file.close()

type_cnt_list=[]
type_prob_dict = defaultdict(float)
for key, value in type_cnt.iteritems():
    type_cnt_list.append((key, value))
for i in sorted(type_cnt_list):
    type_prob_dict[i[0]] = 1 - i[1] * 1.0 / HAND_COMBO

# write dict to file
output = open('type_prob_dict.pkl', 'wb')
pickle.dump(type_prob_dict, output)
output.close()

for key, value in type_prob_dict.iteritems():
    print '%20s %.2f' % (key, value)

