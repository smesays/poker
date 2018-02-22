execfile('card.py') 
execfile('hand.py') 
execfile('deck.py') 
execfile('agent.py') 
execfile('gameplay.py')
import sys, os, time
import random, pickle

#SIMULATE = 1
SIMULATE = 0
VS_BOT_STYLE = None    # pick bot style to play against human, or None
BOT_STYLE1 = None   # pick bot style 1 for bots play, or None
BOT_STYLE2 = None   # pick bot style 2 for bots play, or None

def report_winloss(bal):
    if bal == 0:
        return -1
    return 1

def nprint(): # disable printing
    sys.stdout = open(os.devnull, 'w')

def yprint(): # enable printing
    sys.stdout = sys.__stdout__

def tournament(tourneynum):
    BUY_IN = 20000  # standard tournament with initial buy-in $20k
    # structure of blinds follows https://www.cardplayer.com/poker-tournaments/2605-2009-nbc-national-heads-up-championship/18234
    BLIND_STRUCTURE  =[150, 200, 300, 400, 600, 1000, 1500, 2000, 3000, 4000, 5000, 8000, 10000, 15000, 20000, 30000, 40000]
    # smallest denomination of chips in each round
    MINCHIP_STRUCTURE=[25 , 25 , 25 , 25 , 100, 100 , 100 , 500 , 500 , 500 , 1000, 1000, 1000 , 1000 , 1000 , 1000 , 1000 ] 

    if SIMULATE: 
        human = 'n'
        PRINT_LOG = 0
#        PRINT_LOG = 1
    else:
        print " "
        print "                                                              **************************************************************"
        print "                                                              * Welcome to the Texas No Limit Hold'em Heads-up Tournament! *"
        print "                                                              **************************************************************"
        print " "
        human = 'y'
#        human =  raw_input("                                                                   > Is human playing? Enter y or n: ").lower()
        PRINT_LOG = 1

    quick_slow = 's'
    if human == 'y':
#        quick_slow = raw_input("                                                                   > (Q)uick or (S)tandard game? Enter q or s: ")
#        quick_slow = quick_slow.lower()
        quick_slow = 'q'
        if quick_slow == 'q':
            BUY_IN = 5000
        human_name = raw_input("                                                                   > Enter your name: ")
        print '                                                                   Hello %s' % human_name
        print "                                                                   Let's see who starts first." 
        time.sleep(1)
        if random.choice([1,2]) == 1:
            prompt = 1
            print "                                                                   %s starts first." % human_name
            agent1 = Agent(human_name, BUY_IN, 0)
            agent2 = Agent("Bot", BUY_IN, VS_BOT_STYLE)
        else:
            prompt = 2
            print "                                                                   Bot starts first."
            agent1 = Agent("Bot", BUY_IN, VS_BOT_STYLE)
            agent2 = Agent(human_name, BUY_IN, 0)
        time.sleep(1)
        print "                                                                   Each player starts with $%d. Let's begin!" % BUY_IN
        print " "
    else:
        prompt = 0
        print "                                                                   Computer bots will play each other."
        print " "
        agent1 = Agent("Bot 1", BUY_IN, BOT_STYLE1)
        agent2 = Agent("Bot 2", BUY_IN, BOT_STYLE2)
    
    gamenum = 0
    roundnum = 1
    blind = BLIND_STRUCTURE[0]
    minchip = MINCHIP_STRUCTURE[0]
    speedup_fct = 1
    elapsed_time = 0        # track elapsed time of each game for blind structure

    tourney_log = []
    agent_log = []
    game_stat_log = []
    while ((agent1.balance > 0) & (agent2.balance > 0)):
        gamenum += 1
        if quick_slow == 'q':
            speedup_fct = 4
        if elapsed_time * speedup_fct > 30*60:  # go to next round with different blind after elapsed time is over 30 minutes
            roundnum += 1
            blind = BLIND_STRUCTURE[min(roundnum-1,16)] # 17 rounds, after that, blind stays at 40k
            minchip = MINCHIP_STRUCTURE[min(roundnum-1,16)]
            agent1.balance = int(agent1.balance / minchip) * minchip
            agent2.balance = int(agent2.balance / minchip) * minchip
            elapsed_time = 0    # reset for a new 30 minutes

        if (gamenum % 2 != 0) & (agent1.balance < blind*2) |\
           (gamenum % 2 == 0) & (agent1.balance < blind*2): # for simplicity, for now check against big blind
            print '                                                           Tournament is over!', agent1.name, 'is bankrupt and', agent2.name, 'wins!'
            agent1.balance = 0
                                    # for simplicity, for now check against big blind
        elif (gamenum % 2 != 0) & (agent2.balance < blind*2) |\
             (gamenum % 2 == 0) & (agent2.balance < blind*2):
            print '                                                           Tournament is over!', agent2.name, 'is bankrupt and', agent1.name, 'wins!'
            agent2.balance = 0
        else:
            if PRINT_LOG == 0:
                nprint()
#            print 'styles: %d %d' % (agent1.style, agent2.style)
            print 'Round %d Game %d with blinds $%d/$%d. Minimum bet is $%d. (Min. chip $%d)' % (roundnum, gamenum, blind, blind*2, blind*2, minchip)
            if gamenum/2.0 != int(gamenum/2.0):
                game = Gameplay(gamenum, agent1, agent2, blind, minchip, prompt)
            else:
                if prompt == 0:
                    game = Gameplay(gamenum, agent2, agent1, blind, minchip, 0)
                elif prompt == 1:
                    game = Gameplay(gamenum, agent2, agent1, blind, minchip, 2)
                else:
                    game = Gameplay(gamenum, agent2, agent1, blind, minchip, 1)
                
            game.play()
            elapsed_time += game.elapsed
#            print 'round elapsed %d' % int(elapsed_time/60)
            game_stat_log.append((game.gamenum, game.phase, game.pot))
            tourney_log.append(game.betlog)
            yprint()
        if human == 'y':
            time.sleep(1)

    if agent1.balance == 0:
        print '                                                           Tournament is over!', agent1.name, 'is bankrupt and', agent2.name, 'wins!'
    elif agent2.balance == 0:
        print '                                                           Tournament is over!', agent2.name, 'is bankrupt and', agent1.name, 'wins!'

    agent_log.append((agent1.name, agent1.style, report_winloss(agent1.balance)))
    agent_log.append((agent2.name, agent2.style, report_winloss(agent2.balance)))

    if SIMULATE == 0:
        print '                                                                   *******************************'
        print '                                                                   ***** Thanks for playing! *****'
        print '                                                                   *******************************'
        print ' '

    print agent_log
#    print game_stat_log
    print ' '

    if SIMULATE==0:
        f = open("../log/agent_fulllog20180209.txt", "a")
        for i in range(len(agent_log)):
            f.write("%d"%tourneynum)
            f.write(",")
            f.write(",".join(map(lambda x: str(x), agent_log[i])))
            f.write("\n")
        f.close()

        f = open("../log/gamestat_fulllog20180209.txt", "a")
        for i in range(len(game_stat_log)):
            f.write("%d"%tourneynum)
            f.write(",")
            f.write(",".join(map(lambda x: str(x), game_stat_log[i])))
            f.write("\n")
        f.close()

        if gamenum < 3:
            f = open("../log/agent_shortlog20180209.txt", "a")
            for i in range(len(agent_log)):
                f.write("%d"%tourneynum)
                f.write(",")
                f.write(",".join(map(lambda x: str(x), agent_log[i])))
                f.write("\n")
            f.close()
        else:
            f = open("../log/agent_log20180209.txt", "a")
            for i in range(len(agent_log)):
                f.write("%d"%tourneynum)
                f.write(",")
                f.write(",".join(map(lambda x: str(x), agent_log[i])))
                f.write("\n")
            f.close()

            f = open("../log/tourney_log20180209.txt", "a")
            for i in range(len(tourney_log)):
                for j in range(len(tourney_log[i])):
                    f.write("%d"%tourneynum)
                    f.write(",")
                    f.write(",".join(map(lambda x: str(x), tourney_log[i][j])))
                    f.write("\n")
            f.close()

if __name__ == "__main__":
    if SIMULATE:  
        for ty in range(10000):
            print 'tournament %d' % ty
            tournament(ty)
    else:
        for ty in range(500):
            tournament(ty)
