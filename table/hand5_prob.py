from collections import defaultdict
import pickle 
HAND_COMBO = 2598960    # number of combinations of poker hands
RANK_COMBO = 7462       # number of combinations of unique hand ranks

pkl_file = open('rank_count.pkl', 'rb') 
rank_count_dict = pickle.load(pkl_file) 
pkl_file.close()
print 'rank count length', len(rank_count_dict)

if len(rank_count_dict) != RANK_COMBO:
	print 'Rank count dictionary is not correct'

hand_count = 0
rank_list = []
for key, value in rank_count_dict.iteritems():
    hand_count += value
    rank_list.append(key)

if hand_count != HAND_COMBO:
    print 'Hand count does not sum to ', HAND_COMBO

rank_map_dict = {}
keycnt = 0
for i in sorted(rank_list):
    keycnt += 1
    rank_map_dict[i]=keycnt

# Map hand rank to 4-digit integer 
output = open('rank_map_dict.pkl', 'wb')
pickle.dump(rank_map_dict, output, protocol=pickle.HIGHEST_PROTOCOL)
output.close()
 
#audit_list = []
#for key, value in rank_map_dict.iteritems():
#       audit_list.append((key, value))
#for i in sorted(audit_list):
#    print i




'''
print 'Unique hand count', len(hand_cnt)

list=[] 
for key, value in hand_cnt.iteritems():
	list.append((key,value)) 

cum_cnt = 0
hand_prob = defaultdict(float)
hand_prob_list = []
for i in sorted(list):
	cum_cnt += i[1]
	hand_prob[i[0]] = cum_cnt * 1.0 / HAND_COMBO
	hand_prob_list.append((i[0], cum_cnt * 1.0 / HAND_COMBO))

for i in hand_prob_list:
	print '%.3f %s' % (i[1], i[0]) 

# construct win probability for the 10 hand types
pkl_file = open('name_count.pkl', 'rb')
name_cnt = pickle.load(pkl_file)
pkl_file.close()

name_cnt_list=[]
name_prob_dict = defaultdict(float)
for key, value in name_cnt.iteritems():
    name_cnt_list.append((key, value))
for i in sorted(name_cnt_list):
    name_prob_dict[i[0]] = 1 - i[1] * 1.0 / HAND_COMBO
    print '%50s %.4f' % (i[0], 1 - i[1] * 1.0 / HAND_COMBO)

# write dict to file
output = open('name_prob_dict.pkl', 'wb')
pickle.dump(name_prob_dict, output)
output.close()


# construct win probability for the 10 hand types 
pkl_file = open('type_count.pkl', 'rb')
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
'''
