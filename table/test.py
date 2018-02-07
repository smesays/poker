import pickle
# reading mapping file to map rank to 4-digit integer
pkl_file = open('hand7_prob.pkl', 'rb')
rank_map_dict = pickle.load(pkl_file)

pkl_file.close()
print len(rank_map_dict)
ranklist=[]
for key, value in rank_map_dict.iteritems():
    ranklist.append((key,value))
print len(ranklist)
print ranklist
for i in sorted(ranklist):
    print i
