from game_consts import *


class MoveRiskAssessor():
    """Creates the Move Risk Assessor which main purpose is to validate the
    next move advised by the Execution Agents (Pursuit, Eating, Counter, Flight).
    Calculates immediate and future threats of the advised move (eg the path to 
    next coordinate is blocked by a ghost, or, getting to a target although successful
    will put Pac-Man in danger of entrapment)

    Attr:
    advisor: Strategy Advisor which contains analysed information from the current
        game situation
    ghosts_in_pursuit: number of ghosts at a distance smaller than 'SAFE_DIST_TO_GHOST'
    """

    def __init__(self, advisor, ghosts_in_pursuit):
        self.advisor = advisor
        self.ghosts_in_pursuit = ghosts_in_pursuit


    def analyse_best_move(self, possible_moves, flight=False, surrounded_eating=False, counter=False):
        """Applies several tests to verify tha dangerousness of the advised moves
        of the Execution Agents

        Args:
        possible_moves: list of advise next moves of Pac-Man
        flight: boolean tag that conditions some tests
        surrounded_eating: boolean tag that conditions some tests
        counter: boolean tag that conditions some tests
        """

        if possible_moves == []:
            return False

        # using only first (already sorted as best) advised move
        move = possible_moves[0]
        _, cost, path = move


        path_coords = [c for corr in path for c in corr.coordinates]
        aux = []
        for c in path_coords:
            if c not in aux:
                aux += [c]
        path_coords = aux

        pacman = self.advisor.pacman_info

        sub_corr0, sub_corr1 = pacman.corridor.sub_corridors(pacman.position)
        sub_corr0 = sub_corr0.coordinates[:-1]
        sub_corr1 = sub_corr1.coordinates[1:]
        crossroad = None
        semaphore = None
        ghost = None

        # verify which side of path pacman wants to go and it's condition
        if any([c in path_coords for c in sub_corr0]):
            crossroad = pacman.crossroad0
            semaphore = pacman.semaphore0
            ghost = pacman.ghost_at_crossroad0
        elif any([c in path_coords for c in sub_corr1]):
            crossroad = pacman.crossroad1
            semaphore = pacman.semaphore1
            ghost = pacman.ghost_at_crossroad1
        else:
            crossroad = pacman.position
            semaphore = pacman.semaphore(crossroad)
            ghost = pacman.ghost_at_crossroad(crossroad)

#------------------------------------------------------------------------------#
# TEST: NO GHOST ATTACKING IN THE DIRECTION PAC-MAN IS GOING
        if ghost == None:
            return True

#------------------------------------------------------------------------------#
# TEST: POISONOUS TARGET - IF PAC-MAN EATS TARGET, IS EATEN BY GHOST AT THE SAME TIME
        tx,ty = move[0]
        gx,gy = ghost.position
        if gx==tx+1 or gx==tx-1 or gy==ty+1 or gy==ty-1:
            if gx==tx or gy==ty:
                if move[1] == 1:
                    return False

#------------------------------------------------------------------------------#
# TEST: BLOCKED PATH- GHOSTS IS IN THE FIRST CORRIDOR OF THE PATH TO TARGET
        if flight == False:
            if ghost.position in path[-2].coordinates:
                return False
        else:
            if ghost.position in path[1].coordinates:
                return False

#------------------------------------------------------------------------------#
# TEST: ENTRAPMENT - TARGET ACCESSIBLE, BUT PAC-MAN IS BLOCKED FROM BEHIND
#       AND NEXT CORRIDOR IS ALSO CURRENTLY BLOCKED
        if flight == False:
            if pacman.pursued_from_other_crossroad(crossroad):
                if len(path) >= 3:
                    if ghost.position in path[-3].coordinates:
                        return False
        else:
            if pacman.pursued_from_other_crossroad(crossroad):
                if len(path) >= 3:
                    if ghost.position in path[2].coordinates:
                        return False

#------------------------------------------------------------------------------#
# TEST: STOP SIGNAL - THE GHOST IS NOT IN THE PATH, BUT JUST A THE INTERSECTION
#       OF PAC-MAN'S CORRIDOR, EXITING MEANS DEATH
        if pacman.dist_to_crossroad(crossroad) == 1 and ghost.dist_to_crossroad == 1:
            return False
        
#------------------------------------------------------------------------------#
# TEST: INTERSEPTION - GHOST AT UNSAFE DISTANCE IS NOT IN PAC-MAN'S PATH BUT
#       WILL INTERCEPT
        if pacman.pursued_from_crossroad(crossroad):
            if ghost.position not in [c for corr in path for c in corr.coordinates]:
                if ghost.side_interception(path):
                    return False

#------------------------------------------------------------------------------#
# TEST: PROBABLE FUTURE INTERSEPTION - GHOST NOT IN PATH IS NOT IN PURSUIT, BUT
#       PAC-MAN IS SURROUNDED AND MAY RISK OF INTERSEPTION IN ESCAPE PATH IS
#       LIKELY
        if flight or surrounded_eating:
            for ghost in self.advisor.ghosts_info:
                if ghost.crossroad_to_pacman == crossroad:
                    if ghost.side_interception(path):
                        return False

#------------------------------------------------------------------------------#
# TEST: FUTURE ENTRAPMENT - TARGET ACCESSIBLE AND NOT BLOCKED, BUT PAC-MAN IS
#       BLOCKED FROM BEHIND AND WHEN PAC-MAN REACHES THE TARGET A FUTURE
#       ENTRAPMENT IS VERY LIKELY (EXCEPTIONS APPLY INSIDE TEST)
        if pacman.position in self.advisor.map_.crossroads and self.ghosts_in_pursuit >= 0:

            #ignore trap because there is a Boost inside the new corridor
            if counter == True:
                if cost < (ghost.dist_to_pacman - cost):
                    return True

            # ignore trap, few targets left, Pac-Man has 3 lifes and can play more
            # aggressively. Avoids losing time outwiting ghosts
            if len(self.advisor.state['energy']) < 20 and self.advisor.state['lives'] >= 2:
                return True
            
            # ignore trap very few target left, Pac-Man has 2 lifes and can play more
            # aggressively. High probability of winning the game and not losing life
            # Avoids losing time outwiting ghosts
            if len(self.advisor.state['energy']) < 5 and self.advisor.state['lives'] == 2:
                return True

            if pacman.ghost_at_crossroad(pacman.get_other_crossroad(crossroad)) != None:
                if pacman.dist_to_ghost_at_crossroad(pacman.get_other_crossroad(crossroad)) < 3:
                    
                    if not flight:
                        next_move = path[-2].get_coord_next_to_end(pacman.position)
                    if flight:
                        next_move = path[1].get_coord_next_to_end(pacman.position)

                    corr = None
                    for c in self.advisor.map_.corridors:
                        if next_move in c.coordinates:
                            corr = c
                            break

                    if pacman.ghost_at_crossroad(crossroad).is_coord_in_path(corr.get_other_end(crossroad)):
                        
                        next_move_dist_to_end = corr.dist_to_end(next_move, corr.get_other_end(crossroad))
                        other_ghost_dist_to_end = pacman.dist_to_ghost_at_crossroad(crossroad) - corr.cost
                        if next_move_dist_to_end >= other_ghost_dist_to_end-1:
                            #self.avoid_coordinates = corr.get_coord_next_to_end(pacman.position)
                            return False

                    elif pacman.ghost_at_crossroad(crossroad).position in corr.coordinates:
                        return False

        return True
        