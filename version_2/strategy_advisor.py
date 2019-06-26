from game_consts import *
from pacman_tree import PacManNode, PacManTree
from ghost_tree import GhostNode, GhostTree

class StrategyAdvisor():
    """Analyses corridors safety (if contains ghost or not) and crossroads
    semaphores. Advises on a strategy for the given conditions.

    Args:
    map_: instance of Map for the current level
    state: the game state given by the server
    tree: the tree with the map paths and information
    """

    def __init__(self, map_, state, pacman_tree):
        self.debug = False
        self.map_ = map_
        self.state = state
        self.tree = pacman_tree

        self.pacman = self.tree.root
        self.ghosts = self.set_of_nodes(self.tree.ghosts)
        self.zombies = self.set_of_nodes(self.tree.zombies)
        self.energies = self.set_of_nodes(self.tree.energies)
        self.boosts = self.set_of_nodes(self.tree.boosts)
        
        self.ghosts_in_pursuit = []

        

#------------------------------------------------------------------------------# 

    def advise(self):
        self._paint_red()


    def _paint_red(self):

        self.debug_print('STRATEGY ADVISOR: number of ghosts is: '+str(len(self.ghosts)))
        avoid_nodes = []
        self.debug_print('ghosts detected are: '+ str(self.ghosts))
        self.debug_print('ghosts that exist are: '+str(self.state['ghosts']))
        self.debug_print('ghosts considered dangerous are: ')
        for ghost in self.ghosts:

            ghost_in_pursuit = self._ghost_is_in_pursuit(ghost)
            if not ghost_in_pursuit:
                continue

            self.debug_print('\t- '+str(ghost))
            # calculate halfway point in ghosts path to pacman
            halfway = self.tree.last_red_position_above_ghost(ghost)
            self.debug_print('\t- halfway in: '+str(halfway))
            # create tree (ghost is root) with halfway_cost -1 depth
            limit = ghost.cost - halfway.cost + YELLOW_MARGIN +1
            root = GhostNode(ghost.coordinates)
            ghost_tree = GhostTree(self.map_, root, avoid_nodes, limit)
            ghost_tree.create()
            _list = ghost_tree.tree_as_list
            avoid_nodes += _list
            coord_list_yellow1 = [n.coordinates for n in _list if n.cost == limit]
            coord_list_yellow2 = [n.coordinates for n in _list if n.cost == limit-1]
            coord_list_yellow3 = [n.coordinates for n in _list if n.cost == limit-2]
            coord_list_yellow4 = [n.coordinates for n in _list if n.cost == limit-3]
            coord_list_red = [n.coordinates for n in _list if n.cost <= limit-4]

            # paint red the ghost tree in pacman tree
            for pac_node in self.tree.tree_as_list:
                if pac_node.cost < halfway.cost-1 or pac_node.color == COLOR.RED:
                    continue
                if pac_node.coordinates in coord_list_red:
                    pac_node.color = COLOR.RED

            for pac_node in self.tree.tree_as_list:
                if pac_node.coordinates in coord_list_yellow1:
                    pac_node.color = COLOR.YELLOW1
                elif pac_node.coordinates in coord_list_yellow2:
                    pac_node.color = COLOR.YELLOW2
                elif pac_node.coordinates in coord_list_yellow3:
                    pac_node.color = COLOR.YELLOW3
                elif pac_node.coordinates in coord_list_yellow4:
                    pac_node.color = COLOR.YELLOW4


    def _ghost_is_in_pursuit(self, ghost):

        px, py = self.pacman.coordinates
        gx, gy = ghost.coordinates

        internal_hor_heuristic = abs(gx-px)
        internal_ver_heuristic = abs(gy-py)
        internal_heuristic = internal_hor_heuristic + internal_ver_heuristic

        hor_tunnel_hor_heuristic = self.map_.map_.hor_tiles - abs(gx-px) if self.tree.hor_tunnel_exists else None
        hor_tunnel_ver_heuristic = abs(gy-py) if self.tree.hor_tunnel_exists else None
        
        ver_tunnel_hor_heuristic = abs(gx-px) if self.tree.ver_tunnel_exists else None
        ver_tunnel_ver_heuristic = self.map_.map_.ver_tiles - abs(gy-py) if self.tree.ver_tunnel_exists else None
        
        
        if hor_tunnel_hor_heuristic != None:
            hor_tunnel_heuristic = hor_tunnel_hor_heuristic + hor_tunnel_ver_heuristic
        else:
            hor_tunnel_heuristic = 1000 # will not be considered

        if ver_tunnel_hor_heuristic != None:
            ver_tunnel_heuristic = ver_tunnel_hor_heuristic + ver_tunnel_ver_heuristic
        else:
            ver_tunnel_heuristic = 1000 # will not be considered


        if internal_heuristic < hor_tunnel_heuristic and internal_heuristic < ver_tunnel_heuristic:
            dx = internal_hor_heuristic
            dy = internal_ver_heuristic

        if hor_tunnel_heuristic < internal_heuristic and hor_tunnel_heuristic < ver_tunnel_heuristic:
            dx = hor_tunnel_hor_heuristic
            dy = hor_tunnel_ver_heuristic

        if ver_tunnel_heuristic < hor_tunnel_heuristic and ver_tunnel_heuristic < internal_heuristic:
            dx = ver_tunnel_hor_heuristic
            dy = ver_tunnel_ver_heuristic

        if (dx <= SAFE_DIST_TO_GHOST and dy <= SAFE_DIST_TO_GHOST) and ghost.cost <= 1.5*SAFE_DIST_TO_GHOST:
            self.ghosts_in_pursuit += [ghost]
            return True
        
        return False


    def set_of_nodes(self, nodes):
        coordinates = [node.coordinates for node in nodes]
        set_coordinates = []
        for coord in coordinates:
            if coord not in set_coordinates:
                set_coordinates += [coord]
        
        _set = []
        for coord in set_coordinates:
            _nodes = [n for n in nodes if n.coordinates == coord]
            node = sorted(_nodes, key=lambda n: n.cost)[0]
            _set += [node]
        
        return _set


    def debug_print(self, string, boolean=True):
        if self.debug and boolean:
            print(string)
