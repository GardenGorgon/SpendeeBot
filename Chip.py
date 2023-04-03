# -*- coding: utf-8 -*-
"""
acceptable colors will be:
    blue
    red
    green
    black
    white

I still cant decide if we should count 
amounts as a feature of the coin object
or if we should just count them seperately
"""

class Chip:
    def __init__(self, color, amount):
        self.color = color #The color of the coin
        self.amount = amount #How many this pile has
