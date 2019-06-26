from game_consts import *
from tree_search import *
from pathways import Pathways


class EatingAgent:
    """Creates the Eating Agent, which calculates the path to all accessible
    targets, and sorts them by cost and safety with the following criteria:
    1 - cost
    2 - distance of ghost that is in Pac-Man's path

    Attr:
    advisor: provides extensive information about the current situation of the map
    targets: the targets to search paths to
    """

    def __init__(self, advisor, targets):
        self.advisor = advisor
        self.targets = targets


    def eat(self):
        """Calculates the path to all accessible targets, and sorts them by cost
        and safety with the following criteria:
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
    # CREATE DOMAIN AND AUXILIAR VARIABLES
        pacman = self.advisor.pacman_info
        acessible_energies = []
        possible_moves = []
        domain = Pathways(self.advisor.map_.corr_adjacencies, self.targets, self.advisor.map_)

    #--------------------------------------------------------------------------#
    # SEARCH FOR ENERGIES
        for energy in self.targets:
            
            # find this energy corridor
            corridor = None
            for corr in self.advisor.map_.corridors:
                if energy in corr.coordinates:
                    corridor = corr
                    break
            
            # create problem and search
            my_prob = SearchProblem(domain, corridor, energy, pacman.corridor, \
                                    pacman.position, self.advisor.map_, self.advisor.state)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.search()
            
            # filter valid results and store them in possible_moves
            if search_results != None:
                acessible_energies += [energy]
                possible_moves += [search_results]

        # if there are no possible moves, everything is eaten
        if len(possible_moves) == 0:
            return possible_moves

    #-------------------------------------------------------------------------#
    # SORT MOVES BY COST
        possible_moves = sorted(possible_moves,key=lambda res: res[1])
    
    #--------------------------------------------------------------------------#
    # SORT MOVES BY WHERE A GHOST IS BLOCKING THE NEXT CORRIDOR
        f_moves = []
        for move in possible_moves:
            if move[2][-3].safe == CORRIDOR_SAFETY.UNSAFE:
                f_moves += [move]

        possible_moves = [move for move in possible_moves if move not in f_moves]
        possible_moves += f_moves

    #--------------------------------------------------------------------------#
    # SORT MOVES BY WHERE A GHOST IS BLOCKING PAC-MAN CORRIDOR
        f_moves = []
        for move in possible_moves:
            if move[2][-2].safe == CORRIDOR_SAFETY.UNSAFE:
                f_moves += [move]

        possible_moves = [move for move in possible_moves if move not in f_moves]
        possible_moves += f_moves

    #--------------------------------------------------------------------------#
    # RETURN OPTIONS
        return possible_moves