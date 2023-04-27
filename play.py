from random import randint, sample
from queue import PriorityQueue
from game import SplendorGameState, SplendorGameRules, Action
import sys
from functools import reduce

GEM_TO_SCRIPT_MAP = {'blue'  : 'b', 
                     'red'   : 'r', 
                     'green' : 'g',
                     'black' : 'k',
                     'white' : 'w'}

class HumanPlayer:
    is_ai = False
    def get_action(self, game_state):
        player_name = game_state.players[game_state.player_to_move].name
        action_str = input(player_name + ' move: ')
        return Action.from_str(action_str)

def play_game(agent_num1, agent_num2):
    player_names = ['Player 1 (AI)', 'Player 2 (AI)']
    players = [] 
    
    if(agent_num1 == 0):
        players.append(HumanPlayer())
        player_names[0] = 'Player 1'
    elif(agent_num1 == 1): # range is [0, 5]
        players.append(BasicAgent())
    elif(agent_num1 == 2):
        players.append(CheapAgent())
    elif(agent_num1 == 3):
        players.append(NobleAgent())
    elif(agent_num1 == 4):
        players.append(AdversarialAgent())
    elif(agent_num1 == 5):
        players.append(AdversarialAgent2())
    
    if(agent_num2 == 0):
        players.append(HumanPlayer())
        player_names[1] = 'Player 2'
    elif(agent_num2 == 1): # range is [0, 5]
        players.append(BasicAgent())
    elif(agent_num2 == 2):
        players.append(CheapAgent())
    elif(agent_num2 == 3):
        players.append(NobleAgent())
    elif(agent_num2 == 4):
        players.append(AdversarialAgent())
    elif(agent_num2 == 5):
        players.append(AdversarialAgent2())

    rules = SplendorGameRules()
    game = SplendorGameState(player_names, rules)

    while not game.check_win():
        for n, player in enumerate(players):
            print(game) # this STAYS
            while True: # check for invalid action inputs
                action = player.get_action(game)
                try:
                    game.action(action)
                    break
                except AttributeError as err:
                    print('Invalid action {}: {}'.format(str(action), str(err)))
                    if player.is_ai:
                        return
            if player.is_ai:
                print(player_names[n] + ' move was: ' + str(action))

    print("Final Game State:")
    print(game)
    print('best player:', game.best_player())




# given a list of cards (from the shop) determines which card has the best cost to point ratio
def cost_point_ratio(cards):
    pass
    best_ratio = 0 
    card_with_best_ratio = None
    for shop_card in cards:
        cost_to_point_ratio = float(shop_card.points) / float(shop_card.total_items_amt()) 
        if best_ratio < cost_to_point_ratio:
            best_ratio = cost_point_ratio
            card_with_best_ratio = card_with_best_ratio
    return card_with_best_ratio
    

def bestNoble(game_state, player):
    """
    given the state of the game, and a player determines which noble is optimal for the player to go for
    gamestate is useful for looking nobles, currentshop
    player is useful for determining which cards that might already contribute towards getting a noble
    """
    best_noble = None
    nobles_values_dict = dict() 
    # for all nobles in the game
    for n in game_state.nobles: 
        
        # put on the non-zero values of chipstick into the dict
        nobles_values_dict[n] = dict()
        for color in n.price.keys():
            if(n.price.gems[color] != 0):
                (nobles_values_dict[n])[color] = max(0, n.price.gems[color] - player.cards.gems[color])# subtract the cards that the player already has
        
    # for all cards in the game state shop
    # cards_sets = [cards for level, cards in enumerate(game_state.cards)]
    for card in reduce(lambda x, y : x + y, game_state.cards): # cards [[], [], ...]
        # for all nobles in the game
        for noble_val in nobles_values_dict:
            # if the gem of the card is required for that noble
            if card.gem in nobles_values_dict[noble_val].keys():
                # subtract value
                nobles_values_dict[noble_val][card.gem]-=1
    min_cost = 15
    # for all the nobles
    for noble_val in nobles_values_dict.keys():
        # sum together a value of which represents accessibility:
        # accessible factor = original_cost - already owned cards - relevant cards in shop
        accessibility_score = sum(nobles_values_dict[noble_val].values()) 
        # keep track of the lowest value and the noble that has that value
        if accessibility_score < min_cost:
            min_cost = accessibility_score
            best_noble = noble_val
    
    return best_noble
    
# given a noble, creates a list of cards that should be bought
def retrieve_cards_required_for_noble(cards, noble):
        # cards = list of cards in the shop/game state
        cards_of_required_color = list()
        for card in reduce(lambda x, y : x + y, cards):
            if noble.price.gems[card.gem]!=0:
                cards_of_required_color.append(card)
        return cards_of_required_color

def retrieve_cards_with_points(cards):
    cards_with_points = list()
    for card in reduce(lambda x, y : x + y, cards):
        if(card.points > 0):
            cards_with_points.append(card)
    return cards_with_points

def sort_cards_by_point_value(cards, game_state): 
        priority_card_queue = PriorityQueue()
        player = game_state.players[game_state.player_to_move]
        preferred_cards = retrieve_cards_with_points(cards)

        counter = 0
        while(len(preferred_cards) > 0):
            cheapest_card = preferred_cards.pop(0) 
            adjustedCardCost = 0
            counter += 1
            for color, amt in cheapest_card.price.items(): # Iterate through the cost of the card
                #color is the color at this layer, amount is the required cost at  this layer
                adjustedCardCost += max(0, (amt - player.cards.gems[color])) #Don't want to assign negative value if we have more discount than the cost
            averagePointsPerGem = adjustedCardCost/cheapest_card.points
            
            priority_card_queue.put((adjustedCardCost, counter, cheapest_card)) #We could use adjustedCardCost as our first argument, but I think it would be better as the averagePointsPerGem
            #For safety im using adjsutedCardCost for now
        return priority_card_queue

def bestThreeCoins(game_state, player, priorityListOfCards):
    """ Using the priority listOfCards we pick out which 3 coins 
    are most important to purchasing those cards. If we cant take 
    the coins relevant to our highest priority card, we pick coins 
    relevant to the second/third/fourth priority card """
    bestCoins = ["color", "color", "color"]
    playerGemsCopy = player.gems.gems.copy() # We need a copy because we don't want to alter the real thing
    playerCardsCopy = player.cards.gems.copy()
    bankGemsCopy = game_state.gems.gems.copy()

    for index, coin in enumerate(bestCoins):# For each coin we are taking
        colorWeWant = 0 # We are trying to fill in the color of the coin we want to take
        for poppedEntry in priorityListOfCards.queue: # From highest priority card to lowest
            card = poppedEntry[2]
            lowestPile = 8 
            
            for color, amt in card.price.items(): # Iterate through the cost of the card 
                if bankGemsCopy[color] != 0: # Skip piles we are out of
                    if playerGemsCopy[color] < amt - playerCardsCopy[color]: # If we need this color. amtt is the cost of this color
                        if bankGemsCopy[color] < lowestPile: # This is the rarest coin that we need
                            lowestPile = bankGemsCopy[color]
                            colorWeWant = color
                            
            
                         
            if colorWeWant != 0: # If we actually picked a coin after the previous block
                bestCoins[index] = colorWeWant #Its official, we are picking that color
                playerGemsCopy[colorWeWant] += 1 #We add this coin to our gems pile copy from now on
                bankGemsCopy[colorWeWant] -= 1 #So we subtract it from our bank copy

                """
                I just noticed this part could throw off our calculations.
                If we end up taking a coin intended for a lower priority card, then if we can BUY that lower priority card
                This algorithm will assume we're buying it.
                We can change this later if we need to.
                """
                canWeAffordCard = True #We check to see if we can buy this desired card in this block of code
                for color, amt in card.price.items():
                    if playerGemsCopy[color] < amt - playerCardsCopy[color]: 
                        canWeAffordCard = False
                        #We cant buy it and will be skipping the next block

                if canWeAffordCard == True: #If we can buy the card we took a coin for
                    for color, amt in card.price.items(): 
                        playerGemsCopy[color] =- (amt - playerCardsCopy[color]) #We anticipate we will buy that card and take away chips from our copy
                    playerCardsCopy[card.gem] += 1 # Then we add the fake card to our copy of card gems
                
                break
        
        """After we have looked through the highest priority card
        Ask: Can we afford this card
        If so subtract the gems it would take from the playerGemsCopy
        If not, don't"""
    
    #This converts the plaintext gem name into the script character associated with that gem
    bestCoins = list(filter(lambda x:x != "color", bestCoins))
    for i in range(len(bestCoins)):
        temp = GEM_TO_SCRIPT_MAP[bestCoins[i]]
        bestCoins[i] = temp
    
    return(bestCoins)

class Agent:
    """
    An agent must define a get_action method
    as an option: the agent should have a way to create a prioritized list of cards
    given a list of cards
    """

    def get_action(self, game_state):
        """
        Given a gamestate, must return an action which is Action:take or purchase
        """
        pass

    def sort_cards(self, cards):
        """
        An agent should have a unique way of prioritizing cards 
        (i.e. what does it think is more important)
        """
        pass

class NobleAgent(Agent): 
    """
    our agent will do all of the above while also trying to get nobles

    Based off game state, assign a value to the affordable cards? 
    """
    is_ai = True
    noble_goal = None
    priority_cards = PriorityQueue() #read the orange bellow please
    """This priority Queue really sucks
    Its a tuple with 3 places
    First place is the adjusted cost of the card
    Second is a counter to break ties
    Third is the actual card"""

    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move] # I think the player this noble agent represents should  be at the top
        if (self.noble_goal is None): # if no goal is set, assign one, otherwise pursue the same goal
            self.noble_goal = bestNoble(game_state, player)
        #Resort the priority Queue, if 0 is 
        self.sort_cards(game_state.cards, game_state)
        # try to purchase any priority cards
        for entry in self.priority_cards.queue: #Iterate through all of our priority cards
            cardWeWant = entry[2] #This is the current card we are checking

            """This code shamelessly copied from basicagent"""
            # First, look if it can afford any card
            for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
                for card_index, card in enumerate(cards):    # looking at each card in this level
                    canAfford = True
                    for color, amt in card.price.items():    # looking at the card's cost per gem
                        agent_amt = 0
                        agent_amt += player.num_color_card(color) # add discount
                        agent_amt += player.gems.gems[color]      # actual # chips of this color
                        if agent_amt < amt:
                            canAfford = False
                    if canAfford and (cardWeWant is card): # Buy it
                        return Action(Action.purchase, None, (level, card_index))


        # otherwise pick-chip
        return Action(Action.take, bestThreeCoins(game_state, player, self.priority_cards), None) #You have to return every action as an action type lame


    def sort_cards(self, cards, game_state): 
        player = game_state.players[game_state.player_to_move]
        preferred_cards = retrieve_cards_required_for_noble(cards, self.noble_goal)
        if len(preferred_cards) == 0: #If no card will help us get a noble
            self.priority_cards = sort_cards_by_point_value(cards, game_state)
        elif game_state.rules.max_player_gems < player.gems.total_items_amt():
            self.priority_cards = sort_cards_by_point_value(cards, game_state)
        else: #If we do have a path to a noble
            while self.priority_cards.empty() != True:
                self.priority_cards.get()

            counter = 0
            while(len(preferred_cards) > 0):
                cheapest_card = preferred_cards.pop(0) 
                adjustedCardCost = 0
                counter += 1
                for color, amt in cheapest_card.price.items(): # Iterate through the cost of the card
                    #color is the color at this layer, amount is the required cost at  this layer
                    adjustedCardCost += max(0, (amt - player.cards.gems[color])) #Don't want to assign negative value if we have more discount than the cost
                self.priority_cards.put((adjustedCardCost, counter, cheapest_card))

    
    """
    Priority 0 is the cheapest card that our noble wants if we can afford it
    Priority 1 is the more expensive cards that our noble wants that we cant afford. Ordered by their discounted cost from lowest to highest
    Priority 2 is the cards we could afford that provide a color necessary to buy the cheapest priority 1 card
    ALTHOUGH
    We could change it so Priority 2 counts up all of the missing chips we need to buy EVERY priority 1 card, and orders the priority 2 cards
    By the discount they provide by purchasing that card.
    So if we there are 

    
    """

class AdversarialAgent(Agent): 
    """can remove all of this if you had a different strategy in mind! This is based off Lilly's whiteboard"""
    #Note for after dinner: Going to tune this agent so it prioritizes cards the opponent can't buy yet, but they are close
    #Step 1: Buy cards the opponent can buy, if you cant
    #Step 2: Buy Carsd the opponent can almost buy, if you cant
    #Step 3: Take the coins the opponent needs to buy those step 2 cards,
    #Step 4: If you cant block a buy, just buy a card thats worth points
    is_ai = True 

    def get_action(self, game_state):
        # what I tried here was basically having the agent check if it can buy a card that's 
        # affordable to the opponent and to then buy it if it can

        # player variables
        player = game_state.players[game_state.player_to_move]

        # opponent variables 
        range_players = list(range(len(game_state.players))) # I want a list of indices for players
        opponent_index = None
        for i in range_players:
            if i != game_state.player_to_move: # compare index to THIS agent index
                opponent_index = i             # if not equal, this is probably the opponent index
        opponent = game_state.players[opponent_index]
        affordable_cards_opp = [] # what cards can opp. buy?
        # We want to look at our opponent's state

        # look at opponents's current cards/chips and determine what they can buy
        for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
            for card_index, card in enumerate(cards):    # looking at each card in this level
                #print(str(card))
                canAfford = True
                cost = 0 # this is the total cost across all gem types for this card
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += opponent.num_color_card(color) # add discount
                    agent_amt += opponent.gems.gems[color]      # actual # chips of this color
                    cost += amt - opponent.num_color_card(color)
                    if agent_amt < amt: # can we buy?
                        canAfford = False
                if canAfford: # Here, we make the change. We want to keep track of all cards opp. can afford
                    affordable_cards_opp.append([level, card_index, card, cost])
        
        # based off the board cards they can buy, see if we can buy any. Then buy that...
        cards_from_opp_player_can_buy = [] # affordable_cards_opp is a tuple list of [level, card_index, card, cost]
        if (len(affordable_cards_opp) > 0):
            for i, tuple in enumerate(affordable_cards_opp): # looking at each card in this level
                level = tuple[0] # getting card info here
                card_index = tuple[1]
                card = tuple[2]
                cost = tuple[3]
                canAfford = True
                player_cost = 0 # this is the total cost across all gem types for this card
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += player.num_color_card(color) # add discount
                    agent_amt += player.gems.gems[color]      # actual # chips of this color
                    player_cost += amt - player.num_color_card(color)
                    if agent_amt < amt: # can we buy?
                        canAfford = False
                if canAfford: # Here, we make the change. We want to keep track of all cards opp. can afford
                    cards_from_opp_player_can_buy.append([level, card_index, card, player_cost])
        
        if (len(cards_from_opp_player_can_buy) > 0):
            # buy the first card you can? wait actually, I think I need to reverse that list here
            # so if all is ordered... I think first card element should be card with highest tier?
            print("opp_cards: " + str(cards_from_opp_player_can_buy))
            cards_from_opp_player_can_buy = list(reversed(cards_from_opp_player_can_buy))
            print("After reverse: " + str(cards_from_opp_player_can_buy))
            card_level = cards_from_opp_player_can_buy[0][0]
            card_index = cards_from_opp_player_can_buy[0][1]
            card_tuple_to_buy = (card_level, card_index)
            return Action(Action.purchase, None, card_tuple_to_buy) # BUY

        # if not, then default to either NobleAgent or CheapAgent strategy
        # chip_actions = rand_choose_cards(game_state) # If no cards are affordable, choose random chips

        # Uhhhh what I think I COULD do here is use chip_colors_given_cards() to return a set of chips
        # GIVEN the set of affordable cards from the opponent
        opps_preferred_cards = [tuple[2] for tuple in affordable_cards_opp] # [level, card_index, card, cost]
        chip_actions_sabotage_opp = chip_colors_given_cards(opps_preferred_cards, game_state) # wait lemme think abt it
        # maybe do the same to find best chips for THIS agent, evaluate between the two sets, and return the one
        # that's determined (somehow) to be more valuable? uhhhhh
 
        return Action(Action.take, chip_actions_sabotage_opp, None)


        

class BasicAgent(Agent): 
    """
    Plays legally... chooses random chips or traverses all cards and randomly buy a card it can afford.
    """
    is_ai = True
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]

        # First, look if it can afford any card
        for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
            for card_index, card in enumerate(cards):    # looking at each card in this level
                canAfford = True
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += player.num_color_card(color) # add discount
                    agent_amt += player.gems.gems[color]      # actual # chips of this color
                    if agent_amt < amt:
                        canAfford = False
                if canAfford: # Buy it
                    return Action(Action.purchase, None, (level, card_index))

        chip_actions = rand_choose_cards(game_state) # If no cards are affordable, choose random chips
        return Action(Action.take, chip_actions, None)

def rand_choose_cards(game_state): # randomly chooses chips based off what's left on the board
    num_chips_to_choose = game_state.rules.max_gems_take
    game_state_chips = game_state.gems.gems.copy() # make a dict to not mutate game_state yet, Action will do this for us
    board_num_chips = 0
    board_num_chips = sum([game_state_chips[i] for i in game_state_chips.keys()]) # add num. of chips per color
    chips_taken = 0   
    chip_actions = [] # the gems to take
    while (chips_taken < num_chips_to_choose) and (board_num_chips != 0): # choose one rand. color at a time
        color_chosen_name = sample(game_state_chips.keys(), 1)[0]         # color randomly chosen
        if game_state_chips[color_chosen_name] != 0:
            chip_actions.append(GEM_TO_SCRIPT_MAP[color_chosen_name])     # add to action list
            chips_taken += 1
            board_num_chips -= 1
            game_state_chips[color_chosen_name] = game_state_chips[color_chosen_name] - 1
    return chip_actions

class CheapAgent(Agent):  
    """
    Implement an agent that purchases the cheapest card it can, then prioritizes cards of that color
    """
    is_ai = True
    color_preference = ""
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]

        # Search for cards you can afford, but have the cheapest chip cost
        affordable_cards = []
        for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
            for card_index, card in enumerate(cards):    # looking at each card in this level
                canAfford = True
                cost = 0 # this is the total cost across all gem types for this card
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += player.num_color_card(color) # add discount
                    agent_amt += player.gems.gems[color]      # actual # chips of this color
                    cost += amt - player.num_color_card(color)
                    if agent_amt < amt: # can we buy?
                        canAfford = False
                if canAfford: # Here, we make the change. We want to keep track of all cards we can afford
                    affordable_cards.append([level, card_index, card, cost]) # we have tuples!
                
        is_empty = (len(affordable_cards) == 0)
        if (not is_empty): # We now have a list of cards we can afford. Let's choose the cheapest one!
            if (self.color_preference == ""): # we have no color preference set yet
                cost_cards = [i[3] for i in affordable_cards]
                min_cost = min(cost_cards)     # identify card in list with min cost
                for tuple in affordable_cards: # tuple: [level, card_index, card, cost]
                    if tuple[3] == min_cost:   # we found our cheapest card
                        level = tuple[0]
                        card_index = tuple[1]
                        self.color_preference = tuple[2].gem
                        return Action(Action.purchase, None, (level, card_index))
            else: # filter affordable cards by color preference, basically the same as the if loop
                cost_cards = [i[3] for i in affordable_cards if i[2].gem == self.color_preference]
                if (len(cost_cards) > 0): # make sure we have cards to choose from
                    min_cost = min(cost_cards)
                    for tuple in affordable_cards: # identify card in list with min cost
                        if tuple[3] == min_cost: # we found our cheapest card
                            level = tuple[0]
                            card_index = tuple[1]
                            return Action(Action.purchase, None, (level, card_index))

        # Given the set of all cards that are the preferred color, choose chips
        cards_sets = [cards for level, cards in reversed(list(enumerate(game_state.cards)))]
        cards = []
        for set in cards_sets: # get all cards in a list
            for card_index, card in enumerate(set):
                if card.gem == self.color_preference: # filter by if they're the preference color
                    cards.append(card)
        chip_actions = chip_colors_given_cards(cards, game_state) # If no cards are affordable, choose random chips.
        return Action(Action.take, chip_actions, None)

def chip_colors_given_cards(preferred_cards, game_state):
    """ Designed for CheapAgent, this tries to grab the most coins it can that are of the color
    costs in the preferred set of cards. If the game state does not have any amount of these colors,
    it simply grabs random chips. """ # be back in a min!
    # Make list of colors in set 
    priority_colors = [] # the set of colors in card set given

    for card in preferred_cards:                 # looking at prioritized cards
        card_price_stack = card.price.gems       # get its price stack

        for color, amt in card_price_stack.items(): # Look through what chips it costs
            if card_price_stack[color] > 0:    
                if color not in priority_colors: # if the color has not been added yet, add!
                    priority_colors.append(color)

    # Randomly choose a set of colors 
    game_state_chips = game_state.gems.gems.copy() # board chips, making copy to avoid extra mutation
    # look to see what colors are available in board
    max_chips_to_grab = game_state.rules.max_gems_take

    chips_taken = 0   
    chip_actions = [] # the gems to take
    while (chips_taken < max_chips_to_grab): # choose one rand. color at a time
        # look thru priority_colors and try to grab from those colors
        if len(priority_colors) != 0:
            color_chosen = sample(priority_colors, 1)[0]
            if game_state_chips[color_chosen] != 0:  # if board has this priority color
                chip_actions.append(GEM_TO_SCRIPT_MAP[color_chosen])     # add to action list
                chips_taken += 1
                game_state_chips[color_chosen] = game_state_chips[color_chosen] - 1
            else: # this color is not available anymore, so get rid from priority
                priority_colors.remove(color_chosen) 
        else: # if no more priority colors available, then just choose from colors in board randomly
            colors_in_board = [color for color in game_state_chips.keys() if game_state_chips[color] > 0]
            color_chosen_name = sample(colors_in_board, 1)[0] # color randomly chosen
            if game_state_chips[color_chosen_name] != 0:
                chip_actions.append(GEM_TO_SCRIPT_MAP[color_chosen_name]) # add to action list
                chips_taken += 1
                game_state_chips[color_chosen_name] = game_state_chips[color_chosen_name] - 1
    return chip_actions



class AdversarialAgent2(Agent): 
    """can remove all of this if you had a different strategy in mind! This is based off Lilly's whiteboard"""
    #Note for after dinner: Going to tune this agent so it prioritizes cards the opponent can't buy yet, but they are close
    #Step 1: Buy cards the opponent can buy, if you cant
    #Step 2: Buy Carsd the opponent can almost buy, if you cant
    #Step 3: Take the coins the opponent needs to buy those step 2 cards,
    #Step 4: If you cant block a buy, just buy a card thats worth points
    is_ai = True 

    def get_action(self, game_state):
        # what I tried here was basically having the agent check if it can buy a card that's 
        # affordable to the opponent and to then buy it if it can

        # player variables
        player = game_state.players[game_state.player_to_move]

        # opponent variables 
        range_players = list(range(len(game_state.players))) # I want a list of indices for players
        opponent_index = None
        for i in range_players:
            if i != game_state.player_to_move: # compare index to THIS agent index
                opponent_index = i             # if not equal, this is probably the opponent index
        opponent = game_state.players[opponent_index]
        affordable_cards_opp = [] # what cards can opp. buy?
        # We want to look at our opponent's state

        # look at opponents's current cards/chips and determine what they can buy
        for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
            for card_index, card in enumerate(cards):    # looking at each card in this level
                #print(str(card))
                canAfford = True
                cost = 0 # this is the total cost across all gem types for this card
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += opponent.num_color_card(color) # add discount
                    agent_amt += opponent.gems.gems[color]      # actual # chips of this color
                    cost += amt - opponent.num_color_card(color)
                    if agent_amt < amt: # can we buy?
                        canAfford = False
                if canAfford: # Here, we make the change. We want to keep track of all cards opp. can afford
                    affordable_cards_opp.append([level, card_index, card, cost])
        
        # based off the board cards they can buy, see if we can buy any. Then buy that...
        cards_from_opp_player_can_buy = [] # affordable_cards_opp is a tuple list of [level, card_index, card, cost]
        if (len(affordable_cards_opp) > 0):
            for i, tuple in enumerate(affordable_cards_opp): # looking at each card in this level
                level = tuple[0] # getting card info here
                card_index = tuple[1] 
                card = tuple[2]
                cost = tuple[3]
                canAfford = True
                player_cost = 0 # this is the total cost across all gem types for this card
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += player.num_color_card(color) # add discount
                    agent_amt += player.gems.gems[color]      # actual # chips of this color
                    player_cost += amt - player.num_color_card(color)
                    if agent_amt < amt: # can we buy?
                        canAfford = False
                if canAfford: # Here, we make the change. We want to keep track of all cards opp. can afford
                    cards_from_opp_player_can_buy.append([level, card_index, card, player_cost])
        
        if (len(cards_from_opp_player_can_buy) > 0):
            # buy the first card you can? wait actually, I think I need to reverse that list here
            # so if all is ordered... I think first card element should be card with highest tier?

            cards_from_opp_player_can_buy = list(reversed(cards_from_opp_player_can_buy))

            card_level = cards_from_opp_player_can_buy[0][0]
            card_index = cards_from_opp_player_can_buy[0][1]
            card_tuple_to_buy = (card_level, card_index)
            return Action(Action.purchase, None, card_tuple_to_buy) # BUY


        """Everything above is to snipe the most expensive card the opponent can buy. Beneath here is going to be the goal of taking coins that stop opponent from
        getting cards they can almost afford"""
        priority_cards = sort_cards_by_cheapness(game_state.cards, game_state, opponent)
        
        for entry in priority_cards.queue: #Iterate through all of our priority cards
            cardWeWant = entry[2] #This is the current card we are checking

            """This code shamelessly copied from basicagent"""
            # First, look if it can afford any card
            for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
                for card_index, card in enumerate(cards):    # looking at each card in this level
                    canAfford = True
                    for color, amt in card.price.items():    # looking at the card's cost per gem
                        agent_amt = 0
                        agent_amt += player.num_color_card(color) # add discount
                        agent_amt += player.gems.gems[color]      # actual # chips of this color
                        if agent_amt < amt:
                            canAfford = False
                    if canAfford and (cardWeWant is card): # Buy it
                        return Action(Action.purchase, None, (level, card_index))


        # otherwise pick-chip
        return Action(Action.take, bestThreeCoins(game_state, player, priority_cards), None) #You have to return every action as an action type lame




        # if not, then default to either NobleAgent or CheapAgent strategy
        # chip_actions = rand_choose_cards(game_state) # If no cards are affordable, choose random chips

        # Uhhhh what I think I COULD do here is use chip_colors_given_cards() to return a set of chips
        # GIVEN the set of affordable cards from the opponent
        opps_preferred_cards = [tuple[2] for tuple in affordable_cards_opp] # [level, card_index, card, cost]
        chip_actions_sabotage_opp = chip_colors_given_cards(opps_preferred_cards, game_state) # wait lemme think abt it
        # maybe do the same to find best chips for THIS agent, evaluate between the two sets, and return the one
        # that's determined (somehow) to be more valuable? uhhhhh
 
        return Action(Action.take, chip_actions_sabotage_opp, None)

def retrieve_all_cards(cards):
    allCards= list()
    for card in reduce(lambda x, y : x + y, cards):
        allCards.append(card)
    return allCards

def sort_cards_by_cheapness(cards, game_state, player): 
        priority_card_queue = PriorityQueue()
        preferred_cards = retrieve_all_cards(cards)

        counter = 0
        while(len(preferred_cards) > 0):
            cheapest_card = preferred_cards.pop(0) 
            adjustedCardCost = 0
            canBuy = True
            counter += 1
            for color, amt in cheapest_card.price.items(): # Iterate through the cost of the card
                #color is the color at this layer, amount is the required cost at  this layer
                adjustedCardCost += max(0, (amt - player.cards.gems[color])) #Don't want to assign negative value if we have more discount than the cost

                if adjustedCardCost > player.gems.gems[color]: #Here we make some adjustments. Its not worth prioritizing a card that the enemy is going to buy next turn, so we ignore those
                    canBuy = False
        
            if canBuy == False:#If the enemy player cant buy the card it goes into the list. Then we will try and buy it/take coins for it.
                priority_card_queue.put((adjustedCardCost, counter, cheapest_card))


        if len(preferred_cards) == 0: #If we can't really cut the player off 
            priority_card_queue = sort_cards_by_point_value(cards, game_state)

        return priority_card_queue

if __name__ == '__main__':
    print("Agent Selections:")
    print("0 - Player Controlled, 1 - BasicAgent, 2 - CheapAgent, 3 - NobleAgent, 4 - AdversarialAgent, 5 - S.O.B.Agent2")
    agent_1 = int(input("Please enter an agent identifying number: 0-5:"))
    agent_2 = int(input("Please enter another agent identifying number: 0-5:"))
    if (agent_1 >= 0 and agent_1 <= 5) and (agent_2 >= 0 and agent_2 <= 5):
        play_game(agent_1, agent_2)
    else:
        sys.exit('Invalid agent number input.')