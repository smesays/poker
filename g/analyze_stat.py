import numpy as np

agent_stat_data = np.genfromtxt('../log/agent_log20180131.txt', delimiter=',')
agent_stat_data = agent_stat_data[:,1:]
print agent_stat_data

agentlist = np.unique(agent_stat_data[:,0])
print agentlist

numofagent = len(agentlist)
print numofagent

win_stat=np.zeros(3)
for i in range(len(agent_stat_data)):
    win_stat[agent_stat_data[i][0]-1] += agent_stat_data[i][1]

print win_stat 
