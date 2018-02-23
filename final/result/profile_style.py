# Code      : profile_style.py
# Written by: LIU, Jiun Ee (G)
# Purpose   : Analyze the tournament log to produce style profiles

import numpy as np

dtyp=np.dtype([('phase','i2'),('style','i2'),('betact','S1'),('amt','i8')])
tourney_log = np.genfromtxt('../log/tourney_log20180222.txt', delimiter=',', usecols = [2,5,6,7], dtype=dtyp)
# var0=tourneynum var1=gamenum var2=phase var3=betidx var4=name var5=style, var6=betact, var7=amt
# numpy array format: [phase, style, betact, amt]
print 'tourney log = ', tourney_log[:5]

phaselist = np.unique(tourney_log['phase'])
print 'phase list = ', phaselist

stylelist = np.unique(tourney_log['style'])
print 'style list = ', stylelist
# style list =  [1 2 3 4 5 6 7 8]

betactlist = np.unique(tourney_log['betact'])
print 'betact list = ', betactlist
# betact list =  ['b' 'c' 'f' 'k' 'r']

betact_map = {'k':0, 'b':1, 'c':2, 'r':3, 'f':4} 
'''
betact_cnt=np.zeros((len(betactlist), len(stylelist)), dtype=int)
for zz in range(len(tourney_log)):
    style=tourney_log[zz]['style']-1
    betact=betact_map[tourney_log[zz]['betact']]
    betact_cnt[betact][style] += 1

print 'betact count by styles'
print betact_cnt
print ' '

phase_cnt=np.zeros((len(phaselist), len(stylelist)), dtype=int)
for zz in range(len(tourney_log)):
    style=tourney_log[zz]['style']-1
    phase=tourney_log[zz]['phase']-1
    phase_cnt[phase][style] += 1

print 'phase count by styles'
print phase_cnt
print ' '

# read agent log to find out for each tourneynum, which style played against which style
dtyp2=np.dtype([('tourneynum','i5'),('style','i2')])
agent_log = np.genfromtxt('../log/agent_log20180222.txt', delimiter=',', usecols = [0,2], dtype=dtyp2)
# numpy array format: [tourneynum, style]

agent_stat_data = agent_log[:,1:]
#print agent_stat_data

stylelist = np.unique(agent_stat_data[:,0])





'''
# v2 are for aggressive style vs all other styles 
tourney_log_aggressive = tourney_log['style'==1]
betact_cnt2=np.zeros((len(betactlist), len(stylelist)), dtype=int)
for zz in range(len(tourney_log)):
    style=tourney_log[zz]['style']-1
    betact=betact_map[tourney_log[zz]['betact']]
    betact_cnt2[betact][style] += 1

print 'aggressive betact count by opponent styles'
print betact_cnt2
print ' '

phase_cnt=np.zeros((len(phaselist), len(stylelist)), dtype=int)
for zz in range(len(tourney_log)):
    style=tourney_log[zz]['style']-1
    phase=tourney_log[zz]['phase']-1
    phase_cnt2[phase][style] += 1

print 'aggressive phase count by opponent styles'
print phase_cnt2
print ' '
'''
