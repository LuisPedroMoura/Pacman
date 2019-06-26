import time
from game_consts import *
from generic_tree import GenericNode, GenericTree


class PacManNode(GenericNode):

    def __init__(self, coordinates, parent=None):

        super(PacManNode, self).__init__(parent, cost=1)
        self.coordinates = coordinates  # initialized on init
        self.color = COLOR.GREEN

        self.dist_to_pacman = self.cost - 1

        self.is_crossroad = False       # updated in Tree().create().expand()
        self.is_zombie = False          # updated in Tree().create().analyse()
        self.is_energy = False         # updated in Tree().create().analyse()
        self.is_boost = False           # updated in Tree().create().analyse()
        self.is_ghost = False           # updated in Tree().create().analyse()
        self.is_hor_tunnel = False
        self.is_ver_tunnel = False

        self.dist_to_red_above = 0

        self.timeout = 0


    # Node analysis and expansion ----------------------------------------------
    def analyse(self, state):

        if self.coordinates in [g[0] for g in state['ghosts']]:
            for ghost in state['ghosts']:
                if self.coordinates == ghost[0]:
                    # ghosts is [coord,zombie,timeout]
                    if ghost[1] == False:
                        self.is_ghost = True
                    elif ghost[1] == True:
                        self.is_zombie = True
                        self.timeout = ghost[2]
        elif self.coordinates in state['energy']:
            self.is_energy = True
        elif self.coordinates in state['boost']:
            self.is_boost = True
        

    def expand(self, map_, exclusions):

        c = self.coordinates
        left = [c[0]-1, c[1]]
        right = [c[0]+1, c[1]]
        up = [c[0], c[1]-1]
        down = [c[0], c[1]+1]

        possible_children = []

        if left[0] >= 0 and not map_.is_wall(left):
            possible_children += [left]
        if right[0] <= map_.hor_tiles and not map_.is_wall(right):
            possible_children += [right]
        if up[1] >= 0 and not map_.is_wall(up):
            possible_children += [up]
        if down[1] <= map_.ver_tiles and not map_.is_wall(down):
            possible_children += [down]

        if c[0] == 0 and not map_.is_wall([map_.hor_tiles-1, c[1]]):
            possible_children += [[map_.hor_tiles-1, c[1]]]
            self.is_hor_tunnel = True
        if c[0] == map_.hor_tiles-1 and not map_.is_wall([0, c[1]]):
            possible_children += [[0, c[1]]]
            self.is_hor_tunnel = True
        if c[1] == 0 and not map_.is_wall([c[0], map_.ver_tiles-1]):
            possible_children += [[c[0], map_.ver_tiles-1]]
            self.is_ver_tunnel = True
        if c[1] == map_.ver_tiles-1 and not map_.is_wall([c[0], 0]):
            possible_children += [[c[0], 0]]
            self.is_ver_tunnel = True

        
        for child in possible_children:
            if self.parent != None:
                if child not in [e.coordinates for e in exclusions] and child != self.parent.coordinates:
                    self.add_child(PacManNode(child,self))
            else:
                if child not in [e.coordinates for e in exclusions]:
                    self.add_child(PacManNode(child,self))

        if len(self.children) > 1:
            self.is_crossroad = True
    
    # standard class methods ---------------------------------------------------
    def equals(self, node):
        if node == None:
            return False
        return self.coordinates == node.coordinates

    def __str__(self):
        
        string = ""

        if self.color == COLOR.RED:
            string += 'R_'
        elif self.color == COLOR.YELLOW1 or self.color == COLOR.YELLOW2 \
          or self.color == COLOR.YELLOW3 or self.color == COLOR.YELLOW4:
            string += 'Y_'
        else:
            string += 'G_'

        if self.is_zombie:
            string += 'Zombie(' + str(self.coordinates) + ')'
        elif self.is_ghost:
            string += 'Ghost(' + str(self.coordinates) + '), with cost: '+str(self.cost)
        elif self.is_energy:
            string += 'Energy(' + str(self.coordinates) + ')'
        elif self.is_boost:
            string += 'Boost(' + str(self.coordinates) + ')'
        else:
            string += str(self.coordinates)
        
        return string

    def __repr__(self):
        return self.__str__()


class PacManTree(GenericTree):

    def __init__(self, map_, state, root, max_calc_time):

        super(PacManTree, self).__init__(root)
        self.map_ = map_
        self.state = state
        self.max_calc_time = max_calc_time
        self.energies = []
        self.ghosts = []
        self.zombies = []
        self.boosts = []
        self.map_width = self.map_.hor_tiles
        self.map_height = self.map_.ver_tiles
        self.hor_tunnel_exists = False
        self.ver_tunnel_exists = False
        self.tree_as_list = [self.root]

        self.debug = False
        

    def create(self):

        open_nodes = [self.root]
        visited_nodes = [self.root]
        #visited_once_coordinates = []
        
        start = time.time()
        cur_time = 0
        self.debug_print('#########################################################')
        self.debug_print('STARTING TO CREATE TREE')
        self.debug_print('#########################################################')
        self.debug_print('Root/Pac-Man is: '+str(self.root))
        while cur_time <= self.max_calc_time and self.size <= MAX_PACMAN_TREE_SIZE \
                and open_nodes != []:

            node = open_nodes.pop(0)
            
            node.analyse(self.state)
            self.debug_print('\nPopped node: '+str(node))

            if node.is_energy:
                self.energies += [node]

            elif node.is_ghost:
                if node.coordinates in [n.coordinates for n in self.ghosts]:
                    cur_time = (time.time() - start) * 1000
                    continue 
                self.ghosts += [node]
                    
            elif node.is_zombie:
                self.zombies += [node]

            elif node.is_boost:
                self.boosts += [node]

            
            if node.is_hor_tunnel:
                self.hor_tunnel_exists = True
            elif node.is_ver_tunnel:
                self.ver_tunnel_exists = True

            try:
                node.expand(self.map_, exclusions=visited_nodes)
                self.tree_as_list.extend(node.children)
                open_nodes.extend(node.children)
                # for child in node.children:
                #     if child.coordinates in visited_once_coordinates:
                #         visited_nodes += [child]
                #     else:
                #         visited_once_coordinates += [child.coordinates]
                #self.visited_nodes.extend(node.children)
                self.size += len(node.children)
                self.debug_print('Children are: '+str(node.children))
            except:
                cur_time = (time.time() - start) * 1000
                continue
            cur_time = (time.time() - start) * 1000
          

    def path_to_pacman(self, node):
        return self.path_to_root(node)

    # def closest_crossroad_from_pacman(self, node):
    #     return self.closest_crossroad_to_root_in_path(node)

    def last_red_position_above_ghost(self, node):

        if not node.is_ghost:
            return None
        
        halfway = (node.cost // 2) + 1
        
        while node.cost != halfway:
            node = node.parent

        return node

    def pacman_crossroads(self):
        return self.closest_crossroads_below(self.root)

    def crossroads_below(self, node):
        return self.closest_crossroads_below(node)

# str, repr and print ---------------------------------------------------------=
    def __str__(self):
        pass

    def __repr__(self):
        pass

    def print(self, advisor):

        array = [[[] for x in range(self.map_height)] for y in range(self.map_width)]
        _list = [(n.coordinates, n.color) for n in self.tree_as_list]

        zombies = advisor.zombies
        energies = advisor.energies
        ghosts = advisor.ghosts
        boosts = advisor.boosts

        for pos in _list:
            x,y = pos[0]
            array[x][y] = pos[1]

        x,y = self.root.coordinates
        array[x][y] = COLOR.PACMAN

        for ghost in ghosts:
            x,y = ghost.coordinates
            array[x][y] = COLOR.GHOST

        for zombie in zombies:
            x,y = zombie.coordinates
            array[x][y] = COLOR.ZOMBIE

        for energy in energies:
            x,y = energy.coordinates
            if array[x][y] == COLOR.RED:
                array[x][y] = COLOR.ENERGY_RED
            elif array[x][y] == COLOR.GREEN:
                array[x][y] = COLOR.ENERGY_GREEN
            elif array[x][y] == COLOR.YELLOW1 or array[x][y] == COLOR.YELLOW2 \
              or array[x][y] == COLOR.YELLOW3 or array[x][y] == COLOR.YELLOW4:
                array[x][y] = COLOR.ENERGY_YELLOW

        for boost in boosts:
            x,y = boost.coordinates
            if array[x][y] == COLOR.RED:
                array[x][y] = COLOR.BOOST_RED
            elif array[x][y] == COLOR.GREEN:
                array[x][y] = COLOR.BOOST_GREEN

        for j in range(self.map_height):
            for i in range(self.map_width):
                color = array[i][j]
                if color == COLOR.GREEN:
                    print("\033[1;32;42m  ", end="")
                elif color == COLOR.ENERGY_GREEN:
                    print("\033[1;32;42m⊙ ", end="")

                elif color == COLOR.RED:
                    print("\033[1;31;41m  ", end="")
                elif color == COLOR.ENERGY_RED:
                    print("\033[1;31;41m⊙ ", end="")

                elif color == COLOR.YELLOW1 or color == COLOR.YELLOW2 \
                  or color == COLOR.YELLOW3 or color == COLOR.YELLOW4:
                    print("\033[1;33;43m  ", end="")
                elif color == COLOR.ENERGY_YELLOW:
                    print("\033[1;33;43m⊙ ", end="")
                
                elif color == COLOR.PACMAN:
                    print("\033[1;34;44m00", end="")
                elif color == COLOR.GHOST or color == COLOR.ZOMBIE:
                    print("\033[1;35;45mXX", end="")
                elif color == COLOR.BOOST_RED:
                    print("\033[1;31;41mⒷ ", end="")
                elif color == COLOR.BOOST_GREEN:
                    print("\033[1;32;42mⒷ ", end="")

                elif color == COLOR.BLACK:
                    print("\033[1;30;40m  ", end="")
                elif color == COLOR.ENERGY_BLACK:
                    print("\033[1;37;40m⊙ ", end="")

                else:
                    print("\033[1;37;47m  ", end="")
            print("\033[1;30;40m  ")


    def debug_print(self, string, boolean=True):
        if self.debug and boolean:
            print(string)