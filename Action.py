ACTIONS = ['grabChips', 'buyCard', 'buyNoble', 'help']

class Action:
    take = ACTIONS[0] # take gems
    reserve = ACTIONS[1] # reserve card
    purchase = ACTIONS[2] # purchase table card
    purchase_hand = ACTIONS[3] # purchase hand card

    def __init__(self, action_type, gems, pos):
        self.type = action_type
        self.gems = gems
        self.pos = pos

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

        if action_type == Action.take: 
            gems = [g for g in action_str[1:]]
        elif action_type == Action.reserve: 
            pos = Action.scan_pos(action_str) # (level, pos)
        elif action_type == Action.purchase: 
            pos = Action.scan_pos(action_str) 
        elif action_type == Action.purchase_hand: 
            assert len(action_str) == 2
            pos = (int(action_str[1]) - 1,) # single int -- position of hand card
        else:
            raise AttributeError('Invalid action type {} (in action {})'.format(action_type, action_str))
        
        return action_type, gems, pos

    @staticmethod
    def scan_pos(action_str):
        assert len(action_str) == 3
        level = int(action_str[1]) - 1
        pos = int(action_str[2]) - 1
        return level, pos
    
class SplendorPlayerState:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.gems = []
        self.hand_cards = []
        self.points = 0
        self.gem_count = 0

    def __str__(self):
        s = self.name + '|' + str(self.points) + '\n'
        s += 'cards:' + str(self.cards) + '\n'
        s += 'gems:' + str(self.gems) + '\n'
        s += 'hand:'
        for card in self.hand_cards:
            s += str(card)
        s += '\n'
        return s

    def purchase_card(self, card):
        '''Does card purchase. Returns false if player can\'t afford card'''

        shortage = self.gems.shortage(card.price)
        gold = self.gems.get(GOLD_GEM) # gold available 
        gold_to_pay = shortage.count()
        if gold < gold_to_pay:
            return False

        # if player can afford card, do actual payment
        if gold_to_pay > 0:
            self.gems.add(GOLD_GEM, -gold_to_pay)
        for gem, price in card.price.items():
            if gem in shortage.gems: # have to pay by gold => new gem count is zero
                self.gems[gem] = 0
            else:
                self.gems.add(gem, -price)
        self.gem_count -= card.price.count()

        self.cards.add(card.gem, 1)
        self.points += card.points
        return True

    def get_noble(self, nobles):
        '''Attempts to acquire noble card. In case of success removes taken noble from input list'''
        noble_list = []
        for n, noble in enumerate(nobles):
            can_afford = True
            for gem, price in noble.price.items():
                if self.cards.get(gem) < price:
                    can_afford = False
                    break
            if can_afford:
                noble_list.append(n)
        
        if noble_list:
            n = randint(1, len(noble_list))# choose random if more than one available
            noble = nobles.pop(noble_list[n])
            self.points += noble.points