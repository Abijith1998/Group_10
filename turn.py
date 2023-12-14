from cards import Card
from utils import check_win


class Turn(object):
# Captures the sequence of a turn, including:
#   - Initialization of hand cards and open card before the first turn
#   - Player's chosen action
#   - Opposite player's counteraction in the case of PL2 or PL4

    def __init__(self, deck, player_1, player_2, agent):
        # Initializes a turn with a standard deck, players, and an open card.
        self.deck = deck
        self.player_1 = player_1
        self.player_2 = player_2
        self.card_open = self.deck.draw_from_deck()
        self.start_up()
    
    def start_up(self):
        while self.card_open.value not in range(0,10):
            print (f'Inital open card {self.card_open.print_card()} has to be normal')
            self.card_open = self.deck.draw_from_deck()
        
        print (f'Inital open card is {self.card_open.print_card()}\n') 
        
        for i in range (7):
            self.player_1.draw(self.deck, self.card_open)
            self.player_2.draw(self.deck, self.card_open)
            
    def action(self, player, opponent, agent, algorithm):
        # Reflects the active player's action only if their hand has not won yet.
        # One player utilizes the RL algorithm, while the other makes random choices.

        player_act = player
        player_pas = opponent
        player_act.evaluate_hand(self.card_open)

        self.count = 0
        
        # When player can play a card directly
        if len(player_act.hand_play) > 0:
            
            if player_act == self.player_1:
                player_act.play_agent(self.deck, self.card_open, agent, algorithm)
            else:
                player_act.play_rand(self.deck)
                
            self.card_open = player_act.card_play
            player_act.evaluate_hand(self.card_open)

        # When player has to draw a card
        else:
            print (f'{player_act.name} has no playable card')
            player_act.draw(self.deck, self.card_open)
            
            # When player draw a card that is finally playable
            if len(player_act.hand_play) > 0:
                
                if player_act == self.player_1:
                    player_act.play_agent(self.deck, self.card_open, agent, algorithm)
                else:
                    player_act.play_rand(self.deck)
                
                self.card_open = player_act.card_play
                player_act.evaluate_hand(self.card_open)
            
            # When player has not drawn a playable card, do nothing
            else:
                player_act.card_play = Card(0,0)
        
        if check_win(player_act) == True: return
        if check_win(player_pas) == True: return
        
        if player_act.card_play.value == "PL4":
            self.action_plus(player   = player_act, 
                             opponent = player_pas, 
                             penalty  = 4)
        
        if player_act.card_play.value == "PL2":
            self.action_plus(player   = player_act, 
                             opponent = player_pas, 
                             penalty  = 2)
        
    def action_plus(self, player, opponent, penalty):
        # Reflects the process when a PL2 or PL4 card is played. If the opponent can counter with the same type of card, they will do so.
        # This continues until a player does not have the respective card.

        player_act = player
        player_pas = opponent
        hit, self.count = True, 1

        while hit == True:
            hit = False
            for card in player_pas.hand:
                if card.value == "PL"+str(penalty):
                    player_pas.play_counter(self.deck, self.card_open, plus_card = card)
                    hit = True
                    self.count += 1
                    break
                    
            if check_win(player_pas) == True: return 

            if hit == True:
                hit = False
                for card in player_act.hand:
                    if card.value == "PL"+str(penalty):
                        player_act.play_counter(self.deck, self.card_open, plus_card = card) 
                        hit = True
                        self.count += 1
                        break
                        
            if check_win(player_act) == True: return
        
        if self.count%2 == 0:
            print (f'\n{player_act.name} has to draw {self.count*penalty} cards')
            for i in range (self.count*penalty): player_act.draw(self.deck, self.card_open)

        else:
            print (f'\n{player_pas.name} has to draw {self.count*penalty} cards')
            for i in range (self.count*penalty): player_pas.draw(self.deck, self.card_open)