"""
acceptable colors will be:
    blue
    red
    green
    black
    white
"""
import csv
from random import sample, shuffle, seed, randint, choice

ACTIONS = ('t', 'b') 
GEMS = ('blue', 'red', 'green', 'black', 'white', 'b', 'r', 'g', 'k', 'w') # Steph: okay, so here, I just add the symbols bc these are how script actions are read
GEMS_SCRIPT_READER = {'b', 'r', 'g', 'k', 'w'} # this is how the gems get read in from the csv
CARD_LEVELS = 3
SCRIPT_TO_GEM_MAP = {'b' : 'blue', 
                     'r' : 'red', 
                     'g' : 'green',
                     'k' : 'black',
                     'w' : 'white'} # this is for when we read in the csv, we can create the stacks
GEM_TO_SCRIPT_MAP = {'blue'  : 'b', 
                     'red'   : 'r', 
                     'green' : 'g',
                     'black' : 'k',
                     'white' : 'w'} # this is for when we read in the csv, we can create the stacks


class ChipStack: #This class reperesents a stack of chips
    def __init__(self, amount=0):
        self.gems = {'blue': amount, 
                     'red': amount, 
                     'green': amount, 
                     'black': amount, 
                     'white': amount}
        
        
    def alterChip(self, color, amt): #Alter the chip stack
        assert (self.gems[color] + amt >= 0) # changed '>' to '>='
      
        self.gems[color] += amt
        
        return self.gems[color]
    
    def items(self):
        return self.gems.items()
    
    def keys(self):
        return self.gems.keys()
    
    def __str__(self):
        s = ''
        for gem in self.gems.keys(): # preserve gem order
            s += GEM_TO_SCRIPT_MAP[gem] + str(self.gems.get(gem)) # Steph: changed this to render differently
        return s
    
    
class Noble: # Represents a noble.
    def __init__(self, points=0, price=None):
        self.points = points # number of win points
        self.price = price
        if price is None:
            self.price = ChipStack(0) # Initialize a chipstack with a size of 0

    def __str__(self):
        # s = ""
        # s += "\n Chipstack: "
        # for i in self.price.price.gems:
        #     amt = self.price.price.gems[i]
        #     color = i
        #     s += GEM_TO_SCRIPT_MAP[color] + str(amt) + "\n"
        return '[' + str(self.points) + '|' + str(self.price) + ']'
    
    @classmethod
    def from_str(cls, string):
        '''Alternative constructor from string'''
        # print("string: " + str(string))
        points, price = Noble.parse_str(string)
        return cls(points, price)
    
    def parse_str(string):
        '''Parse from string (assumes serialization by self method str)'''
        assert len(string) >= 8
        points = int(string[1])
        num_gems = (len(string) - 4)//2
        assert num_gems >= 2 and num_gems <= 3
        chipstack = ChipStack()
        for n in range(num_gems):
            gem_script = string[2*n + 3]
            gem = SCRIPT_TO_GEM_MAP[gem_script]
            count = int(string[2*n + 4])
            print("In parse str")
            chipstack.alterChip(gem, count) # alter nobles price per gem
        return points, chipstack

class Card: # Represents a card
    def __init__(self, gem='', points=0, price=None):
        self.gem = gem # title gem
        self.points = points # number of win points
        self.price = price 
        if price is None:
            self.price = ChipStack(0)

    def __str__(self):
        return '[' + self.gem + str(self.points) + '|' + str(self.price) + ']'
    
"""I was focused on getting game.py out the door. Somebody has to help me tweak this 
so it reads our modified CSV"""
def read_cards_from_csv(file_name): # We gotta tweek this so it works with our modified CSV, I havent yet
    cards = [[], [], []] #The three decks
    reader = csv.reader(open(file_name))
    next(reader, None) # skip header
    for line in reader:
        assert len(line) == 8
        card = Card()
        level = int(line[0]) - 1   # card level
        card.gem = line[1]         # card gem
        card.points = int(line[2]) # card reward
        for gem, amount in zip(GEMS[:-1], line[3:]): 
            if len(amount) == 1:
                card.price.alterChip(gem, int(amount))  # we want to basically add the gem costs to chipstack
        cards[level].append(card)
    return tuple([tuple(cards[n]) for n in range(CARD_LEVELS)])


#These lines are initializing the decks of nobles and cards
NOBLES = tuple(map(Noble.from_str, ['[3|r4g4]', '[3|g4b4]', '[3|b4w4]', '[3|w4k4]', '[3|k4r4]',
    '[3|r3g3b3]', '[3|b3g3w3]', '[3|b3w3k3]', '[3|w3k3r3]', '[3|k3r3g3]']))
CARDS = read_cards_from_csv('cards.csv')
CARD_LEVELS = 3


class SplendorPlayerState: #Players own the actions to change the boardstate now
    def __init__(self, name):
        self.name = name
        self.cards = ChipStack()
        self.gems = ChipStack()
        self.points = 0

    def __str__(self): #Print out everything you own
        s = self.name + '| ' + "points: " + str(self.points) + '\n'
        s += 'cards:' + '\n' + str(self.cards) + '\n'
        s += 'gems:' + '\n' + str(self.gems) + '\n'
        s += '\n'
        return s

    def purchase_card(self, card):
        '''Does card purchase. Returns false if player can't afford card'''
        """This section checks if the player can afford the card"""
        # Creating the purchasing power total
        print('card: ' + str(card))
        purchasingPower = ChipStack()
        purchasingPowerDict = purchasingPower.gems
        for key in purchasingPowerDict.keys():
            purchasingPower.gems[key] = self.num_color_card(key) # I added this function 
            purchasingPower.gems[key] += self.gems.gems[key] 
            
        # Creating how many coins you are missing if you are missing any
        shortage = ChipStack()
        wasShort = False
        for color, amt in card.price.items(): # Price is stored in the chipstack object so we call items on the price
            diff = amt - purchasingPower.gems[color]
            if diff > 0:
                print("Here")
                shortage.alterChip(color, amt)
                wasShort = True
        if wasShort == True:
            print("You can't afford this card, you are short by this many coins: " + str(shortage))
            return False
        
        """This section actually does the purchasing"""        
        # if player can afford card, do actual payment
        discountedPrice = ChipStack() # Discounted price is the price after the discount from your gem cards
        discountedPriceDict = discountedPrice.gems
        for key in discountedPriceDict.keys():
            discountedPrice.gems[key] = card.price.gems[key] - self.cards.gems[key]
        for gem, price in discountedPrice.gems.items(): # Spending the players gem chips
            # print("gem: " + str(gem))
            # print("price: " + str(price))
            self.gems.alterChip(gem, -price)
            
        self.cards.alterChip(card.gem, 1) # add bought card to player's cards
        self.points += card.points             # add card reward for buying it
        return True
    # We successfully bought the card

    def get_noble(self, nobles):
        '''Attempts to acquire noble card. In case of success removes taken noble from input list'''
        noble_list = []
        for n, noble in enumerate(nobles):
            can_afford = True
            for gem, price in noble.price.items():
                if self.cards.gems[gem] < price: # access card chipstack 
                    can_afford = False
                    break
            if can_afford:
                noble_list.append(n)
        
        if noble_list:
            n = randint(1, len(noble_list))# choose random if more than one available
            noble = nobles.pop(noble_list[n])
            self.points += noble.points
            #We just pop the noble from the available noble list, and add its points to the player
    
    def num_color_card(self, gem):
        """ informs you how many cards of the given gem this player has"""
        return self.cards.gems[gem]

ACTIONS = ('t', 'b') #Take and buy
#The format of our Actions will have to be t and then the colors seperated by space
#For buy it would be b pos where pos is the position of the card you want
#Pos will look like 1 4 (Level and the position on that row)
class Action:
    take = ACTIONS[0] # take gems
    purchase = ACTIONS[1] # purchase table card

    def __init__(self, action_type, gems, pos):
        self.type = action_type
        self.gems = gems
        self.pos = pos #Position of a card

    def __str__(self):
        if self.type == Action.take: 
            return Action.take + ''.join(self.gems)
        else:
            return self.type.join(map(str, self.pos))

    @classmethod
    def from_str(cls, action_str):
        try:
            action_type, gems, pos = Action.parse(action_str)
            return cls(action_type, gems, pos)
        except Exception:
            raise AttributeError('Invalid action string {}'.format(action_str))

    @staticmethod
    def parse(action_str):
        action_type = action_str[0] # should be one of ACTIONS
        gems = None
        pos = None

        print("action_str: " + str(action_str))
        if action_type == Action.take: # If the action was take, we split everything after the t and those get put into the gems variable
            gems = [g for g in action_str[1:]] # I removed the split so that gems are separated in a list
        elif action_type == Action.purchase: 
            print("I get here!")
            pos = Action.scan_pos(action_str) 
        else:
            raise AttributeError('Invalid action type {} (in action {})'.format(action_type, action_str))
        
        return action_type, gems, pos

    @staticmethod
    def scan_pos(action_str):
        """ Format: p[level][pos]  """
        print("action_str: " + str(action_str))
        assert len(action_str) == 3
        level = int(action_str[1]) - 1
        pos = int(action_str[2]) - 1
        return level, pos
    
class SplendorGameRules:
    def __init__(self):
        self.num_players = 2
        self.max_open_cards = 4 # open cards on table
        self.win_points = 15
        self.max_player_gems = 10
        self.max_nobles = self.num_players + 1
        self.max_gems_take = 3 # max gems to take
        self.max_gems = 7

class SplendorGameState:
    '''This tracks gamestate'''
    def __init__(self, player_names, rules):
        assert rules.num_players == len(player_names)

        self.rules = rules #Holds onto all the numbers we reference later
        self.num_moves = 0 #Turn counter
        self.player_to_move = 0 #The next player to go, 0 is player one

        # init nobles
        self.nobles = sample(NOBLES, self.rules.max_nobles) # Random sampling our nobles to make em

        # init decks and cards 
        self.decks = []
        self.cards = [] # open cards on table
        for level in range(CARD_LEVELS):
            cards = list(CARDS[level])#
            shuffle(cards)
            open_cards = self.rules.max_open_cards
            self.decks.append(cards[:-open_cards])
            self.cards.append(cards[-open_cards:])

        # init gems
        self.gems = ChipStack(self.rules.max_gems) 


        # init players
        self.players = [SplendorPlayerState(name) for name in player_names]

    def __str__(self):
        s = 'turn:' + str(self.num_moves) + ' player:' + str(self.player_to_move) + '\n'
        
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

    def new_table_card(self, level, pos):
        '''Put new card on table if player reserved/purchased card'''
        new_card = None
        if self.decks[level]:
            new_card = self.decks[level].pop()
        self.cards[level][pos] = new_card

    def action(self, action):
        player = self.players[self.player_to_move]

        if action.type == Action.take: 
            print("Action: t")
            gems = action.gems
            print("gems: " + str(gems))
                
            """
            Just some leftovers we may or may not need. Might as well comment them.
            
            if len(gems) > self.rules.max_gems_take:
                raise AttributeError('Can\'t take more than {} gems'.format(self.rules.max_gems_take))
            

            if player.gem_count + len(gems) > self.rules.max_player_gems:
                raise AttributeError('Player can\'t have more than {} gems'.format(self.rules.max_player_gems))
            """
            # This part actually takes gems from the table
            self_chipstack = self.gems
            for gem in gems:
                script_to_gem = ""
                try:
                    script_to_gem = SCRIPT_TO_GEM_MAP[gem]  
                except Exception:
                    raise AttributeError('Invalid gem given {}'.format(str(gem)))

                if gem not in GEMS:
                    raise AttributeError('Invalid gem {}'.format(gem))
                if self_chipstack.gems[script_to_gem] == 0:
                    raise AttributeError('Not enough {} gems on table'.format(gem))
                player.gems.alterChip(script_to_gem, 1) # add to player
                self.gems.alterChip(script_to_gem, -1)  # remove from table 

            """This section is for preventing softlock.
            If a player has more than the max number of gems, we take 3 away
            """
            playerGemCount = 0 # Calculating how many gems the player has
            player_chips = player.gems.gems # gets kind weird here but chipstack has a dict called gems
            for key in player_chips.keys():
                playerGemCount += player_chips[key]
                
            if playerGemCount >= self.rules.max_player_gems: # To prevent softlock, we are randomly removing players chips if they get too greedy
                print("You already have the max number of gems! Now I'm going to take some away at random! Bwa ha ha ha!") # evil
                for i in range(3):
                    punishmentPiles = []
                    player_chipstack_dict = player.gems.gems
                    for key in player_chipstack_dict.keys():
                        if player.gems.gems[key] > 0:
                            punishmentPiles.append(key)
                    punishment = choice(punishmentPiles)
                    player.gems.alterChip(punishment, -1) # remove chip from player
                    self.gems.alterChip(punishment, 1) # wait, should this be +1 if we are grabbing from the player?

        elif action.type == Action.purchase: 
            level, pos = action.pos 
            print("Level: " + str(level))
            print("pos " + str(pos))
            if level < 0 or level >= CARD_LEVELS:
                raise AttributeError('Invalid deck level {}'.format(level + 1))
            if pos < 0 or pos >= self.rules.max_open_cards:
                raise AttributeError('Invalid card position {}'.format(pos + 1))

            card = self.cards[level][pos]
            if not player.purchase_card(card):
                raise AttributeError('Player can\'t afford card') # I told the player exactly how many they were missing, we can probably get rid of that
            self.new_table_card(level, pos) # Replacing the card
            player.get_noble(self.nobles) # try to get noble


        else: # The command was bad
            raise AttributeError('Invalid action type {}'.format(action.type))

        self.player_to_move = (self.player_to_move + 1) % self.rules.num_players
        if self.player_to_move == 0: # round end
            self.num_moves += 1

    def check_win(self):
        for player in self.players:
            if player.points >= self.rules.win_points:
                return True
        return False

    def best_player(self):
        '''Returns name of best player'''
        scores = [(player.score, player.name) for player in self.players]
        return sorted(scores, reverse=True)[0]
        
    # -*- coding: utf-8 -*-

