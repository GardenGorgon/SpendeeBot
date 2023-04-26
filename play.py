from random import randint, sample
from game import SplendorGameState, SplendorGameRules, Action

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
    
class BasicAgent: 
    """
    Plays legally... maybe it should just make random moves? like choose random chips, 
    then traverse all cards and randomly buy a card it can afford
    """
    is_ai = True
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]

        # First, look if it can afford any card
        for level, cards in reversed(list(enumerate(game_state.cards))): # cards sets are ordered by their level
            # print("level: " + str(level))
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

class CheapAgent:  
    """
    Implement an agent that purchases the cheapest card it can, then prioritizes cards of that color
    """
    is_ai = True
    color_preference = ""
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]
        # print("AI color preference: " + self.color_preference)

        # Search for cards you can afford, but have the cheapest chip cost
        affordable_cards = []
        init_level = 2
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
                    # print("We can afford a card, but is it the preferred color?")
                    affordable_cards.append([level, card_index, card, cost]) # we have tuples!
                
        # print("affordable_cards: " + str(affordable_cards))
        is_empty = (len(affordable_cards) == 0)
        if (not is_empty): # We now have a list of cards we can afford. Let's choose the cheapest one!
            if (self.color_preference == ""): # we have no color preference set yet
                cost_cards = [i[3] for i in affordable_cards]
                # print("cost_cards: " + str(cost_cards))
                min_cost = min(cost_cards)     # identify card in list with min cost
                # print("min_cost: " + str(min_cost))
                for tuple in affordable_cards: # tuple: [level, card_index, card, cost]
                    if tuple[3] == min_cost:   # we found our cheapest card
                        # print("found min. card")
                        level = tuple[0]
                        card_index = tuple[1]
                        # print("tuple[2].gem: " + str(tuple[2].gem))
                        self.color_preference = tuple[2].gem
                        return Action(Action.purchase, None, (level, card_index))
            else: # filter affordable cards by color preference, basically the same as the if loop
                cost_cards = [i[3] for i in affordable_cards if i[2].gem == self.color_preference]
                if (len(cost_cards) > 0): # make sure we have cards to choose from
                    # print("cost_cards: " + str(cost_cards))
                    min_cost = min(cost_cards)
                    # print("min_cost: " + str(min_cost))
                    for tuple in affordable_cards: # identify card in list with min cost
                        if tuple[3] == min_cost: # we found our cheapest card
                            level = tuple[0]
                            card_index = tuple[1]
                            return Action(Action.purchase, None, (level, card_index))

        # TODO: Should this change to prioritize certain cards? 
        chip_actions = rand_choose_cards(game_state) # If no cards are affordable, choose random chips.
        return Action(Action.take, chip_actions, None)

def chip_colors_given_cards(cards, game_state):
    """ Steph: This outputs a set of gem names that are required by the given set of cards. 
     Designed for CheapAgent. A TODO for later..."""
    # Make list of colors in set 
    # Randomly choose a set of colors 
    # if there are no chips of that color, remove it 
    # if there are no chips of the rest of the colors, choose from the colors left

class NobleAgent: 
    """
    our agent will do all of the above while also trying to get nobles

    Based off game state, assign a value to the affordable cards? 
    """
    is_ai = True
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]


class AverserialAgent:
    """"""
    is_ai = True
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]

def play_game():
    player_names = ['AI Agent 1', 'AI Agent 2']
    players = [CheapAgent(), CheapAgent()]
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
                print(player_names[n] + ' move: ' + str(action))

    print('best player:', game.best_player())


if __name__ == '__main__':
    play_game()

# given a list of cards (from the shop) determines which card has the best cost to point ratio
def cost_point_ratio(cards):
    pass
    best_ratio = 0 # Me when I'm on twitter
    card_with_best_ratio = None
    for shop_card in cards:
        cost_to_point_ratio = float(shop_card.total_items_amt()) / float(shop_card.points)
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
        nobles_values_dict[n] = {x:y for x,y in n.price if y!=0}
        # subtract the cards that the player already has
        for key in n.price.keys():
            n.price[key]-player.cards[key]
    # for all cards in the game state shop
    for card in game_state.cards:
        # for all nobles in the game
        for noble_val in nobles_values_dict:
            # if the gem of the card is required for that noble
            if [card.gem] in nobles_values_dict[noble_val].keys():
                # subtract value
                nobles_values_dict[noble_val][card.gem]-=1
    min_cost = int('inf')
    # for all the nobles
    for noble_val in nobles_values_dict:
        # sum together a value of which represents accessibility:
        # accessible factor = original_cost - already owned cards - relevant cards in shop
        accessibility_score = sum(nobles_values_dict[noble_val])
        # keep track of the lowest value and the noble that has that value
        if accessibility_score < min_cost:
            min_cost = accessibility_score
            best_noble = noble_val
    
    return best_noble
    
# given a noble, creates a list of cards that should be bought
def retrieve_cards_required_for_noble(cards,noble):
        # cards = list of cards in the shop/game state
        cards_of_required_color = list()
        for card in cards:
            if noble.price[card.gem]!=0:
                cards_of_required_color.add(card)
        return cards_of_required_color
        
        
        


def bestThreeCoins(game_state, player, priorityListOfCards):
    """ Determines how to choose the best coins... by I'm not sure how ... """
    #Using the priority listOfCards we pick out which 3 coins are most important to purchasing those cards
    #If we cant take the coins relevant to our highest priority card, we pick coins relevant to the second/third/fourth priority card
    bestCoins = ["color", "color", "color"]
    playerGemsCopy = player.gems.copy() # We need a copy because we don't want to alter the real thing
    playerCardsCopy = player.cards.copy()
    for coin in bestCoins:# For each coin we are taking
        colorWeWant = 0 # We are trying to fill in the color of the coin we want to take
        canWeAffordCard = True
        for card in priorityListOfCards: # From highest priority card to lowest
            lowestPile = 7 
            for color, amt in card.price.items(): # Iterate through the cost of the card
            
                if game_state.gems[color] != 0: # Skip piles we are out of
                    if playerGemsCopy[color] < card.price.items - playerCardsCopy[color]: # If we need that color
                        if game_state.gems[color] < lowestPile: # This is the rarest coin that we need
                            lowestPile = game_state.gems[color]
                            colorWeWant = color
                            
            
                         
            if colorWeWant != 0: # If we actually picked a coin
                playerGemsCopy[colorWeWant] += 1 #We need to add the coin we will have for the next iterations
                for color, amt in card.price.items():#We check to see if we would can buy this card
                    if playerGemsCopy[color] < card.price.items - playerCardsCopy[color]:
                        canWeAffordCard = False   
                break
    
        if canWeAffordCard == True:
            for color, amt in card.price.items(): 
                playerGemsCopy[color] =- card.price.items - playerCardsCopy[color] 
            playerCardsCopy[card.gem] += 1
        """After we have looked through the highest priority card
        Ask: Can we afford this card
        If so subtract the gems it would take from the playerGemsCopy
        If not, don't"""
    
    #This converts the plaintext gem name into the script character associated with that gem
    for i in range(len(bestCoins)):
        temp = GEM_TO_SCRIPT_MAP[bestCoins[i]]
        bestCoins[i] = temp
    return(bestCoins)