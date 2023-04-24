"""
CS4100

This class represents a player for a game of Splendee. 
A player takes in a strategy (how they choose to play) and
has a number of points, set of chips, and set of cards they hold. At initialization, 
a player have 0 points and no cards/chips.
"""
from random import randint
from ChipStack import ChipStack
from SpendeeGameState import SpendeeGameState
from Action import Action

init_stack = {
    'blue' : ChipStack('blue', 0),
    'red'  : ChipStack('red', 0),
    'green': ChipStack('green', 0),
    'black': ChipStack('black', 0),
    'white': ChipStack('white', 0)
}

class Player():

    def __init__(self, strategy, points=0, chips=init_stack, cards=[], name="Agent", is_ai=False):
        """
        name: name of player
        strategy: an action that determines how this player will play when prompted by game state.
        points: number of points this player has
        chips: a dictionary of this players chips. ( color : ChipStack )
        cards: this player's set of cards
        is_ai: says if this player is ai or not
        """
        self.name = name
        self.strategy = strategy
        self.points = points
        self.chips = chips
        self.cards = cards
        self.is_ai = is_ai

    def __str__(self):
        s = self.name + '|' + str(self.points) + '\n'
        s += 'chips:' + str(self.chips) + '\n'
        s += 'cards:' + str(self.cards) + '\n'
        s += 'hand:'
        s += '\n'
        return s

    def next_move(self, game_state):
        # Returns the next move given the game_state
        return self.strategy(game_state)

    def add_points(self, points):
        # Adds points to this player's total points
        self.points += points

    def purchase_card(self, card):
        '''Does card purchase. Returns false if player can\'t afford card'''
        cost_dict = card.cost
        for i in cost_dict: # accessing cost dict from card, look at each gem cost
            chip_stack = self.chips[i]
            if chip_stack.amount < cost_dict[i]: # each chip is a chipstack w/ an amount and color
                return False

        # player can afford card if false hasn't been returned
        self.add_card(card) # add card to player

        # add points from card
        self.add_points(card.reward)

        # remove chips used to buy card
        for i in cost_dict: # accessing cost dict from card, look at each gem cost
            chip_stack = self.chips[i]
            chip_stack.amount = chip_stack.amount - cost_dict[i] # compute new amount of chips

        return True # success!

    def get_noble(self, nobles):
        '''Attempts to acquire noble card. In case of success removes taken noble from input list'''
        noble_list = []
        for n, noble in enumerate(nobles):
            can_afford = True
            cost_dict = noble.cost
            for i in cost_dict:
                noble_cost = cost_dict[i]
                num_color_card_player = self.num_color_cards(i) # number of cards of color i this player has
                if num_color_card_player < noble_cost:
                    can_afford = False
                    break
            if can_afford: 
                noble_list.append(n) # add to player's cards
        
        if noble_list:
            n = randint(1, len(noble_list))# choose random if more than one available
            noble = nobles.pop(noble_list[n])
            self.points += noble.points


    # //////////////////// A couple of helpers
    def num_cards(self):
        return len(self.cards)

    def num_chips(self):
        total = 0
        for color in self.chips:
            stack = self.chips[color]
            total += stack.amount
        return total

    def num_color_chip(self, color: str):
        return self.chips[color].amount # returns the number of chips of a specific color

    def num_color_cards(self, color: str):
        total_cards_of_color = 0
        for card in self.cards:
            if card.color == color:
                total_cards_of_color += 1
        return total_cards_of_color

    def num_unique_chip(self):
        # returns the number of unique chip colors
        total = 0
        for color in self.chips:
            if color.amount > 0:
                total += 1
        return total

    def add_card(self, card):
        self.cards.append(card)


class HumanPlayer:
    is_ai = False
    def get_action(self, game_state):
        player_name = game_state.players[game_state.player_to_move].name
        action_str = input(player_name + ' move: ')
        return Action.from_str(action_str)
    

class CultivatorPlayer:
    is_ai = True
    def get_action(self, game_state: SpendeeGameState):
        player = game_state.players[game_state.player_to_move]

        action_scores = []
        
        # for level, cards in enumerate(game_state.cards):
        #     for pos, card in enumerate(cards):
        #         shortage = player.gems.shortage(card.price)
        #         gold_shortage = shortage.count() - gold
        #         if gold_shortage <= 0: # affordable card
        #             action = Action(Action.purchase, None, (level, pos))
        #             score = card.points
        #             action_scores.append((score, action))
        #         else: 
        #             gems = list(shortage.gems.keys())

        #             if len(gems) > 3:
        #                 gems = gems[:3]
        #             if len(gems) == 1 and shortage.get(gems[0]) > 1:
        #                 gems = [gems[0], gems[0]]
        #             action = Action(Action.take, gems, None)
        #             score = -gold_shortage
        #             if card.points > 0 and gold_shortage < 3:
        #                 score += card.points + 1
        #             action_scores.append((score, action))

        # _, best_action = sorted(action_scores, reverse=True, key = lambda x: x[0])[0]
        # return best_action

