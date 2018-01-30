execfile('card.py') 
execfile('hand.py') 
execfile('deck.py') 
execfile('agent.py') 
execfile('gameplay.py')
import time
import random
import pickle

def report_winloss(bal):
    if bal == 0:
        return -1
    return 1

if __name__ == "__main__":
    print " "
    print "                                                              **************************************************************"
    print "                                                              * Welcome to the Texas No Limit Hold'em Heads-up Tournament! *"
    print "                                                              **************************************************************"
    print " "

    BUY_IN = 20000  # standard tournament with initial buy-in $20k
    human =  raw_input("                                                                   > Is human playing? Enter y or n: ")
    human = human.lower()

    quick_slow = 's'
    if human == 'y':
        quick_slow = raw_input("                                                                   > (Q)uick or (S)tandard game? Enter q or s: ")
        quick_slow = quick_slow.lower()
        if quick_slow == 'q':
            BUY_IN = 2000        
        human_name = raw_input("                                                                   > Enter your name: ")
        print '                                                                   Hello %s' % human_name
        print "                                                                   Let's see who starts first." 
        time.sleep(1)
        if random.choice([1,2]) == 1:
            prompt = 1
            print "                                                                   %s starts first." % human_name
            agent1 = Agent(human_name, BUY_IN, '')
            agent2 = Agent("Bot", BUY_IN, 'aggressive')
        else:
            prompt = 2
            print "                                                                   Bot starts first."
            agent1 = Agent("Bot", BUY_IN, 'aggressive')
            agent2 = Agent(human_name, BUY_IN, '')
        time.sleep(1)
        print "                                                                   Each player starts with $%d. Let's begin!" % BUY_IN
        print " "
    else:
        prompt = 0
        print "                                                                   Computer bots will play each other."
        print " "
#        agent1 = Agent("Bot 1", BUY_IN, 'conservative')
        agent1 = Agent("Bot 1", BUY_IN, 'high_hater')
        agent2 = Agent("Bot 2", BUY_IN, 'aggressive')
    
    # structure of blinds follows https://www.cardplayer.com/poker-tournaments/2605-2009-nbc-national-heads-up-championship/18234
    blind_structure=[150, 200, 300, 400, 600, 1000, 1500, 2000, 3000, 4000, 5000, 8000, 10000, 15000, 20000, 30000, 40000]
    gamenum = 0
    roundnum = 0

    tourney_log = []
    agent_log = []
    while ((agent1.balance > 0) & (agent2.balance > 0)):
#    while (gamenum < 13):
        gamenum += 1
        game_per_round = 20
        if quick_slow == 'q':
            game_per_round = 4
        if (gamenum - 1) % game_per_round == 0: # alternatively, add each move by seconds, and next round after 30 minutes
            roundnum += 1
        blind = blind_structure[min(roundnum-1,16)]/10 # 17 rounds, after that, blind stays at 40k
        if (gamenum % 2 != 0) & (agent1.balance < blind*2) |\
           (gamenum % 2 == 0) & (agent1.balance < blind):
            print '                                                           Tournament is over!', agent1.name, 'is bankrupt and', agent2.name, 'wins!'
            agent1.balance = 0
        elif (gamenum % 2 != 0) & (agent2.balance < blind) |\
             (gamenum % 2 == 0) & (agent2.balance < blind*2):
            print '                                                           Tournament is over!', agent2.name, 'is bankrupt and', agent1.name, 'wins!'
            agent2.balance = 0
        else:
            print 'Round %d Game %d with blind $%d/$%d. Minimum bet is $%d.' % (roundnum, gamenum, blind, blind*2, blind*2)
            if gamenum/2.0 != int(gamenum/2.0):
                game = Gameplay(agent1, agent2, blind, prompt)
            else:
                if prompt == 0:
                    game = Gameplay(agent2, agent1, blind, 0)
                elif prompt == 1:
                    game = Gameplay(agent2, agent1, blind, 2)
                else:
                    game = Gameplay(agent2, agent1, blind, 1)
                
            game.play()
            tourney_log.append(game.betlog)
        if human == 'y':
            time.sleep(1)

    if agent1.balance == 0:
        print '                                                           Tournament is over!', agent1.name, 'is bankrupt and', agent2.name, 'wins!'
    elif agent2.balance == 0:
        print '                                                           Tournament is over!', agent2.name, 'is bankrupt and', agent1.name, 'wins!'

    agent_log.append((agent1.name, agent1.style, report_winloss(agent1.balance)))
    agent_log.append((agent2.name, agent2.style, report_winloss(agent2.balance)))

    print '                                                                   *******************************'
    print '                                                                   ***** Thanks for playing! *****'
    print '                                                                   *******************************'
    print ' '
    print agent_log
    print ' '
    print tourney_log
