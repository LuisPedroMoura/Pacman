from game_consts import *
from tree_search import SearchProblem, SearchTree
from pathways import Pathways
from corridor import Corridor
from ghost_info import Ghost_Info
from pacman_info import Pacman_Info

class StrategyAdvisor():
    """Analyses corridors safety (if contains ghost or not) and crossroads
    semaphores. Advises on a strategy for the given conditions.

    Args:
    map_: instance of Map for the current level
    state: the game state given by the server

    Attr:
    ghosts: A set of quadruples with (ghost_position, zombie, timeout, distance_to_pacman)
    """

    def __init__(self, map_, state):
        self.map_ = map_
        self.state = state
        self.unsafe_corridors = []
        self.pacman_info = None
        self.non_zombie_ghosts = []
        self.zombie_ghosts = []
        self.ghosts_info = []

        self._analyse_situation()

#------------------------------------------------------------------------------# 

    def _analyse_situation(self):

        self._set_corridors_safety()
        self.pacman_info = Pacman_Info(self.state['pacman'])
        self._calculate_pacman_corridor()
        self._calculate_ghosts_info()
        self._calculate_pacman_safeties()

#------------------------------------------------------------------------------#

    #* COMPLETE - NOT TESTED
    def _set_corridors_safety(self):
        """Sets the corridors safety flag according to the existence of ghosts

        Args:
        ghots: a list with the position of all non zombie ghosts

        Returns:
        A list of tuples with the unsafe corridors and the position of the ghost
        in that corridor. If more than one ghost is in a given corridors, the
        corridor is returned multiple times tupled with each ghost 
        """

        unsafe_corridors = []
        for ghost in [ghost for ghost in self.state['ghosts'] if ghost[1] == False]: # non zombie ghosts
            for [cA, cB] in self.map_.corr_adjacencies:
                cA.safe = CORRIDOR_SAFETY.SAFE
                cB.safe = CORRIDOR_SAFETY.SAFE
                if ghost[0] in cA.coordinates:
                    cA.safe = CORRIDOR_SAFETY.UNSAFE
                    unsafe_corridors += [cA]
                if ghost[0] in cB.coordinates:
                    cB.safe = CORRIDOR_SAFETY.UNSAFE
                    unsafe_corridors += [cB]
        
        self.unsafe_corridors = list(set(unsafe_corridors))
            
#------------------------------------------------------------------------------#

    def _calculate_ghosts_info(self):
        """Calculates the information of ghosts and their attack paths to pacman

        Sets:
        self.non_zombie_ghots: a list of active ghosts (will eat Pac-Man)
        self.zombie_ghots: a list of inactive ghosts (Pac-Man can eat them)
        self.ghosts_info: list of ghosts and associated information (object Ghost_Info)
            each ghost is represented twice, one for each side it will attack Pac-Man
        self.ghosts_at_cross0: list of ghosts that will attack Pac-Man at crossroad0
        self.ghosts_at_cross1: list of ghosts that will attack Pac-Man at crossroad1
        """

        self.non_zombie_ghosts = [ghost for ghost in self.state['ghosts'] if ghost[1] == False]
        self.zombie_ghosts = [ghost for ghost in self.state['ghosts'] if ghost[1] == True]

        pacman = self.pacman_info.position
        pac_corridor = self.pacman_info.corridor
        pac_subcorr0, pac_subcorr1 = pac_corridor.sub_corridors(pacman)
        ghost_corr = None
        ghosts_at_cross0 = []
        ghosts_at_cross1 = []

        for [ghost,zombie,timeout] in self.non_zombie_ghosts:

            domain = Pathways(self.map_.corr_adjacencies, ghost, self.map_)
            for corr in self.unsafe_corridors:
                if ghost in corr.coordinates:
                    ghost_corr = corr
                    break
                else:
                    ghost_corr = None

            # calculate trajectory of every ghost towards Pac-Man
            if ghost_corr != None: # if ghost is not in ghosts_den
                
                # calculate path from ghost to pacman through Pac-Manś crossroad1
                my_prob = SearchProblem(domain, self.pacman_info.corridor, pacman, \
                                        ghost_corr, ghost, \
                                        self.map_, self.state)
                my_tree = SearchTree(my_prob, "a*")
                
                avoid_coordinates = self._get_avoid_coordinates(pac_subcorr0)
                search_result = my_tree.all_path_search(avoid_coordinates)
                if search_result != []:
                    _, cost1, path1 = search_result[0]
                    ghosts_at_cross1 += [Ghost_Info(ghost, zombie, timeout, \
                                        ghost_corr, cost1, self.pacman_info.crossroad1, \
                                        cost1 - self.pacman_info.dist_to_crossroad1, \
                                        path1)]


                # calculate path from ghost to pacman through Pac-Man crossroad0
                my_prob = SearchProblem(domain, self.pacman_info.corridor, pacman, \
                                        ghost_corr, ghost, \
                                        self.map_, self.state)
                my_tree = SearchTree(my_prob, "a*")

                avoid_coordinates = self._get_avoid_coordinates(pac_subcorr1)
                search_result = my_tree.all_path_search(avoid_coordinates)
                if search_result != []:
                    _, cost0, path0 = search_result[0]
                    ghosts_at_cross0 += [Ghost_Info(ghost, zombie, timeout, \
                                        ghost_corr, cost0, self.pacman_info.crossroad0, \
                                        cost0 - self.pacman_info.dist_to_crossroad0, \
                                        path0)]
            else:
                continue
                
        g0 = sorted(ghosts_at_cross0, key=lambda ghost: ghost.dist_to_pacman)
        g1 = sorted(ghosts_at_cross1, key=lambda ghost: ghost.dist_to_pacman)

        self.ghosts_info = g0 + g1
        self.ghosts_at_cross0 = g0
        self.ghosts_at_cross1 = g1

# --auxiliar method to previous method-----------------------------------------#
    def _get_avoid_coordinates(self, sub_corr):
        pacman = self.pacman_info.position
        avoid_coordinates = []
        avoid = sub_corr.get_coord_next_to_end(pacman)
        if avoid == None:
            for corr in self.map_.corridors:
                if corr != self.pacman_info.corridor:
                    if pacman in corr.ends:
                        av = corr.get_coord_next_to_end(pacman)
                        if av != None:
                            avoid_coordinates += [av]
        else:
            avoid_coordinates += [avoid]

        return avoid_coordinates

#------------------------------------------------------------------------------#

    def _calculate_pacman_corridor(self):

        pac_all_corr = [corr for corr in self.map_.corridors if self.pacman_info.position in corr.coordinates]
        pac_unsafe_corr = [corr for corr in pac_all_corr if corr in self.unsafe_corridors]

        pac_corridor = None
        if len(pac_unsafe_corr) == 0:
            pac_corridor = pac_all_corr[0]

        elif len(pac_unsafe_corr) == 1:
            pac_corridor = pac_unsafe_corr[0]

        elif len(pac_unsafe_corr) > 1:
            aux = []
            live_ghosts = [ghost for ghost in self.state['ghosts'] if ghost[1] == False]
            for ghost in live_ghosts:
                for corr in pac_unsafe_corr:
                    if ghost[0] in corr.coordinates:
                        aux += [(corr, ghost[0])]

            dist = aux[0][0].dist_between_coords(self.pacman_info.position, aux[0][1])
            pac_corridor = aux[0][0]

            for (corr,ghost) in aux:
                new_dist = corr.dist_between_coords(self.pacman_info.position, ghost)
                if new_dist < dist:
                    dist = new_dist
                    pac_corridor = corr

        self.pacman_info.update_corridor(pac_corridor)

#------------------------------------------------------------------------------#

    def _calculate_pacman_safeties(self):
        """Computes the information to update Pacman_Info regarding its safety
        (ie crossroad semaphore, distance to ghost at that crossroad, which
        ghost at the crossroad, etc)
        """

        g0 = self.ghosts_at_cross0
        g1 = self.ghosts_at_cross1

        # if there are no ghosts (all are zombie or in the den)
        if g0 == [] and g1 == []:
            return

        # there is only on ghost
        if len(g0) == 1 and len(g1) == 1:
            if g0[0].dist_to_pacman < g1[0].dist_to_pacman:
                self.pacman_info.update_safeties(g0[0])
            elif g0[0].dist_to_pacman > g1[0].dist_to_pacman:
                self.pacman_info.update_safeties(g1[0])
            else:
                self.pacman_info.update_safeties(g0[0])
                self.pacman_info.update_safeties(g1[0])
            return

        # more than one ghost
        # the same ghost is closer to pacman from the crossroad0 and crossroad1
        if g0[0].position == g1[0].position:
            # closer from crossroad0 - pick that one to cross0 and next on cross1
            if g0[0].dist_to_pacman < g1[0].dist_to_pacman:
                self.pacman_info.update_safeties(g0[0])
                self.pacman_info.update_safeties(g1[1])
            # closer from crosroad1 - pick that one to cross1 and next on cross0
            elif g0[0].dist_to_pacman > g1[0].dist_to_pacman:
                self.pacman_info.update_safeties(g1[0])
                self.pacman_info.update_safeties(g0[1])
            # same distance from both crossroads
            else:
                # evaluate distance o next closer ghost on cross0 and cross1
                if g0[1].dist_to_pacman < g1[1].dist_to_pacman:
                    self.pacman_info.update_safeties(g0[1])
                    self.pacman_info.update_safeties(g1[0])
                else:
                    self.pacman_info.update_safeties(g1[1])
                    self.pacman_info.update_safeties(g0[0])
        # closer ghosts from cross0 and cross1 are different
        else:
            self.pacman_info.update_safeties(g0[0])
            self.pacman_info.update_safeties(g1[0])
