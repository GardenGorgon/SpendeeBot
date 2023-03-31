"""
CS4100

This class represents a player for a game of Splendee. 
A player takes in a strategy (how they choose to play) and
has a number of points, set of chips, and set of cards they hold.

At initialization, a player have 0 points and no cards/chips.
"""

class Player():
    def __init__(self, strategy):
        self.strategy = strategy
        self.points = 0 
        self.chips = []
        self.cards = []

    def num_cards(self):
        return len(self.cards)
    
    def num_chips(self):
        return len(self.chips)