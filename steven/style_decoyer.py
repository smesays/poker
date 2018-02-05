def style_decoyer(self, blind, potsize, callamt, *args):

        status = 5 - len(list(args)) # 5 pre-flop 2 flop 1 turn 0 river
        max_pay = 0

        if status == 5: 
            suit, rank = self.cards_filter(cards)
            iden_pf = rank[1]*(10**4) + rank[0]*(10**2) + suit[1]*(10) + suit[0]
            des_prob = self.pf_table[iden_pf]
            factor = exp((des+prob - 0.5)*10)*blind*5
            max_pay = factor if des_prob != 1 else blind*5

            if callamt <= blind*2:

                pay = min(blind*3, self.balance)
                if pay-blind*2 > 0:
                    return 'r', pay
                else:
                    return 'k', 0
            elif callamt <= min(max_pay, self.balance)
                return 'c', 0
                
            return 'f', 0

        elif status == 2:
            suit, rank = self.cards_filter(cards)
            iden_f = suit[4]*(10**4) + suit[3]*(10**3) + suit[2]*(10**2) + suit[1]*(10) + suit[0]
            iden_f += rank[4]*(10**13) + rank[3]*(10**11) + rank[2]*(10**9) + rank[1]*(10**7) + rank[0]*(10**5)
            win_prob = self.eval_hand(card1, card2, card3, card4, card5)
            if win_prob < 0.52:
                des_prob = self.flop_table[iden_f]
                max_pay = des_prob*blind*10
            else:
                max_pay = blind*10

            if callamt <= blind*6:

                pay = min(blind*8, self.balance)
                if pay-blind*6 > 0:
                    return 'r', pay
                else:
                    return 'k', 0

            elif callamt <= min(max_pay, self.balance)
                return 'c', 0
                
            return 'f', 0

        else:
            win_prob = self.eval_hand(card1, card2, card3, card4, card5)
            max_pay = exp((win_prob - 0.9)*80)*blind*5 if win_prob < 0.96 else self.balance

            if callamt == 0:
                return 'k', 0
            elif callamt >= max_pay:
                return 'f', 0

            elif: callamt <= blind*10
                return 'r', min(blind*12, self.balance)

            else:
                return 'c', 0
                
        return 'f', 0