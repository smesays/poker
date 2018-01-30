import pickle 

LOAD_HANDNAME = 0
PRINT_HANDNAME = 0

LOAD_NAMECNT = 1
PRINT_NAMECNT = 0

if LOAD_HANDNAME:
    print '*************' 
    print '* Hand Name *' 
    print '*************' 
    pkl_file = open('hand_name_dict.pkl', 'rb') 
    hand_name_map = pickle.load(pkl_file) 
    pkl_file.close()
    print 'Hand-Name map has length ', len(hand_name_map)

    if PRINT_HANDNAME: 
#        for i in range(len(hand_name_map)):
#            if i % 100000 == 0:
#                print i[0], i[1]
    	for i in hand_name_map:
    		print i[0], i[1] 
    print 'Hand Count has length ', len(hand_cnt)

if LOAD_NAMECNT:
    print '**************' 
    print '* Name Count *' 
    print '**************' 
    pkl_file = open('name_count.pkl', 'rb') 
    name_cnt = pickle.load(pkl_file) 
    pkl_file.close() 
    print 'Name Count has length ', len(name_cnt)

    if PRINT_NAMECNT:
    	list=[] 
    	for key, value in name_cnt.iteritems():
    		list.append((key,value)) 
    	for i in sorted(list):
    		print i[1], i[0]
'''
print '**************'
print '* Type Count *'
print '**************'
pkl_file = open('type_count.pkl', 'rb')
type_cnt = pickle.load(pkl_file)
pkl_file.close()
print len(type_cnt)

list=[]
for key, value in type_cnt.iteritems():
    list.append((value,key))
for i in sorted(list):
    print '%20s %d' % (i[1], i[0])

print '*************'
print '* Type Prob *'
print '*************'
pkl_file = open('type_prob_dict.pkl', 'rb')
type_prob = pickle.load(pkl_file)
pkl_file.close()
print len(type_prob)

for key, value in type_prob.iteritems():
    print '%20s %.4f' % (key, value)
'''
