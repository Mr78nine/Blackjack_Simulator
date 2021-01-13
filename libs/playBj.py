import sys,os
sys.path.append(os.path.dirname(__file__))
from yaml import load, FullLoader
import pbjHelpers as ph


class State:

    def __init__(self, cfg):

        #Init config
        self.config = cfg

        # Init strategy vars
        self.betSpread = self.config["Strategy"]["betSpread"]
        # Init player vars
        self.runningCount = 0
        self.playerHands = [[]]
        self.playerBets = []
        self.playerBankroll = self.config["Strategy"]["bankroll"]
        self.playerState = ""

        # Init table vars
        self.deckNumber = self.config["Rules"]["deckNumber"]
        self.shoe = ph.Deck(numDecks=self.deckNumber)
        self.dealer17 = self.config["Rules"]["dealer17"]
        self.bjPays = self.config["Rules"]["bjPays"] + 1 #We always "lose" original bet, so pay it back
        self.surrender = self.config["Rules"]["surrender"]
        self.insurancePays = self.config["Rules"]["insurancePays"] +1 #Same as bj
        self.minBet = self.config["Rules"]["minBet"]
        self.maxBet = self.config["Rules"]["maxBet"]
        self.deckPen = self.config["Rules"]["deckPen"]
        self.resplitAces = self.config["Rules"]["resplitAces"]
        self.whenDouble = self.config["Rules"]["whenDouble"]
        self.das = self.config["Rules"]["das"]

        # Init dealer vars
        self.dealerHand = []
        self.dealerAction = ""

        #Init meta vars
        self.wins = 0
        self.losses = 0
    #Functions for playing


    #Helpers
    def get_hand_total(self, hand):
        total = 0
        saveIt = 0
        for card in hand:
            val = self.get_cardVal(card)
            if val == 11:
                saveIt += 1
            total += val
        # Now, try to save it if we have aces!
        while total > 21 and saveIt > 0:
            if saveIt == 0:
                break
            total -= 10
            saveIt -= 1
        return total

    def get_upcard(self):
        if self.get_cardVal(self.dealerHand[0]) == 11:
            return "A"
        return self.get_cardVal(self.dealerHand[0])

    def get_cardVal(self,card):
        if card.value == "Jack" or card.value == "Queen" or card.value == "King":
            return 10
        elif card.value == "Ace":
            return 11
        else:
            return int(card.value)

    def check_natural(self,hand):
        if (len(hand) == 2 and self.get_hand_total(hand) == 21):
            return True
        else:
            return False
    # Assume we didn't bust
    def get_formatted_hand(self,hand, forceHardTotal=False):
        if len(hand) == 1:
            if self.get_cardVal(hand[0]) == 11:
                return "A"
            else:
                return self.get_cardVal(hand[0])

        # Check for potential split hands
        if len(hand) == 2:
            if self.get_cardVal(hand[0]) == self.get_cardVal(hand[1]) and forceHardTotal is False:
                if self.get_cardVal(hand[0]) == 11:
                    return ("A-A")
                else:
                    return ("{}-{}".format(self.get_cardVal(hand[0]), self.get_cardVal(hand[1])))

        total = self.get_hand_total(hand)
        aceCount = 0

        for card in hand:
            if self.get_cardVal(card) == 11:
                aceCount += 1

        if aceCount == 0:
            return total
        elif total-11 > 1:
            return f"A-{total-11}"
        else:
            return total



    def check_insurance(self):
        tcount = self.get_true_count()
        if len(self.playerHands[0]) == 2 and self.get_upcard() == "A":  # Check for insurance
            if tcount >= float(self.config["Strategy_Table"]["insurance"]) :  # todo: Assumes we take insurace at positive true counts
                return True
        return False


    def get_player_state(self, playerHand, tcount):

        # Check for bust
        if self.get_hand_total(playerHand) > 21:
            return "bust"
        elif self.get_hand_total(playerHand) == 21: #Put this here! No lookups for 21
            return "stand"

        if (len(self.playerHands) < 4):
            action = (self.config["Strategy_Table"][self.get_formatted_hand(playerHand)][self.get_upcard()]).split()
        else:
            action = (self.config["Strategy_Table"][self.get_formatted_hand(playerHand, forceHardTotal=True)][self.get_upcard()]).split()



        # Check for index play
        if len(action) > 1:
            indexAction = action[0]
            indexNumber = action[1]
            nonIndexAction = action[2]

            indexDirection = indexNumber[0]


            if indexDirection == "+":
                if tcount >= float(indexNumber):  # If we should take index play, take it!
                    return indexAction
                else:
                    return nonIndexAction
            elif indexDirection == "-":
                if tcount <= float(indexNumber):  # If we should take index play, take it!
                    return indexAction
                else:
                    return nonIndexAction
            else:
                raise ValueError("Improper index play format at {} : {}. Index number should be of type \"+-n\""
                                 .format(self.get_formatted_hand(playerHand), self.get_formatted_hand(self.dealerHand)))
        else:
            return action[0]

    def update_running_count(self,cardDealt):

        if self.get_cardVal(cardDealt) >= 2 and self.get_cardVal(cardDealt) <= 6:
            self.runningCount += 1
        elif self.get_cardVal(cardDealt) >= 10:
            self.runningCount -= 1

    def get_true_count(self):
        if (len(self.shoe.cards) == 0):
            return 0
        return self.runningCount / (len(self.shoe.cards) / 52)

    #Assume we already checked insurance
    def play_player(self, handIndex):
        stop = False
        while not stop:
            while self.playerState != "bust" and self.playerState != "stand" and self.playerState != "double":

                self.playerState = self.get_player_state(playerHand=self.playerHands[handIndex], tcount=self.get_true_count())

                # If we have split aces, we must stand:
                if len(self.playerHands) > 1 and self.get_cardVal(self.playerHands[handIndex][0]) == 11:
                    self.playerState = "stand"
                    continue


                # If we busted:
                if self.playerState == "bust" or self.playerState == "stand":
                    continue

                # If we wanna surrender: todo



                # If we wanna hit:
                if self.playerState == "hit":
                    card = self.shoe.rm_card()
                    self.playerHands[handIndex].append(card)  # Go to the hand that wants the card, and give the card to it
                    # Now, update the running count
                    self.update_running_count(card)


                # If we wanna double
                elif self.playerState == "double":  # When can we double?
                    if self.whenDouble == "Original Two":
                        if len(self.playerHands[handIndex]) > 2 or len(self.playerHands) > 1:
                            self.deal_card(self.playerHands[handIndex])
                        else:
                            self.playerBankroll -= self.playerBets[handIndex]
                            self.playerBets[handIndex] *= 2  # Bet index corresponds to handIndex - i.e. for hands[2], its bet is at bets[2]
                            self.deal_card(self.playerHands[handIndex])

                # todo: Rest of double cases like only double 9-11, 9-10, etc. (def can_double)

                # If we wanna double-stand:
                elif self.playerState == "double-stand":  # When can we double?
                    if self.whenDouble == "Original Two":
                        if len(self.playerHands[handIndex]) > 2:
                            self.playerState = "stand"
                        else:
                            self.playerBankroll -= self.playerBets[handIndex]
                            self.playerBets[handIndex] *= 2
                            self.deal_card(self.playerHands[handIndex])

                    # todo: Rest of double cases (def can_double)

                elif self.playerState == "split":

                    splitCard = self.playerHands[handIndex].pop()  # Should get a card here

                    # Update hands and bets
                    self.playerHands.append([splitCard])  # [ [splitCard] , [splitCard] ]
                    self.playerBets.append(self.playerBets[handIndex]) #New corresponding bets
                    self.playerBankroll -= self.playerBets[handIndex]

                    #Give the hand a card
                    self.deal_card(self.playerHands[handIndex])



            #Once done with a hand, if our handIndex < numHands -1, then we have hands yet to play!
            if handIndex < len(self.playerHands)-1:
                #New hand!
                handIndex += 1
                #Deal a card to the next hand, and continue!
                self.deal_card(self.playerHands[handIndex])
                self.playerState = ""
            else:
                stop = True


    def is_soft17(self, hand):
        if self.get_formatted_hand(hand) == "A-6":
            return True
        else:
            return False

    def play_dealer(self):
        self.update_running_count(self.dealerHand[1]) #Show our downcard

        #If player has no non-bust hands, don't play
        busted = True
        for hand in self.playerHands:
            if self.get_hand_total(hand) < 21:
                busted = False
        if busted:
            return

        if self.config["Rules"]["dealer17"] == "S17":
            while self.get_hand_total(self.dealerHand) < 17:
              self.deal_card(self.dealerHand)
        elif self.config["Rules"]["dealer17"] == "H17":
            while self.get_hand_total(self.dealerHand) < 17 or self.is_soft17(self.dealerHand):
                self.deal_card(self.dealerHand)

    def place_bets_profbj(self):
        bet = 1
        self.playerBankroll -= bet
        self.playerBets.append(bet)
    def place_bets(self):

        strategy = self.betSpread.split("-")

        bet = 0
        if len(strategy) == 1: #Flat bets
            bet = int(strategy[0])
        else:
            minBet = int(strategy[0])
            maxBet = int(strategy[1])

            tcount = self.get_true_count()
            bet = int (1.2 * tcount)

            if bet < minBet:
                bet = minBet
            elif bet > maxBet:
                bet = maxBet

        self.playerBankroll -= bet
        self.playerBets.append(bet)
    #Deal card
    def deal_card(self, hand, updateRC=True):
        card = self.shoe.rm_card()
        if updateRC:
            self.update_running_count(card)
        hand.append(card)

    # Deal hands
    def deal_hands(self):

        #Deal player, dealer, player, dealer
        self.deal_card(self.playerHands[0])
        self.deal_card(self.dealerHand)
        self.deal_card(self.playerHands[0])
        self.deal_card(self.dealerHand, updateRC=False)


    def payout(self):
        dTotal = self.get_hand_total(self.dealerHand)

        for hand, bet in zip(self.playerHands, self.playerBets):
            #If the hand beat the dealer
            if (self.get_hand_total(hand) > dTotal or dTotal > 21) and self.get_hand_total(hand) <= 21:
                self.playerBankroll += (2*bet)
                self.wins += 1
            elif self.get_hand_total(hand) == dTotal and self.get_hand_total(hand) <= 21:
                self.playerBankroll += bet
            else:
                self.losses += 1

    # Play!
    def play_rounds(self, numRounds):

        for i in range(numRounds):

            self.clear_table()
            #Check if we should shuffle (grab a new deck)
            if (self.deckPen * 52) >= len(self.shoe.cards):
                self.shuffle()

            if(self.playerBankroll < self.minBet):
                print("Bankrupt!")
                return i

            self.place_bets_profbj() #todo: Change to accept any betting strategy
            self.deal_hands()

            # Check for player natural
            if self.check_natural(self.playerHands[0]):
                if self.check_natural(self.dealerHand):
                    self.playerBankroll += self.playerBets[0]
                else:
                    self.playerBankroll += (self.bjPays * self.playerBets[0])
                    self.wins += 1

                #update running count of dealer down card
                self.update_running_count(self.dealerHand[1])
                continue

            #Check for insurance
            haveNatural = self.check_natural(self.dealerHand)
            wantInsurance = self.check_insurance()

            if wantInsurance and self.get_upcard() == "A":
                insBet = self.playerBets[0]/2
                self.playerBankroll -= insBet
                if haveNatural:
                    self.playerBankroll += (self.insurancePays * insBet)
                    #update running count of dealer down card
                    self.update_running_count(self.dealerHand[1])
                    continue
            else:
                if haveNatural:
                    self.update_running_count(self.dealerHand[1])
                    continue

            #Player plays
            self.play_player(handIndex=0)
            #Dealer plays
            self.play_dealer()
            #Payout
            self.payout()
        return numRounds

    def clear_table(self):
        self.playerHands = [[]]
        self.dealerHand = []
        self.playerBets = []
        self.playerState = ""

    def shuffle(self):
        del self.shoe
        self.shoe = ph.Deck(self.deckNumber)
        self.runningCount = 0




if __name__ == "__main__": #For testing

    file = open("ConfigureBJ.yaml", "r")
    cfg = load(file, Loader=FullLoader)
    state = State(cfg)
    file.close()
    #Let's play a few practice rounds

    for count in range(1000000):
        state.play_rounds()
        print(count, f": {state.playerBankroll}")
        if (state.playerBankroll < state.minBet) :
            state.playerBankroll = 1000
            print("Bankrupt - resetting")
