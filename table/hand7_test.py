execfile('../g/hand.py') 
execfile('../g/card.py') 
import pickle 
import time 

pkl_file = open('hand7_cnt_dict.pkl', 'rb') 
hand7_cnt_dict = pickle.load(pkl_file) 
pkl_file.close() 

pkl_file = open('hand7_cnt_dict2.pkl', 'rb') 
hand7_cnt_dict2 = pickle.load(pkl_file) 
pkl_file.close() 

flop1=Card(2) 
flop2=Card(7) 
flop3=Card(10) 
turn =Card(21) 
river=Card(50) 
hole1=Card(40) 
hole2=Card(3) 

print len(hand7_cnt_dict)
print len(hand7_cnt_dict2)
#print hand7_cnt_dict

comm=Hand(flop1,flop2,flop3,turn,river) 
print comm, comm.hand_name, comm.hand_rank 

hand=Hand(flop1,flop2,flop3,turn,river,hole1,hole2) 
print hand, hand.hand_name, hand.hand_rank 

if comm.hand_rank >= 10000:
    comm_shortrank = '%.5f'%comm.hand_rank
else:
    comm_shortrank = '0%.4f'%comm.hand_rank

comm_list = hand7_cnt_dict[comm_shortrank] 
comm_list2 = hand7_cnt_dict2[comm_shortrank] 
print comm_list
print comm_list2
