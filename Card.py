"""
acceptable colors will be:
    blue
    red
    green
    black
    white

"""

class Card:
    def __init__(self, reward, color, cost):
        self.reward = reward #Point reward
        self.color = color #Color the card is worth
        self.cost = cost #I'm imagining cost to be a dictionary
        #That looks like:
        """
            cost = {
                "green": 1,
                "blue": 1,
                "red": 1,
                "black": 1
                }
            cant decide if we should have entries for empty colors.
        """
