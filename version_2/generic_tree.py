class GenericNode():

    def __init__(self, parent, cost):

        self.parent = parent            # initialized on init
        self.children = []              # updated in Tree().create().expand()

        self.cost = self.calculate_cost(cost)     # initialized on init
        self.color = None
        

    def calculate_cost(self,cost):
        return (self.parent.cost if self.parent != None else 0) + cost

    def has_children(self):
        return len(self.children) > 0

    def add_child(self, child):
        self.children += [child]

    def paint(self, color):
        self.color = color

    def expand(self, map_, exclusions):
        pass



class GenericTree():

    def __init__(self, root):

        self.root = root
        self.size = 1


    def path_to_root(self, node):

        path = [node]
        while node.parent != None:
            path += [node.parent]
            node = node.parent
        
        return path
    

    # def closest_crossroad_to_node_in_path(self,node):

    #     while node != self.root:
    #         if node.is_crossroad:
    #             return node
    #         node = node.parent
            
    #     return None

    # def closest_crossroad_to_root_in_path(self,node):

    #     crossroad = node if node.is_crossroad else None

    #     while node != self.root:
    #         if node.is_crossroad:
    #             crossroad = node
    #         node = node.parent
            
    #     return crossroad

    def closest_crossroads_below(self, node):

        crossroads = []

        for child in node.children:
            
            while child.children != []:
                
                if len(child.children) > 1:
                    crossroads += [child]
                    break
                else:
                    child = child.children[0]

        return crossroads


    # def closest_common_ancestor(self, node1, node2):

    #     if node1 == node2:
    #         return node1
        
    #     found = False
    #     node1 = node1.parent
    #     node2 = node2.parent

    #     while not found:
            
    #         if node1 == node2:
    #             found = True

    #         while len(node1.children) < 2:
    #             node1 = node1.parent
            
    #         while len(node2.children) < 2:
    #             node2 - node2.parent

    #     return node1


    # def interseption_node(self, path, node):

    #     while node != self.root:
    #         if node in path:
    #             return node
    #         node = node.parent
        
    #     return None
        

    # def propagate_downward(self, node, function):

    #     function(node)

    #     if not node.has_children:
    #         return
        
    #     for child in node.children:
    #         return self.propagate_downward(child, function)


    # def propagate_upward(self, node, stop_node, function):

    #     if node == stop_node:
    #         return

    #     function(node)

    #     if node.parent == None:
    #         return

    #     self.propagate_upward(node.parent, stop_node, function)


    def tree_to_list(self):
        _list = []