ACTIONS = ['grabChips', 'buyCard', 'help']

class Action:
    take = ACTIONS[0] # take gems
    purchase = ACTIONS[1] # purchase table card
    purchase = ACTIONS[2] # help

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