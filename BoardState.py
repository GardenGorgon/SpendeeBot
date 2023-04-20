# -*- coding: utf-8 -*-
"""
acceptable colors will be:
    blue
    red
    green
    black
    white
    
    Chip piles will be in that order
"""

class BoardState: #This tracks everything on the board, and probably has some functions too
    def __init__(self, nobles, deck3, deck2, deck1, chipPile):
        self.nobles = nobles #The deck of nobles on the board
        self.deck3 = deck3 #The deck of level 3 cards
        self.deck2 = deck2 #The deck of level 2 cards
        self.deck1 = deck1 #The deck of level 1 cards
        self.chipPile = chipPile #An array of length five. It contains 5 ChipStacks
    
    def buyCard(self, deckLevel, cardNumber): #Deck level is the rarity, card number is which card in the row
        #Not defined lol
        #Coins will return to the central chipPile when they are spent here
        return ("Lol not implimented")
    
    def takeChips(self, chip1, chip2, chip3): #Which 3 chips the player wants to take
        #If a pile is empty it'll say "Lol there werent any [COLOR] chips"
        return ("Lol not implimented")
    
    def checkNobles(self, nobles):# At the end of a players turn, call this function
        #It will check if they deserve a noble and give them one while removing that noble from
        #The BoardStates collection
        return ("Lol not implimented")
    
# -*- coding: utf-8 -*-

