"""
CS4100

This class represents the state of a game of Spendee. 
Script moves for a player:

grabChips [color] [number] [color] [number] ... until 5 chips are selected
buyCard   [name?]
help      displays instructions

"""
import random

from BoardState import BoardState
from Player import Player
import csv

from Noble import Noble
from Card import Card

commands = ['grabChips', 'buyCard', 'help']

class SpendeeGameState():

    def __init__(self, board: BoardState, rules, players: list[Player]=[], point_goal: int = 15):
        """
        players: the list of players in the game
        point_goal: the points needed to win the game. Defaults to 15. 
        TODO: Add a board param?
        """
        self.players = players
        self.point_goal = point_goal
        self.board = board
        self.rules = rules

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
            if player.points >= self.point_goal:
                return True
        return False

    def give_player_noble(self,player,noble):
        for color in ["blue", "red", "green", "black", "white"]:
            if player.num_color_cards(color) != noble.cost[color]:
                return False
        #otherwise give the player 3 points and remove the noble from the game.
        player.points +=3
        return True #we might want to change the return type here.

    def generate_nobles(self):
        all_nobles = list()
        with open('nobles.csv') as nobles_data:
            csv_reader = csv.DictReader(nobles_data)
            for row in csv_reader:
                all_nobles.append(noble(row['points'], row['blue'], row['red'], row['green'], row['black'], row['white']))
        self.nobles_list = random.sample(all_nobles,3)

    def create_shop(self):
        self.card_inventory = {1:list(),2:list(),3:list()}
        self.card_shop = {1:list(),2:list(),3:list()}

        with open('cards.csv') as card_data:
            csv_reader = csv.DictReader(card_data)
            for row in csv_reader:
                self.card_inventory[row['level']].append(Card(row['points'],row['color'],
                                                              row['blue'],row['red'],row['green'],row['black'],row['white']))
        for rank in range(1,4,1):
            random_card = self.card_inventory.pop(self.card_inventory[rank][random.randint(0,len(self.card_inventory[rank]))])
            self.card_shop[rank].append(random_card)

    def refill_shop(self,rank_num):
        random_card = self.card_inventory.pop(self.card_inventory[rank_num][random.randint(0,len(self.card_inventory[rank_num]))])
        self.card_shop.append(random_card)

    def can_player_buy_card(self,player,card):
        """
        checks if the given player is able to purchase the given card
        :param player:
        :param card:
        :return: Boolean
        """
        check_tokens = {}

        # loop through and check if the player has enough cards to purchase the card
        for color in {"blue",'red','green','black','white'}:
            if player.num_color_cards(color) < card.costPile[color]:
                check_tokens[color] = card.costPile[color] - player.player.num_color_cards(color)


        if check_tokens.size == 0 :
            return True
        # loop through and check if the player has enough tokens to supplement which cards they do not have
        for color in check_tokens:
            if player.num_color_chip(color) < check_tokens[color]:
                return False
        return True

    def player_buy_card(self,player,card):
        if(self.can_player_buy_card(player,card)):
            if card in self.card_shop[0]:
                self.card_shop[0].remove(card)
            elif card in self.card_shop[1]:
                self.card_shop[1].remove(card)
            elif card in self.card_shop[2]:
                self.card_shop[0].remove(card)

            # add card to player's inventory and remove necessary tokens
            player.add_card(card)

            #remove tokens if needed
            for x in range(len(player.chips)):
                player.chips[x].remChip(max(0, card.cost[x]-player.num_color_cards(self.num_to_color(x))))

    # given a number 0-4, translates it into a color string
    def num_to_color(self, x):
        if x == 0:
            return 'blue'
        elif x == 1:
            return 'red'
        elif x == 2:
            return 'green'
        elif x == 3:
            return 'black'
        elif x == 4:
            return 'white'
        else:
            return ""
        

class SplendorGameRules:
    def __init__(self):
        random.seed(1828)
        self.num_players = 2
        self.max_open_cards = 4 # open cards on table
        self.win_points = 15
        self.max_player_hand_cards = 10
        self.max_nobles = self.num_players + 1
        self.max_gems_take = 5       # max gems to take
        self.max_same_gems_take = 3  # max same color gems to take
        self.min_same_gems_stack = 4 # min size of gem stack from which you can take 2 same color gems
        self.max_gems = 7 # max same color gems on table (except gold)
        if self.num_players < 4:
            self.max_gems = 2 + self.num_players
