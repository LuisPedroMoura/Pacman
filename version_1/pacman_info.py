from corridor import Corridor
from game_consts import *

class Pacman_Info():
    """Creates the Pac-Man Info, which is a collection of information on Pac-Man
    in a specific moment of gameplay.

    Attr:
    position: the coordinates of the ghost
    corridor: the corridor where Pac-Man is positioned
    crossrods (crossroad0 & crossroad1): the extremities of 'corridor'
    dist_to_crossroad0(1): distance of Pac-Man to each crossroad  
    semaphore0(1): Enumerate that identifies danger of corresponding crossroad
    dist_to_ghost_at_crossroad_0(1): distance to the closest ghost attacking at
        crossroad
    crossroad0(1)_is_blocked: boolean flag that indicates a ghost is inside
        'corridor' and at which side
    pursued_from_crossroad0(1): boolean flag that indicates is in pursuit distance
        of Pac-Man and will attack from that crossroad
    ghost_at_crossroad0(1): the closest 'Ghost_Info' that will attack at the
        crossroad, contains all information on said ghost
    """

    def __init__(self, pacman):
        self.position = pacman

        self.corridor = None
        self.crossroads = None
        self.crossroad0 = None
        self.crossroad1 = None
        self.dist_to_crossroad0 = None
        self.dist_to_crossroad1 = None

        self.semaphore0 = None
        self.semaphore1 = None
        self.dist_to_ghost_at_crossroad0 = None
        self.dist_to_ghost_at_crossroad1 = None

        # evaluates if a ghost is inside the corridor, blocking the crossroad
        self.crossroad0_is_blocked = False 
        self.crossroad1_is_blocked = False

        # evaluates if the closest ghost in the direction of crossroad is at safe distance (game_consts.pySAFE_DIST_TO_GHOST)
        self.pursued_from_crossroad0 = False
        self.pursued_from_crossroad1 = False

        self.ghost_at_crossroad0 = None
        self.ghost_at_crossroad1 = None

    # called in strategy_advisor, calculate_pacman_corridor()
    def update_corridor(self, corridor):
        self.corridor = corridor
        self.crossroads = corridor.ends
        self.crossroad0 = corridor.ends[0]
        self.crossroad1 = corridor.ends[1]
        self.dist_to_crossroad0 = corridor.dist_end0(self.position)
        self.dist_to_crossroad1 = corridor.dist_end1(self.position)


    def update_safeties(self, ghost):
        if ghost.crossroad_to_pacman == self.crossroad0:
            self.ghost_at_crossroad0 = ghost
            self.dist_to_ghost_at_crossroad0 = ghost.dist_to_pacman
            safe_dist = ghost.dist_to_crossroad - self.dist_to_crossroad0
            if safe_dist <= 0:
                self.semaphore0 = SEMAPHORE.RED
            elif safe_dist > 0 and safe_dist <= SAFE_DIST_TO_CROSSROAD:
                self.semaphore0 = SEMAPHORE.YELLOW
            else:
                self.semaphore0 = SEMAPHORE.GREEN
            if ghost.dist_to_crossroad <= 0:
                self.crossroad0_is_blocked = True
            if ghost.dist_to_pacman <= SAFE_DIST_TO_GHOST:
                self.pursued_from_crossroad0 = True
        elif ghost.crossroad_to_pacman == self.crossroad1:
            self.ghost_at_crossroad1 = ghost
            self.dist_to_ghost_at_crossroad1 = ghost.dist_to_pacman
            safe_dist = ghost.dist_to_crossroad - self.dist_to_crossroad1
            if safe_dist <= 0:
                self.semaphore1 = SEMAPHORE.RED
            elif safe_dist > 0 and safe_dist <= SAFE_DIST_TO_CROSSROAD:
                self.semaphore1 = SEMAPHORE.YELLOW
            else:
                self.semaphore1 = SEMAPHORE.GREEN
            if ghost.dist_to_crossroad <= 0:
                self.crossroad1_is_blocked = True
            if ghost.dist_to_pacman <= SAFE_DIST_TO_GHOST:
                self.pursued_from_crossroad1 = True


    def dist_to_crossroad(self, crossroad):
        if crossroad == self.crossroad0:
            return self.dist_to_crossroad0
        elif crossroad == self.crossroad1:
            return self.dist_to_crossroad1
        else:
            return None


    def pursued_from_crossroad(self, crossroad):
        if crossroad == self.crossroad0:
            return self.pursued_from_crossroad0
        elif crossroad == self.crossroad1:
            return self.pursued_from_crossroad1
        else:
            return None


    def pursued_from_other_crossroad(self, crossroad):
        if crossroad == self.crossroad0:
            return self.pursued_from_crossroad1
        elif crossroad == self.crossroad1:
            return self.pursued_from_crossroad0
        else:
            return None


    def ghost_at_crossroad(self, crossroad):
        if crossroad == self.crossroad0:
            return self.ghost_at_crossroad0
        elif crossroad == self.crossroad1:
            return self.ghost_at_crossroad1
        else:
            return None


    def dist_to_ghost_at_crossroad(self, crossroad):
        if crossroad == self.crossroad0:
            return self.dist_to_ghost_at_crossroad0
        elif crossroad == self.crossroad1:
            return self.dist_to_ghost_at_crossroad1
        else:
            return None


    def get_other_crossroad(self, crossroad):
        if crossroad == self.crossroad0:
            return self.crossroad1
        if crossroad == self.crossroad1:
            return self.crossroad0
        else:
            return None


    def semaphore(self, crossroad):
        if crossroad == self.crossroad0:
            return self.semaphore0
        elif crossroad == self.crossroad1:
            return self.semaphore1
        else:
            return None
    
    
    def __str__(self):
        string = \
        'Pac-Man is in position ' + str(self.position) + '\n'

        if self.ghost_at_crossroad0 != None:
            string += \
            'Ghost ' + str(self.ghost_at_crossroad0.position) + ' is at crossroad ' + str(self.crossroad0) + \
            ' at distance ' + str(self.dist_to_ghost_at_crossroad0) + ' from Pc-Man '
        if (self.dist_to_ghost_at_crossroad0 != None):
            string += \
            ' at distance ' + str(self.dist_to_ghost_at_crossroad0 - self.dist_to_crossroad0) + ' of crossroad \n' + \
            'with the semaphore ' + str(self.semaphore0) + '\n' + \
            'Pac-Man distance to this crossroad0 is ' + str(self.dist_to_crossroad0) + '\n'

        if self.ghost_at_crossroad1 != None:
            string += \
            'Ghost ' + str(self.ghost_at_crossroad1.position) + ' is at crossroad ' + str(self.crossroad1) + \
            ' at distance ' + str(self.dist_to_ghost_at_crossroad1) + ' from Pc-Man'
        if (self.dist_to_ghost_at_crossroad1 != None):
            string += \
            ' at distance ' + str(self.dist_to_ghost_at_crossroad1 - self.dist_to_crossroad1) + ' of crossroad \n' + \
            'with the semaphore ' + str(self.semaphore1) + '\n' \
            'Pac-Man distance to this crossroad1 is ' + str(self.dist_to_crossroad1)

        return string

    def __repr__(self):
        return self.__str__()