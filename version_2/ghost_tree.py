from generic_tree import GenericNode, GenericTree


class GhostNode(GenericNode):

    def __init__(self, coordinates, parent=None):

        super(GhostNode, self).__init__(parent, cost=1)
        self.coordinates = coordinates  # initialized on init

    # Node analysis and expansion ----------------------------------------------
    def analyse(self, state):
        pass

    def expand(self, map_, exclusions, limit):

        if self.cost > limit:
            raise Exception('limit was reached')

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
        if c[0] == map_.hor_tiles-1 and not map_.is_wall([0, c[1]]):
            possible_children += [[0, c[1]]]
        if c[1] == 0 and not map_.is_wall([c[0], map_.ver_tiles-1]):
            possible_children += [[c[0], map_.ver_tiles-1]]
        if c[1] == map_.ver_tiles-1 and not map_.is_wall([c[0], 0]):
            possible_children += [[c[0], 0]]
        
        for child in possible_children:
            if self.parent != None:
                if child not in [e.coordinates for e in exclusions] and child != self.parent.coordinates:
                    self.add_child(GhostNode(child,self))
            else:
                if child not in [e.coordinates for e in exclusions]:
                    self.add_child(GhostNode(child,self))

        if len(self.children) > 1:
            self.is_crossroad = True

class GhostTree(GenericTree):

    def __init__(self, map_, root, visited_nodes, limit):
        super(GhostTree, self).__init__(root)
        self.map_ = map_
        self.root = root
        self.visited_nodes = visited_nodes
        self.limit = limit
        self.tree_as_list = [self.root]

    def create(self):

        open_nodes = [self.root]
        self.visited_nodes = [self.root]
        
        while open_nodes != []:

            node = open_nodes.pop(0)
            
            try:
                node.expand(self.map_, exclusions=self.visited_nodes, limit=self.limit)
                self.tree_as_list.extend(node.children)
                open_nodes.extend(node.children)
                self.visited_nodes.extend(node.children)
                self.size += len(node.children)
            except:
                continue
