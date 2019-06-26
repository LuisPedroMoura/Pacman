from tree_search import *
from pathways import Pathways
from corridor import *


class PanicAgent:
    """Creates Panic Agent, which is called after all other Execution Agents
    advised moves have been considered invalid. It's objective is to find the
    closest safest corridor

    Attr:
    advisor: provides extensive information about the current situation of the map
    pac_info: Object with extensive information on Pac-Man
    ... : various information extracted from 'pac_info' form visual code simplification
    """

    def __init__(self, advisor):
        self.advisor = advisor
        self.pac_info = advisor.pacman_info
        self.pacman = advisor.pacman_info.position
        self.crossroad0 = advisor.pacman_info.crossroad0
        self.crossroad1 = advisor.pacman_info.crossroad1
        self.semaphore0 = advisor.pacman_info.semaphore0
        self.semaphore1 = advisor.pacman_info.semaphore1


    def panic(self, invalid_corridors):
        '''Calculates the next move of Pac-Man based on the surrounding corridors
        and their safety. Choses one from the best possible outcomes.

        Args:
        advisor: instance of Strategy_Advisor
        pac_info: instance of Pacman_Info
        pacman: coordinates of Pac-Man position
        crossroad0: coordinates of crossroad0 of Pac-Man corridor
        crossroad1: coordinates of crossroad0 of Pac-Man corridor
        semaphore0: semaphore of crossroad0 of Pac-Man corridor
        semaphore1: semaphore of crossroad1 of Pac-Man corridor

        Returns:
        The cordinate where advises Pac-Man to go next
        '''
    
        pac_adj0, pac_safe_corr0, pac_unsafe_corr0 = self.calc_adj_and_safe(self.pac_info.crossroads[0])
        escape_corridors0 = pac_safe_corr0 if pac_safe_corr0 != [] else pac_adj0

        pac_adj1, pac_safe_corr1, pac_unsafe_corr1 = self.calc_adj_and_safe(self.pac_info.crossroads[1])
        escape_corridors1 = pac_safe_corr1 if pac_safe_corr1 != [] else pac_adj1

        aux0 = []
        aux1 = []
        aux_adj0 = []
        aux_adj1 = []
        aux_safe0 = []
        aux_safe1 = []

        for corr in invalid_corridors:

            for c in pac_adj0:
                if all([coord in c.coordinates for coord in corr.coordinates]):
                    aux_adj0 += [c]

            for c in pac_adj1:
                if all([coord in c.coordinates for coord in corr.coordinates]):
                    aux_adj0 += [c]

            for c in pac_safe_corr0:
                if all([coord in c.coordinates for coord in corr.coordinates]):
                    aux_adj0 += [c]

            for c in pac_safe_corr1:
                if all([coord in c.coordinates for coord in corr.coordinates]):
                    aux_adj0 += [c]

            for c in escape_corridors0:
                if all([coord in c.coordinates for coord in corr.coordinates]):
                    aux_adj0 += [c]

            for c in escape_corridors1:
                if all([coord in c.coordinates for coord in corr.coordinates]):
                    aux_adj0 += [c]
        
        if aux0 != []:
            escape_corridors0 = aux0
        if aux1 != []:
            escape_corridors1 = aux1
        if aux_adj0 != []:
            pac_adj0 = aux_adj0
        if aux_adj1 != []:
            pac_adj1 = aux_adj1
        if aux_safe0 != []:
            pac_safe_corr0 = aux_safe0
        if aux_safe1 != []:
            pac_safe_corr1 = aux_safe1

        all_adjacent_corridors = pac_adj0 + pac_adj1
        all_safe_adjacent_corridors = pac_safe_corr0 + pac_safe_corr1
        all_unsafe_adjacent_corridors = pac_unsafe_corr0 + pac_unsafe_corr1
        all_escape_corridors = escape_corridors0 + escape_corridors1
   
    #--------------------------------------------------------------------------#
    # PAC-MAN CORRIDOR IS UNSAFE (THERE IS A GHOSTS IN THE CORRIDOR)

        # pacman is blocked from both sides - moves to the side with the farthest ghost
        if self.pac_info.crossroad0_is_blocked == True and self.pac_info.crossroad1_is_blocked == True:
            if self.pac_info.dist_to_ghost_at_crossroad0 >= self.pac_info.dist_to_ghost_at_crossroad1:
                # 0 - blocked from both sides: goes for 0
                return self.calc_next_coord(self.pacman, self.crossroad0, [])
            else:
                # 1 - blocked from both sides: goes for 1
                return self.calc_next_coord(self.pacman, self.crossroad1, [])
        
        # pacman is blocked only from one side - moves to the other side (probably)
        if self.pac_info.crossroad0_is_blocked == True or self.pac_info.crossroad1_is_blocked == True:
            blocked_cross = None
            free_cross = None
            semaphore = None
            escape_coridors = None
            if self.pac_info.crossroad0_is_blocked == True:
                blocked_cross = self.crossroad0
                free_cross = self.crossroad1
                semaphore = self.pac_info.semaphore1
                escape_corridors = escape_corridors1
            if self.pac_info.crossroad1_is_blocked == True:
                blocked_cross = self.crossroad1
                free_cross = self.crossroad0
                semaphore = self.pac_info.semaphore0
                escape_corridors = escape_corridors0

            # unblocked crossroad is not red - pacman can pass through it
            if semaphore == SEMAPHORE.YELLOW or semaphore == SEMAPHORE.GREEN:   
                # 2 - blocked from side: ' + str(blocked_cross) + ' goes for ' + str(free_cross) + 'which is yellow or green
                next_corr = self.calc_next_corridor(escape_corridors)
                return self.calc_next_coord(self.pacman, free_cross, next_corr)

            # unblocked crossroad is red - pacman cannot go through it
            if semaphore == SEMAPHORE.RED:
                # 3 - blocked from side: ' + str(blocked_cross) + ' goes for ' + str(free_cross) + 'which is red
                return self.escape_to_farthest_ghost_side(free_cross, blocked_cross)


    #--------------------------------------------------------------------------#
    # PAC-MAN CORRIDOR IS SAFE (THERE IS NOT A GHOSTS IN THE CORRIDOR)

        # both crossroads are red - chooses side with farthest ghost
        if self.semaphore0 == SEMAPHORE.RED and self.semaphore1 == SEMAPHORE.RED:
            # 4 - not blocked. Both crossroads are red: goes for farthest side
            return self.escape_to_farthest_ghost_side(self.crossroad0, self.crossroad1)

        # one crossroad is red - chooses the other crossroad
        if self.semaphore0 == SEMAPHORE.RED:
            next_corr = self.calc_next_corridor(escape_corridors1)
            # 5 - not blocked. crossroad ' + str(self.crossroad0) + ' is red, goes for the other
            return self.calc_next_coord(self.pacman, self.crossroad1, next_corr)
        if self.semaphore1 == SEMAPHORE.RED:
            next_corr = self.calc_next_corridor(escape_corridors0)
            # 6 - not blocked. crossroad ' + str(self.crossroad1) + ' is red, goes for the other
            return self.calc_next_coord(self.pacman, self.crossroad0, next_corr)

        # both crossroads are yellow - chooses farthest crossroad
        if self.semaphore0 == SEMAPHORE.YELLOW and self.semaphore1 == SEMAPHORE.YELLOW:
            # 7 - not blocked. both crossroads are yellow: goes for farthest side
            return self.escape_to_farthest_crossroad(self.crossroad0, self.crossroad1, escape_corridors0, escape_corridors1)

        # crossroads are green or yellow - chooses a safe corridor
        if all_safe_adjacent_corridors != []:
            next_corr = self.calc_next_corridor(all_safe_adjacent_corridors)
            # 8 - not blocked. crossroads are green or yellow: goes for a safe corridor
            return self.calc_next_coord(pacman=self.pacman, crossroad=None , next_corridor=next_corr)

        next_corr = self.calc_next_corridor(all_adjacent_corridors)
        # 9 - not blocked. crossroads are green or yellow: goes for an unsafe corridor
        return self.calc_next_coord(pacman=self.pacman, crossroad=None , next_corridor=next_corr)


    def calc_adj_and_safe(self, crossroad):

        aux = []
        adj_corrs = []
        safe_corrs = []
        unsafe_corrs = []
        aux += [cA for [cA, cB] in self.advisor.map_.corr_adjacencies if crossroad in cA.ends]
        aux += [cB for [cA, cB] in self.advisor.map_.corr_adjacencies if crossroad in cB.ends]

        #remove pacman corridor
        aux = [c for c in aux if c != self.pac_info.corridor]
        aux = list(set(aux))

        # set corridors as unsafe
        for corr in aux:
            ghost_in_corr = False
            for ghost in [ghost for ghost in self.advisor.state['ghosts'] if ghost[1] == False]:
                if ghost[0] in corr.coordinates:
                    ghost_in_corr = True
            
            if not ghost_in_corr:
                corr.safe = CORRIDOR_SAFETY.SAFE
                safe_corrs += [corr]
            if ghost_in_corr:
                corr.safe = CORRIDOR_SAFETY.UNSAFE
                unsafe_corrs += [corr]
            adj_corrs += [corr]

        return adj_corrs, safe_corrs, unsafe_corrs
                

    def calc_next_coord(self, pacman, crossroad, next_corridor):
        '''Calculates the next position where Pac-Man should go to, according to
        the next safe Corridor, and the Crossroad that connects Pac-Man's
        Corridor to it
        
        Args:
        pacman: Pac-Man position
        crossroad: Crossroad that indicates which side of Pac-Man should move
            in it's corridor
        next_corridor : the Corridor considered as the safest to go to in the
            next move

        Returns:
        The coordinates of the next position Pac-Man should go to
        '''

        next_move = None

        # Pac-Man has to move within it's Corridor
        if next_corridor == []:
            if crossroad != None:
                return self.advisor.pacman_info.corridor.get_next_coord_to_the_side_of_crossroad(pacman, crossroad)
            else:
                return None
        
        # Pc-Man is at a crossroad and may move either into or out of it's Corridor
        if next_corridor != []:
            # crossroad is None
            if crossroad == None:
                crossroad = [c for c in next_corridor.ends if c in self.pac_info.corridor.ends][0]
                next_move = self.pac_info.corridor.get_next_coord_to_the_side_of_crossroad(pacman, crossroad)
                if next_move != None:
                    return next_move
                else: # pacman is in the crossroad
                    return next_corridor.get_coord_next_to_end(crossroad)
            # crossroad exists
            else:
                # tries to get next coordinate to the side of crossroad
                next_move =  self.advisor.pacman_info.corridor.get_next_coord_to_the_side_of_crossroad(pacman, crossroad)
                if next_move != None:
                    return next_move
                else:
                    return next_corridor.get_coord_next_to_end(crossroad)


    #escolhe corr com ghost mais afastado
    def calc_next_corridor(self, pac_adj):
        
        safe_corrs = []
        for corr in pac_adj:
            if corr.safe == CORRIDOR_SAFETY.SAFE:

                if any([c in self.advisor.state['energy'] for c in corr.coordinates]):
                    return corr

                safety_number = self.long_range_safety(corr.ends[0])
                safety_number += self.long_range_safety(corr.ends[1])
                safe_corrs += [(corr, safety_number)]
        
        if len(safe_corrs) != 0:
            safe_corrs = sorted(safe_corrs, key=lambda t: t[1])
            return safe_corrs[0][0]

        corridors_with_ghost = []
        corridors_with_ghost = [(corr, ghost.dist_to_pacman) for ghost in self.advisor.ghosts_info \
                                                            for corr in pac_adj]

        return sorted(corridors_with_ghost, key=lambda t: t[1], reverse=True)[0][0]


    def escape_to_farthest_ghost_side(self, cross0, cross1):
        if self.pac_info.dist_to_ghost_at_crossroad(cross0) <= self.pac_info.dist_to_ghost_at_crossroad(cross1):
            return self.calc_next_coord(self.pacman, cross1, [])
        else:
            return self.calc_next_coord(self.pacman, cross0, [])

    def escape_to_farthest_crossroad(self, cross0, cross1, escape_corridors0, escape_corridors1):
        
        if self.pac_info.dist_to_crossroad(cross0) >= self.pac_info.dist_to_crossroad(cross1):
            next_corr = self.calc_next_corridor(escape_corridors0)
            return self.calc_next_coord(self.pacman, cross0, next_corr)  
        else:
            next_corr = self.calc_next_corridor(escape_corridors1)
            return self.calc_next_coord(self.pacman, self.crossroad1, next_corr)

    def long_range_safety(self, crossroad):
        _, _, unsafe_corrs = self.calc_adj_and_safe(crossroad)
        return len(unsafe_corrs)

