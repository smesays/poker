from functools import reduce
from itertools import groupby
from itertools import combinations
import random

class PowerTable:

    def __init__(self):
        self.bfs_table = {}
        self.pf_score = []
        self.flop_score = []
        self.deep_hand()
        self.pf_table()

    def cards_filter(self, cards):
        result = []
        for card in cards:
            if (card-1)%13 != 0:
                result.append([(4 - int((card-1)/13)), (card-1)%13 + 1])
            else:
                result.append([(4 - int((card-1)/13)), 14])

        result.sort(key = lambda i: (i[1], i[0]), reverse = False)
        return [result[i][0] for i in range(len(result))], [result[i][1] for i in range(len(result))]


    def deep_hand(self):
        idx_list = list(combinations(range(1, 53), 5))
        #f = open("flop_score.txt", "w")
        counter = 0

        for cards in idx_list:
            suit, rank = self.cards_filter(cards)
            iden_f = suit[4]*(10**4) + suit[3]*(10**3) + suit[2]*(10**2) + suit[1]*(10) + suit[0]
            iden_f += rank[4]*(10**13) + rank[3]*(10**11) + rank[2]*(10**9) + rank[1]*(10**7) + rank[0]*(10**5)
            score = self.hand_eval(suit, rank)
            self.bfs_table[iden_f] = score
            #f.write(",".join(map(lambda x: str(x), [iden_f, score])))
            if score < 4:
                improvement = self.eval_prob(suit, rank)
                self.flop_score.append([iden_f, improvement])
            print(counter)
            counter += 1
        #f.close()

    def pf_table(self):
        idx_list = list(combinations(range(1, 53), 2))

        for cards in idx_list:
            suit, rank = self.cards_filter(cards)
            iden_pf = rank[1]*(10**4) + rank[0]*(10**2) + suit[1]*(10) + suit[0]
            score_pf = self.eval_flop(cards)
            print(iden_pf)
            self.pf_score.append([iden_pf, score_pf/19600.0])

    def eval_flop(self, p_cards):
        idx_list = range(1, 53)
        score_flop = 0
        for card in p_cards:
            idx_list.remove(card)
        idx_list = list(combinations(idx_list, 3))
        for cards in idx_list:
            all_card = cards + p_cards
            suit, rank = self.cards_filter(all_card)
            iden_f = suit[4]*(10**4) + suit[3]*(10**3) + suit[2]*(10**2) + suit[1]*(10) + suit[0]
            iden_f += rank[4]*(10**13) + rank[3]*(10**11) + rank[2]*(10**9) + rank[1]*(10**7) + rank[0]*(10**5)
            current_score = self.bfs_table[iden_f]
            if current_score != 0:
                score_flop += 1
        return score_flop


    def hand_eval(self, suit, rank):
        str_flu_flag = self.is_straight_or_straight_flush(rank, suit)
        return max(self.is_fullhouse_or_four(rank, suit), str_flu_flag)

    def is_straight_or_straight_flush(self, rank, suit):
        for i in range(-1, len(rank)-4):
            eval_rank = [rank[i+j]-j for j in range(0, 5)] 
            if len(set(eval_rank)) == 1 or eval_rank == [14, 1, 1, 1, 1]:
                eval_suit = [suit[i+j] for j in range(0, 5)] 
                return (4 + self.is_flush(eval_suit))
        return self.is_flush(suit)

    def is_flush(self, suit):
        for suit, group_obj in groupby(sorted(suit)):
            leng = len(list(group_obj))
            if leng >= 5: return 5
        return 0

    def is_fullhouse_or_four(self, rank, suit):
        flg2, flg3 = [0, 0]
        for rank_obj, group_obj in groupby(rank):
            leng = len(list(group_obj))
            if leng >= 4:
                return 7
            elif leng >= 3:
                flg3 += 1
            elif leng >= 2:
                flg2 += 1

        if min(flg3, flg2) != 0 or flg3 == 2: return 6
        elif flg3 != 0: return 3
        else: return min(2, flg2)

    def eval_prob(self, suit, rank):
        return max(self.almost_straight(rank), self.almost_flush(suit), self.almost_fullhouse_or_four(rank))

    def almost_straight(self, rank):
        for i in range(-1, len(rank)-4):
            eval_rank = [rank[i+j]-j for j in range(0, 5)] 
            if len(set(eval_rank)) == 1 and eval_rank[0] != 14 and eval_rank[4] != 9: return 0.2886216466
        return 0

    def almost_flush(self, suit):
        for suit, group_obj in groupby(sorted(suit)):
            leng = len(list(group_obj))
            if leng == 4: return 0.3496762257
            elif leng == 3: return 0.04162812211
        return 0

    def almost_fullhouse_or_four(self, rank):
        flg2, flg3 = [0, 0]
        for rank_obj, group_obj in groupby(rank):
            leng = len(list(group_obj))
            if leng == 3: return 0.3395004625
            elif leng >= 2:
                flg2 += 1
        if flg2 == 2: return 0.1637372803
        elif flg2 ==1: return 0.01757631822
        return 0
#-------------------------------------------------------------------------------------------------
decisiontable = PowerTable()

#f = open("decision_table_preflop.txt", "w")
#for i in range(len(decisiontable.pf_score)):
#    f.write(",".join(map(lambda x: str(x), decisiontable.pf_score[i])))
#    f.write("\n")
#f.close()

#f = open("decision_table_flop.txt", "w")
#for i in range(len(decisiontable.flop_score)):
#    f.write(",".join(map(lambda x: str(x), decisiontable.flop_score[i])))
#    f.write("\n")
#f.close()