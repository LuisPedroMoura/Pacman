from tree_search import SearchDomain
from corridor import Corridor
import math

class Pathways(SearchDomain):

    def __init__(self, adjacencies, targets, map_):
        self.adjacencies = adjacencies
        self.targets = targets
        self.map_ = map_

    def actions(self,corridor):
        """Calculates the next action(corridor adjacency) for the tre_search.
        Avoids searches if the target is immediately surrounded by al sides

        Args:
        corridor: current node
        """
        actlist = []

        for (corr1, corr2) in self.adjacencies:
            
            if (corr1.coordinates == corridor.coordinates):
                actlist += [(corr1, corr2)]

            elif (corr2.coordinates == corridor.coordinates):
                actlist += [(corr2, corr1)]

        if corridor.cost == 0: #is the initial or final corridor
            surrounded = []
            for (corr1, corr2) in actlist:
                if corr2.get_coord_next_to_end(corridor.coordinates[0]) in self.targets:
                    surrounded += [True]
                else:
                    surrounded += [False]
            
            if all(surrounded):
                actlist = []

        return actlist

    def result(self,corridor,action):
        corr1, corr2 = action
        if corr1 == corridor:
            return corr2
 
    def cost(self, cur_corr, action):
        corr1, corr2 = action
        if (corr1 != cur_corr):
            return None
        return corr2.cost


    def heuristic(self, curr_state, new_state, goal, hor_tunnel=False, ver_tunnel=False):
        """Calculates the heuristic cost of current position to goal. Uses the
        Manhattan distance adapted to a circular map.
        """
        c_ends = curr_state.ends
        n_ends = new_state.ends

        c_end = [ e for e in c_ends if e in n_ends][0]

        if c_end == n_ends[0]:
            x, y = n_ends[1]
            gx, gy = goal.ends[0]
        else:
            x, y = n_ends[0]
            gx, gy = goal.ends[0]
        
        heuristics = []
        internal_heuristic = abs(gx-x) + abs(gy-y)
        heuristics += [internal_heuristic]
        hor_tunnel_heuristic = self.map_.map_.hor_tiles - abs(gx-x) + abs(gy-y) if hor_tunnel == True else None
        heuristics += [hor_tunnel_heuristic]
        ver_tunnel_heuristic = abs(gx-x) + self.map_.map_.ver_tiles - abs(gy-y) if ver_tunnel == True else None
        heuristics += [ver_tunnel_heuristic]
        heuristics = [heur for heur in heuristics if heur != None]

        return min(heuristics)

    def copy(self):
        return Pathways(self.adjacencies.copy(), self.targets.copy(), self.map_)