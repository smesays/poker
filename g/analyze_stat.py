import numpy as np

agent_stat_data = np.genfromtxt('../log/agent_log20180201.txt', delimiter=',')
agent_stat_data = agent_stat_data[:,1:]
#print agent_stat_data

agentlist = np.unique(agent_stat_data[:,0])
#print agentlist

numofagent = len(agentlist)
#print numofagent
'''
win_stat=np.zeros(numofagent,(2,3))
for i in len(agentlist):
    win_stat[i,:,:]=agentlist[i]
win_stat[:,0,:]=1
win_stat[:,1,:]=-1
print win_stat

'''
win_stat=np.zeros(numofagent)
for i in range(len(agent_stat_data)):
    for j in range(len(agentlist)):
        win_stat[agent_stat_data[i][0]-1] += agent_stat_data[i][1]

print 'num of tourney', len(agent_stat_data)/2
print 'win stat', win_stat 

