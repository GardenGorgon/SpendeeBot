"""
CS4100

This class represents the state of a game of Spendee. 
Script moves for a player:

grabChips [color] [number] [color] [number] ... until 5 chips are selected
buyCard   [name?]
buyNoble  [name?]
help      displays instructions

"""
from Player import Player

commands = ['grabChips', 'buyCard', 'buyNoble', 'help']

class SpendeeGameState():

    def __init__(self, players: list[Player]=[], point_goal: int = 15):
        """
        players: the list of players in the game
        point_goal: the points needed to win the game. Defaults to 15. 
        TODO: Add a board param?
        """
        self.players = players
        self.point_goal = point_goal

    def play_game(self):
        """
        TODO: Plays the game. 
        """
        while (not self.is_game_over):
            self.is_game_over = True
            for player in self.players:
               # successful_move = False
               # while(not successful_move):
               #    nextMove = player.strategy(self) 
               #    successful_move = board(nextMove, player) # maybe return bool? and also changes board state
               #    if (successful_move): display_action(nextMove) display_board()
               return  
        
        for player in self.players:
            if player.points == self.point_goal:
                print(player.name + " won!")

    def is_game_over(self):
        """
        Returns true if a player has reached the point goal.
        """
        for player in self.players:
            if player.points == self.point_goal:
                return True
        return False
    
    def display_board(self):
        # TODO: 
        return 0
    
    def display_instructions(self):
        # TODO: 
        return ""
    
    def display_action(self, action):
        # TODO: 
        return ""