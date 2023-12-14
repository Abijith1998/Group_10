import random
from utils import underline


class Player(object):
# A player is characterized by a list of cards representing their hand.
# Players can have a name, a hand of cards, and a playable hand.
# Therefore, the state of players can be determined.

    
    def __init__(self, name, agent):
        self.name         = name
        self.hand         = list()
        self.hand_play    = list()
        self.card_play    = 0
        self.state        = dict()
        self.actions      = dict()
        self.action       = 0
        agent.prev_state  = 0
    
    def evaluate_hand(self, card_open):
    
    # Iterates through each card in the player's hand. Evaluation depends on whether the card is open.
    # Required parameter: card_open as card

        
        self.hand_play.clear()
        for card in self.hand:
            if card.evaluate_card(card_open.color, card_open.value) == True:
                self.hand_play.append(card)
    
    def draw(self, deck, card_open):
    # Adds a card to the player's hand and evaluates the hand.
    # Required parameters:
    #   - deck: deck
    #   - card_open: card

        
        card = deck.draw_from_deck()
        self.hand.append(card)
        self.evaluate_hand(card_open)
        print (f'{self.name} draws {card.print_card()}')
        
    def identify_state(self, card_open):
        # The player's state is determined by iterating through the player's hand for each property of the state.
        norm_cards = {"RED":2,"GRE":2,"BLU":2,"YEL":2}
        spec_cards = {"SKI":1,"REV":1,"PL2":1}
        wild_cards = {"PL4":1,"COL":1}
    
        self.state = dict()
        self.state["OPEN"] = card_open.color
        if self.state["OPEN"] not in ["RED","GRE","BLU","YEL"]: random.choice(["RED","GRE","BLU","YEL"])
        
        # State properties: normal hand cards
        for key, val in zip(norm_cards.keys(), norm_cards.values()):
                self.state[key] = min([1 if (card.color == key) and (card.value in range(0,10)) else 0 for card in self.hand].count(1),val)
        
        # State properties: special hand cards
        for key, val in zip(spec_cards.keys(), spec_cards.values()):
                self.state[key] = min([1 if (card.value == key) else 0 for card in self.hand].count(1),val)
        
        # State properties: wild hand cards
        for key, val in zip(wild_cards.keys(), wild_cards.values()):
                self.state[key] = min([1 if (card.value == key) else 0 for card in self.hand].count(1),val)
        
        # State properties: normal playable cards
        for key, val in zip(norm_cards.keys(), norm_cards.values()):
                self.state[key+"#"] = min([1 if (card.color == key) and (card.value in range(0,10)) else 0 for card in self.hand_play].count(1),val-1)
        
        # State properties: special playable cards
        for key, val in zip(spec_cards.keys(), spec_cards.values()):
                self.state[key+"#"] = min([1 if card.value == key else 0 for card in self.hand_play].count(1),val)
    
    def identify_action(self):

        # Evaluates all actions available to the player based on their hand and the open card.

        norm_cards = {"RED":2,"GRE":2,"BLU":2,"YEL":2}
        spec_cards = {"SKI":1,"REV":1,"PL2":1}
        wild_cards = {"PL4":1,"COL":1}
        
        # Action properties: normal playable cards
        for key in norm_cards.keys():
            self.actions[key] = min([1 if (card.color == key) and (card.value in range(0,10)) else 0 for card in self.hand_play].count(1),1)
        
        # Action properties: special playable cards
        for key in spec_cards.keys():
            self.actions[key] = min([1 if card.value == key else 0 for card in self.hand_play].count(1),1)
        
        # Action properties: wild playable cards
        for key in wild_cards.keys():
            self.actions[key] = min([1 if card.value == key else 0 for card in self.hand_play].count(1),1)
     
    def play_agent(self, deck, card_open, agent, algorithm):
        # Represents an intelligent move by a player supported by the RL algorithm, involving:
        #   - Identification of the player's state and available actions
        #   - Choosing a card to play
        #   - Removing the chosen card from the hand and replacing the open card with it
        #   - Updating Q-values in the case of Temporal Difference (TD)

        # Required parameters:
        #   - deck: deck
        #   - card_open: card

        # Identify state & actions for action selection
        self.identify_state(card_open)
        self.identify_action()
        
        # Agent selects action
        self.action = agent.step(self.state, self.actions)

        # Selected action searches corresponding card
        # Playing wild card
        if self.action in ["COL","PL4"]:
            for card in self.hand:            
                if card.value == self.action:
                    break

        # Playing normal card with different color
        elif (self.action in ["RED","GRE","BLU", "YEL"]) and (self.action != card_open.color):
            for card in self.hand:
                if (card.color == self.action) and (card.value == card_open.value):
                    break

        # Playing normal card with same color
        elif (self.action in ["RED","GRE","BLU", "YEL"]) and (self.action == card_open.color):
            for card in self.hand:
                if (card.color == self.action) and (card.value in range(0,10)):
                    break

        # Playing special card with same color
        elif (self.action not in ["RED","GRE","BLU", "YEL"]) and (self.action != card_open.value):
            for card in self.hand:
                if (card.color == card_open.color) and (card.value == self.action):
                    break

        # Playing special card with different color
        else:
            for card in self.hand:
                if card.value == self.action:
                    break

        # Selected card is played
        self.card_play = card
        self.hand.remove(card)
        self.hand_play.pop()
        deck.discard(card)
        print (f'\n{self.name} plays {card.print_card()}')

        if (self.card_play.value in ["COL","PL4"]):
            self.card_play.color = self.choose_color()
        
        # Update Q Value           
        if algorithm == "q-learning":
            agent.update(self.state, self.action)      

    def play_rand(self, deck):
        # Represents a player's random move, involving:
        #   - Shuffling the player's hand cards
        #   - Iterating through hand cards and choosing the first available card to be played
        #   - Removing the chosen card from the hand and replacing the open card with it

        # Required parameter:
        #   - deck: deck

        random.shuffle(self.hand_play)
        for card in self.hand:
            if card == self.hand_play[-1]:
                self.card_play = card
                self.hand.remove(card)
                self.hand_play.pop()
                deck.discard(card)
                print (f'\n{self.name} plays {card.print_card()}')
                break

        if (self.card_play.color == "WILD") or (self.card_play.value == "PL4"):
            self.card_play.color = self.choose_color()  
            
    def play_counter(self, deck, card_open, plus_card):
        # Represents a player's counter move to a plus card.

        # Required parameters:
        #   - deck: deck
        #   - card_open: card
        #   - plus_card: card

        
        for card in self.hand:
            if card == plus_card:
                self.card_play = card
                self.hand.remove(card)
                deck.discard(card)
                self.evaluate_hand(card_open)
                print (f'{self.name} counters with {card.print_card()}')
                break
        
    def choose_color(self):
        # Chooses a card color when a player plays PL4 or WILD COL.
        # The color is determined by the majority color in the active player's hand.

        colors = [card.color for card in self.hand if card.color in ["RED","GRE","BLU","YEL"]]
        if len(colors)>0:
            max_color = max(colors, key = colors.count)
        else:
            max_color = random.choice(["RED","GRE","BLU","YEL"])

        print (f'{self.name} chooses {max_color}')
        return max_color
    
    def show_hand(self):
        underline (f'\n{self.name}s hand:')
        for card in self.hand:
            card.show_card()
        
    def show_hand_play(self, card_open):
        underline (f'\n{self.name}s playable hand:')
        self.evaluate_hand(card_open)
        for card in self.hand_play:
            card.show_card()