from tree_search import *
from pathways import Pathways
from eating_agent import EatingAgent


class CounterAgent:
    """ Creates de Counter Agent, which s a Wrapper to EatingAgent where Pac-Man
    searches for Boosts in order to turn ghosts into zombie ghosts as a tactic
    to evade them and earn more points
        
    Attr:
    advisor: provides extensive information about the current situation of the map
    targets: the targets to search paths to
    """
    def __init__(self, advisor, targets):
        self.advisor = advisor
        self.targets = targets


    def counter(self):
        """Calculates the path to all accessible targets using EatingAgent class,
        and sorts them by cost and safety which are sorted according to the
        following criteria:
        1 - cost
        2 - if being pursued, distance of pacman to target smaller than ghost's
        3 - proximity of ghost in path to target

        Returns:
        A list of paths to every accessible target, ordered by cost and safety
        """

    #--------------------------------------------------------------------------#
    # IN CASE THERE ARE NO TARGETS TO SEARCH FOR
        if self.targets == []:
            return None

    #--------------------------------------------------------------------------#
    #

        eating_agent = EatingAgent(self.advisor, self.targets)
        possible_moves = eating_agent.eat()
        return possible_moves
