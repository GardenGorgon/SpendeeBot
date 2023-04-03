"""
CS4100

This class represents a player for a game of Splendee. 
A player takes in a strategy (how they choose to play) and
has a number of points, set of chips, and set of cards they hold.

At initialization, a player have 0 points and no cards/chips.
"""
from Chip import Chip

class Player():
    
    def __init__(self, strategy, points: int=0, chips: list[Chip]=[], cards=[], name: str = "Agent"):
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
        return len(self.chips)
    
    def num_color_chip(self, color: str):
        # returns the number of chips of a specific color
        total_color = 0
        for i in self.chips:
            if i.color == color:
                total_color += 1
        return total_color
    
    def num_unique_chip(self):
        # returns the number of unique chip colors
        colors = [i.color for i in self.chips]
        return len(set(colors))