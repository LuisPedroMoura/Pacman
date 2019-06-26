from tree_search import *
from pathways import Pathways


class FlightAgent:

    def __init__(self, advisor, targets):
        self.advisor = advisor
        self.targets = targets
        self.pacman = advisor.pacman_info


    def flee(self):
        '''
        args:
        advisor: instance of Strategy_Advisor
                self.map_ = map_
                self.state = state
                self.unsafe_corridors = self.set_corridors_safety()
                self.pacman_info = Pacman_Info(state['pacman'])
                self.calculate_pacman_corridor()
                self.ghosts_info = self.calculate_ghosts_info()
        '''

    #--------------------------------------------------------------------------#
    # IN CASE THERE ARE NO TARGETS TO SEARCH FOR
        if self.targets == []:
            "Flight targets are empty!"
            return None

    # #--------------------------------------------------------------------------#
    # # SEARCH ALL PATHS FOR ENERGIES

        pacman = self.advisor.pacman_info
        domain = Pathways(self.advisor.map_.corr_adjacencies, self.advisor.state['energy'] + self.advisor.state['boost'], self.advisor.map_)

        all_paths_list = []

        for target in self.targets:

            # get target corridor
            corridor = None
            for corr in self.advisor.map_.corridors:
                if target[0] in corr.coordinates:
                    corridor = corr
                    break
            
            # search path
            my_prob = SearchProblem(domain, pacman.corridor, pacman.position,
                                    corridor, target[0], self.advisor.map_, self.advisor.state)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.all_path_search(target[1])

            # add search result to all_paths_list
            all_paths_list += [search_results]   

        return [move for possible_moves in all_paths_list for move in possible_moves]
    #--------------------------------------------------------------------------#
    # 

        