"""
CS4100

This class represents the state of a game of Spendee. 
"""
import random

from BoardState import BoardState
from Player import Player
from Action import Action
import csv

from Noble import Noble
from Card import Card

commands = ['grabChips', 'buyCard', 'help']

GOLD_GEM = 'y'
GEMS = ('r', 'g', 'b', 'w', 'k', GOLD_GEM) # red, green, blue, white, black, yellow(gold)
ACTIONS = ('t', 'r', 'p', 'h') # take gems, reserve card, purchase card, purchase hand card
CARD_LEVELS = 3


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

    def __str__(self):
        s = 'move:' + str(self.num_moves) + ' player:' + str(self.player_to_move) + '\n'
        
        s += 'nobles: '
        for noble in self.nobles:
            s += str(noble) + ' '
        s += '\n'

        for n, card_list in enumerate(reversed(self.cards)):
            s += str(CARD_LEVELS - n) + ': '
            for card in card_list:
                if card:
                    s += str(card) + ' '
            s += '\n'

        s += 'gems:' + str(self.gems) + '\n'

        for player in self.players:
            s += str(player)

        return s 

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

    def new_table_card(self, level, pos):
        '''Put new card on table if player reserved/purchased card'''
        new_card = None
        if self.decks[level]:
            new_card = self.decks[level].pop()
        self.cards[level][pos] = new_card

    def action(self, action):
        player = self.players[self.player_to_move]

        if action.type == Action.take: 
            gems = action.gems
            unique_gems = list(set(gems))
            if len(gems) > self.rules.max_gems_take:
                raise AttributeError('Can\'t take more than {} gems'.format(self.rules.max_gems_take))
            if len(unique_gems) == 1: # all same color
                if self.gems.get(unique_gems[0]) < self.rules.min_same_gems_stack:
                    raise AttributeError('Should be at least {} gems in stack'.format(self.rules.min_same_gems_stack))
                if len(gems) != 1 and len(gems) > self.rules.max_same_gems_take: 
                    raise AttributeError('Can\'t take more than {} identical gems'.format(self.rules.max_same_gems_take))
            if len(unique_gems) > 1 and len(unique_gems) != len(gems): 
                raise AttributeError('You can either take all identical or all different gems')
            if player.gem_count + len(gems) > self.rules.max_player_gems:
                raise AttributeError('Player can\'t have more than {} gems'.format(self.rules.max_player_gems))

            for gem in gems:
                if gem not in GEMS:
                    raise AttributeError('Invalid gem {}'.format(gem))
                if gem == GOLD_GEM:
                    raise AttributeError('You are not allowed to take gold ({}) gem'.format(GOLD_GEM))
                if self.gems.get(gem) == 0:
                    raise AttributeError('Not inough {} gems on table'.format(gem))
                
                player.gems.add(gem, 1)
                self.gems.add(gem, -1)

        elif action.type == Action.reserve: 
            level, pos = action.pos
            if level < 0 or level >= CARD_LEVELS:
                raise AttributeError('Invalid deck level {}'.format(level + 1))
            if pos < -1 or pos >= len(self.cards[level]):
                raise AttributeError('Invalid card position {}'.format(pos + 1))
            if len(player.hand_cards) >= self.rules.max_hand_cards:
                raise AttributeError('Player can\'t reserve more than {} cards'.format(self.rules.max_hand_cards))

            card = None
            if pos >= 0:
                card = self.cards[level][pos]
                if card is None:
                    raise AttributeError('Card already taken')
                self.new_table_card(level, pos)
            if pos == -1: # blind reserve from deck
                if not self.decks[level]:
                    raise AttributeError('Deck {} is empty'.format(level + 1))
                card = self.decks[level].pop()
            player.hand_cards.append(card)
            if self.gems.get(GOLD_GEM) > 0:
                player.gems.add(GOLD_GEM, 1)
                self.gems.add(GOLD_GEM, -1)

        elif action.type == Action.purchase: 
            level, pos = action.pos 
            if level < 0 or level >= CARD_LEVELS:
                raise AttributeError('Invalid deck level {}'.format(level + 1))
            if pos < 0 or pos >= self.rules.max_open_cards:
                raise AttributeError('Invalid card position {}'.format(pos + 1))

            card = self.cards[level][pos]
            if not player.purchase_card(card):
                raise AttributeError('Player can\'t afford card')
            self.new_table_card(level, pos)

            player.get_noble(self.nobles) # try to get noble

        elif action.type == Action.purchase_hand: 
            pos, = action.pos # position of card in hand
            if pos < 0 or pos >= len(player.hand_cards):
                raise AttributeError('Invalid card position in hand {}'.format(pos + 1))

            card = player.hand_cards[pos]
            if not player.purchase_card(card):
                raise AttributeError('Player can\'t afford card')
            player.hand_card.pop(pos) # remove card from hand

            player.get_noble(self.nobles) # try to get noble

        else:
            raise AttributeError('Invalid action type {}'.format(action.type))

        self.player_to_move = (self.player_to_move + 1) % self.rules.num_players
        if self.player_to_move == 0: # round end
            self.num_moves += 1
    

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
                all_nobles.append(Noble(row['points'], row['blue'], row['red'], row['green'], row['black'], row['white']))
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

    def best_player(self):
        '''Returns name of best player'''
        scores = [(player.score, player.name) for player in self.players]
        return sorted(scores, reverse=True)[0]
        

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
