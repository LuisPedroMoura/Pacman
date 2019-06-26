class Node():

    def __init__(self, coordinates, parent):
        
        self.coordinates = coordinates  # initialized on init
        self.parent = parent            # initialized on init
        self.children = []              # updated in Tree().create().expand()

        self.cost = parent.cost + 1     # initialized on init
        self.color = None               

        self.is_crossroad = False       # updated in Tree().create().expand()
        self.is_zombie = False          # updated in Tree().create().analyse()
        self.is_energie = False         # updated in Tree().create().analyse()
        self.is_boost = False           # updated in Tree().create().analyse()
        self.is_ghost = False           # updated in Tree().create().analyse()
        
        self.path_to_zombie = False
        self.path_to_energie = False
        self.path_to_boost = False
        self.path_to_ghost = False


    def add_child(self, child):
        self.children += [child]


    def analyse(self, state):

        if self.coordinates in state['energy']:
            self.is_energy = True
        elif self.coordinates in state['boost']:
            self.is_boost = True
        elif self.coordinates in state['ghosts']:
            for ghost in state.ghosts:
                if self.coordinates == ghost[0]:
                    # ghosts is [coord,zombie,timeout]
                    if ghost[1] == False:
                        self.is_ghost = True
                    elif ghost[1] == True:
                        self.is_zombie = True

    def expand(self, map_, exclusions):

        c = self.coordinates
        left = [c[0]-1, c[1]]
        right = [c[0]+1, c[1]]
        up = [c[0], c[1]+1]
        down = [c[0], c[1]-1]

        possible_children = []

        #!VERIFICAR TUNEIS E QUANDO BATE NA MARGEM DO MAPA
        if map_.is_wall(left):
            possible_children += [left]
        if map_.is_wall(right):
            possible_children += [right]
        if map_.is_wall(up):
            possible_children += [up]
        if map_.is_wall(down):
            possible_children += [down]

        for child in possible_children:
            if child not in exclusions and child != self.parent:
                self.add_child(Node(child,self))

        if len(self.children) > 1:
            self.is_crossroad = True


class Tree():

    def __init__(self, map_, state, root):
        self.map_ = map_
        self.state = state
        self.root = Node(state['pacman'], None)
        self.energies = []
        self.ghosts = []
        self.boosts = []


    def path_to_root(self, node):

        path = [node]
        while node.parent != None:
            path += [node.parent]
            node = node.parent
        
        return path
    

    def closest_crossroad_to_root(self,node):
        
        if node == self.root:
            return 0, node, 0

        crossroad = node if node.is_crossroad else None
        dist_to_node = 0

        while node != self.root:
            node = node.parent
            dist_to_node += 1
            if node.is_crossroad:
                crossroad = node

        return dist_to_node, crossroad, node.cost


    def closest_common_ancestor(self, node1, node2):

        if node1 == node2:
            return node1
        
        found = False
        node1 = node1.parent
        node2 = node2.parent

        while not found:
            
            if node1 == node2:
                found = True

            while len(node1.children) < 2:
                node1 = node1.parent
            
            while len(node2.children) < 2:
                node2 - node2.parent

        return node1


    def create(self):

        self.open_nodes = [self.root]
        self.visited_crossroads = []

        while open_nodes != []:

            node = self.open_nodes.pop()

            node.analyse(self.state)
            if node.is_ghost:
                self.ghosts += [node]
            if node.is_energies:
                self.energies += [node]
            if node.is_boosts:
                self.boosts += [node]

            node.expand_children(self.map_, [self.root]+visited_crossroads)
            if node.is_crossroad:
                visited_crossroads += [node]

            open_nodes += node.children
