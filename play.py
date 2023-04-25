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
        game_state_chips = game_state.gems.gems

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
            color_chosen_name = sample(gem_types, 1)[0] # color randomly chosen
            color_chosen_script = GEM_TO_SCRIPT_MAP[color_chosen_name]
            print("color_chosen: " + str(color_chosen_name))
            if game_state_chips[color_chosen_name] != 0:
                amt_chosen = 1
                print("amt_chosen: " + str(amt_chosen))
                chip_actions.append(color_chosen_script) 
                chips_taken += 1
                board_num_chips -= 1
            print("chip_actions: " + str(chip_actions))
        return Action(Action.take, chip_actions, None)

class CheapAgent:  
    """
    Implement an agent that purchases the cheapest card it can, then prioritizes cards of that color
    """
    is_ai = True
    def get_action(self, game_state):
        # amt_chosen = randint(1, num_chips_to_choose) # amount randomly chosen
            # num_chips_left_to_take = num_chips_to_choose - chips_taken
            # for i in range(num_chips_left_to_take): # add gems to chip_actions
            #     chip_actions.append(color_chosen_script) 
            #     chips_taken += 1
            #     board_num_chips -= 1
        player = game_state.players[game_state.player_to_move]

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

"""class CultivatorPlayer: # FOR REFERENCE
    is_ai = True
    def get_action(self, game_state: SplendorGameState):
        player = game_state.players[game_state.player_to_move]
        gold = player.gems.get(GOLD_GEM)

        action_scores = []
        
        for level, cards in enumerate(game_state.cards):
            for pos, card in enumerate(cards):
                shortage = player.gems.shortage(card.price)
                gold_shortage = shortage.count() - gold
                if gold_shortage <= 0: # affordable card
                    action = Action(Action.purchase, None, (level, pos))
                    score = card.points
                    action_scores.append((score, action))
                else: 
                    gems = list(shortage.gems.keys())

                    if len(gems) > 3:
                        gems = gems[:3]
                    if len(gems) == 1 and shortage.get(gems[0]) > 1:
                        gems = [gems[0], gems[0]]
                    action = Action(Action.take, gems, None)
                    score = -gold_shortage
                    if card.points > 0 and gold_shortage < 3:
                        score += card.points + 1
                    action_scores.append((score, action))

        _, best_action = sorted(action_scores, reverse=True, key = lambda x: x[0])[0]
        return best_action"""

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
