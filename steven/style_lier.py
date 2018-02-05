def style_lier(self, blind, potsize, callamt, card1, card2, *args):

        status = 5 - len(list(args)) # 5 pre-flop 2 flop 1 turn 0 river
        max_pay = 0
        win_prob = self.eval_hand(card1, card2, card3, card4, card5)
        lie = 0.1 if random.random > 0.8 and win_prob < 0.52 else 1.0
        call_ratio = callamt * 1.0 / (potsize - callamt)

        if status == 5: 
            suit, rank = self.cards_filter(cards)
            iden_pf = rank[1]*(10**4) + rank[0]*(10**2) + suit[1]*(10) + suit[0]
            des_prob = self.pf_table[iden_pf]
            factor = exp((des+prob - 0.5)*10*lie)*blind*5
            max_pay = factor if des_prob != 1 else blind*5

            if call_amt >= max_pay:
                return 'f', 0

            elif call_amt == 0
                return 'r', min(blind*2, max_pay)

            elif:
                call_amt <= 0.8*max_pay
                return 'r', max_pay
            else:
                return 'c', 0

        elif status == 2:
            suit, rank = self.cards_filter(cards)
            iden_f = suit[4]*(10**4) + suit[3]*(10**3) + suit[2]*(10**2) + suit[1]*(10) + suit[0]
            iden_f += rank[4]*(10**13) + rank[3]*(10**11) + rank[2]*(10**9) + rank[1]*(10**7) + rank[0]*(10**5)
            win_prob = win_prob/(lie*6) if win_prob < 0.52 else win_prob

            if win_prob < 0.52:
                des_prob = self.flop_table[iden_f]
                max_pay = des_prob*blind*8
            else:
                max_pay = blind*10

            if callamt <= min(max_play, self.balance):

                pay = min(int(max_pay*0.9), self.balance)
                if pay-blind*8 >= 0:
                    return 'r', max_pay
                else:
                    if callamt == 0:
                        return 'k', 0
                    else:
                        return 'c', 0
                
            return 'f', 0

        else:
            win_prob = win_prob/(lie*5.5) if win_prob < 0.52 else win_prob
            max_pay = exp((win_prob - 0.9)*80)*blind*5 if win_prob < 0.96 else self.balance

            if callamt == 0:
                return 'k', 0
            elif callamt >= max_pay:
                return 'f', 0

            elif: callamt <= max_pay
                return 'r', min(blind*15, self.balance)
            else:
                return 'c', 0
                
        return 'f', 0