"""
CS4100

This class represents a player for a game of Splendee. 
A player takes in a strategy (how they choose to play) and
has a number of points, set of chips, and set of cards they hold. At initialization, 
a player have 0 points and no cards/chips.
"""
from ChipStack import ChipStack

init_stack = {
    'blue' : ChipStack('blue', 0),
    'red'  : ChipStack('red', 0),
    'green': ChipStack('green', 0),
    'black': ChipStack('black', 0),
    'white': ChipStack('white', 0)
}

class Player():

    def __init__(self, strategy, points=0, chips=init_stack, cards=[], name="Agent", is_ai=False):
        """
        name: name of player
        strategy: an action that determines how this player will play when prompted by game state.
        points: number of points this player has
        chips: a dictionary of this players chips. ( color : ChipStack )
        cards: this player's set of cards
        is_ai: says if this player is ai or not
        """
        self.name = name
        self.strategy = strategy
        self.points = points
        self.chips = chips
        self.cards = cards

    def next_move(self, game_state):
        # Returns the next move given the game_state
        return self.strategy(game_state)

    def add_points(self, points):
        # Adds points to this player's total points
        self.points += points

    # //////////////////// A couple of helpers
    def num_cards(self):
        return len(self.cards)

    def num_chips(self):
        total = 0
        for color in self.chips:
            stack = self.chips[color]
            total += stack.amount
        return total

    def num_color_chip(self, color: str):
        return self.chips[color].amount # returns the number of chips of a specific color

    def num_color_cards(self, color: str):
        total_cards_of_color = 0
        for card in self.cards:
            if card.color == color:
                total_cards_of_color += 1
        return total_cards_of_color

    def num_unique_chip(self):
        # returns the number of unique chip colors
        total = 0
        for color in self.chips:
            if color.amount > 0:
                total += 1
        return total

    def add_card(self, card):
        self.cards.append(card)

