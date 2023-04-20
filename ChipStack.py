# -*- coding: utf-8 -*-
"""
acceptable colors will be:
    blue
    red
    green
    black
    white
"""

class ChipStack: #This class reperesents a stack of chips
    def __init__(self, color, amount):
        self.color = color #The color of the coin
        self.amount = amount #How many this pile has
    
    def addChip(self, amt): #Add Chip
        self.amount += amt
    
    def remChip(self, amt): #Remove Chip
        self.amount -= amt
        if self.amount < 0:
            self.amount = 0
        
    
