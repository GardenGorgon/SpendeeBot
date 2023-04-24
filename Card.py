"""
acceptable colors will be:
    blue
    red
    green
    black
    white
"""

class Card:
    def __init__(self, reward, color, blue, red, green, black, white):
        self.reward = reward #Point reward. An Int.
        self.color = color #Color the card is worth. A string
        self.cost = {
            "blue": blue,
            "red": red,
            "green": green,
            "black": black,
            "white": white
        } #This is an array with length 5, containing 5 chip piles. One for each color
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
