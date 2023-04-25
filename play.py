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

        # Game state cards/chips/nobles
        game_state_chips = game_state.gems.gems.copy()

        # First, look if it can afford any card
        for level, cards in enumerate(game_state.cards): # cards sets are ordered by their level
            print("Level: " + str(level)) 
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

        # If no cards are affordable, choose random chips
        num_chips_to_choose = game_state.rules.max_gems_take
        board_num_chips = 0
        for i in game_state_chips.keys(): # add num. of chips per color
            board_num_chips += game_state_chips[i]
        gem_types = game_state_chips.keys() 
        chips_taken = 0   
        chip_actions = [] # the gems to take
        while (chips_taken < num_chips_to_choose) and (board_num_chips != 0): # choose one rand. color at a time
            color_chosen_name = sample(gem_types, 1)[0]              # color randomly chosen
            color_chosen_script = GEM_TO_SCRIPT_MAP[color_chosen_name]
            print("color_chosen: " + str(color_chosen_name))
            if game_state_chips[color_chosen_name] != 0:
                chip_actions.append(color_chosen_script) 
                chips_taken += 1
                board_num_chips -= 1
                game_state_chips[color_chosen_name] = game_state_chips[color_chosen_name] -1
            print("chip_actions: " + str(chip_actions))
        return Action(Action.take, chip_actions, None)

class CheapAgent:  
    """
    Implement an agent that purchases the cheapest card it can, then prioritizes cards of that color
    """
    is_ai = True
    color_preference = ""
    def get_action(self, game_state):
        player = game_state.players[game_state.player_to_move]

        # Game state cards/chips/nobles
        game_state_chips = game_state.gems.gems.copy()

        # Search for cards you can afford, but have the cheapest chip cost
        affordable_cards = []
        for level, cards in enumerate(game_state.cards): # cards sets are ordered by their level
            for card_index, card in enumerate(cards):    # looking at each card in this level
                canAfford = True
                cost = 0 # this is the total cost across all gem types for this card
                for color, amt in card.price.items():    # looking at the card's cost per gem
                    agent_amt = 0
                    agent_amt += player.num_color_card(color) # add discount
                    agent_amt += player.gems.gems[color]      # actual # chips of this color
                    cost += amt
                    if agent_amt < amt:
                        canAfford = False
                if canAfford: 
                    # Here, we make the change. We want to keep track of all cards we can afford,
                    # then take any one that has the least chip amount
                    print("We can afford a card, so we should terminate somewhere here")
                    affordable_cards.append([level, card_index, card, cost]) # we have tuples!
                    # return Action(Action.purchase, None, (level, card_index))
                
        is_empty = (len(affordable_cards) == 0)
        if (not is_empty): # We now have a list of cards we can afford. Let's choose the cheapest one!
            if (self.color_preference == ""): # we have no color preference set yet
                cost_cards = [i[3] for i in affordable_cards]
                min_cost = min(cost_cards)
                # identify card in list with min cost
                for tuple in affordable_cards: # tuple: [level, card_index, card, cost]
                    if tuple[3] == min_cost: # we found our cheapest card
                        level = tuple[0]
                        card_index = tuple[1]
                        self.color_preference = card.gem # set new color preference
                        return Action(Action.purchase, None, (level, card_index))
            else: # filter affordable cards by color preference, basically the same as the if loop
                cost_cards = [i for i in affordable_cards if i[2].gem == self.color_preference]
                min_cost = min(cost_cards)
                # identify card in list with min cost
                for tuple in affordable_cards:
                    if tuple[3] == min_cost: # we found our cheapest card
                        level = tuple[0]
                        card_index = tuple[1]
                        return Action(Action.purchase, None, (level, card_index))

        # If no cards are affordable, choose random chips. Should this change to prioritize certain cards?
        num_chips_to_choose = game_state.rules.max_gems_take
        board_num_chips = 0
        for i in game_state_chips.keys(): # add num. of chips per color
            board_num_chips += game_state_chips[i]
        gem_types = game_state_chips.keys() 
        chips_taken = 0   
        chip_actions = [] # the gems to take
        while (chips_taken < num_chips_to_choose) and (board_num_chips != 0): # choose one rand. color at a time
            color_chosen_name = sample(gem_types, 1)[0] # color randomly chosen
            color_chosen_script = GEM_TO_SCRIPT_MAP[color_chosen_name]
            if game_state_chips[color_chosen_name] != 0:
                chip_actions.append(color_chosen_script) 
                chips_taken += 1
                board_num_chips -= 1
                game_state_chips[color_chosen_name] = game_state_chips[color_chosen_name] -1
        return Action(Action.take, chip_actions, None)

class NobleAgent: 
    """
    our agent will do all of the above while also trying to get nobles
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
    player_names = ['Human', 'AI Agent']
    players = [HumanPlayer(), BasicAgent()]
    rules = SplendorGameRules()
    game = SplendorGameState(player_names, rules)

    while not game.check_win():
        for n, player in enumerate(players):
            print(game) # this STAYS
            while True: # check for invalid action inputs
                action = player.get_action(game)
                try:
                    game.action(action) # here?
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
