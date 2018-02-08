import numpy as np

agent_log = np.genfromtxt('../log/agent_log20180207.txt', delimiter=',', usecols = [0,2,3], dtype=int)
# [tourneynum, style, 1/-1]
print agent_log
agent_stat_data = agent_log[:,1:]
#print agent_stat_data

stylelist = np.unique(agent_stat_data[:,0])
#print stylelist

numofstyle = len(stylelist)
print 'number of styles: %d' % numofstyle

print 'num of tourney', len(agent_stat_data)/2

print len(agent_log)
winner_stat = agent_log[agent_log[:,2]==-1]
loser_stat = agent_log[agent_log[:,2]==1]
winloss_stat = np.concatenate((winner_stat, loser_stat), axis=1)
audit = winloss_stat[winloss_stat[:,0] != winloss_stat[:,3]]
print len(audit)

#print 'sample winloss_stat'
#print winloss_stat[:5]
#print ' '

win_cnt=np.zeros((numofstyle, numofstyle), dtype=int)
win_prob=np.zeros((numofstyle, numofstyle), dtype=float)
tourney_cnt=np.zeros((numofstyle, numofstyle), dtype=int)
for i in range(len(winloss_stat)):
    style1=winloss_stat[i][1]-1
    style2=winloss_stat[i][4]-1
    print style1, style2
    if style1 > style2:
        tourney_cnt[style2][style1] += 1
    else:
        tourney_cnt[style1][style2] += 1
    win_cnt[style1][style2] += 1

print 'tournament vs counts'
print tourney_cnt
print ' '

print 'win counts'
print win_cnt
print ' '

np.set_printoptions(precision=2)
for i in range(numofstyle):
    for j in range(numofstyle):
        if i != j and win_cnt[i][j]*2 >= max(tourney_cnt[i][j],tourney_cnt[j][i]):
            win_prob[i][j] = win_cnt[i][j] *1.0 / max(tourney_cnt[i][j],tourney_cnt[j][i])
print 'win %'
print win_prob
print ' '
