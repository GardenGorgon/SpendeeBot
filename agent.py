import sys

class Agent:
    """
    An agent must define a get_action method
    as an option: the agent should have a way to create a prioritized list of cards
    given a list of cards
    """

    def get_action(self,game_state):
        """
        Given a gamestate, must return an action which is Action:take or purchase
        """
        pass

    def sort_cards(self,cards):
        """
        An agent should have a unique way of prioritizing cards 
        (i.e. what does it think is more important)
        """
        pass
