from abc import ABC, abstractmethod
from game_consts import *
from corridor import Corridor
# DOMAIN ----------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Dominios de pesquisa. Permitem calcular as accoes possiveis em cada estado
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal_state):
        pass


# PROBLEM ---------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Problemas concretos a resolver dentro de um determinado dominio
class SearchProblem:
    """
        Args:
        domain: problem's SearchDomain
        initial: tupple with initial corridor and initial position in the corridor
        goal: tupple with goal corridor and goal position in the corridor (goal will be where pacman is)

        Attr:
        domain: problem's SearchDomain
        initial_corr: initial corridor
        initial_pos: initial position in the corridor
        goal_corr: goal corridor
        goal_pos: goal position in the corridor
        """

    
    def __init__(self, domain, initial_corr, initial_pos, goal_corr, goal_pos, map_, state):
        
        self.domain = domain.copy() #so we can change the domain as we wish
        self.initial_corr = initial_corr
        self.initial_pos = initial_pos
        self.goal_corr = goal_corr
        self.goal_pos = goal_pos
        self.state = state
        self.map_ = map_

        self.initial = Corridor([self.initial_pos])
        
        sub_init0, sub_init1 = self.initial_corr.sub_corridors(self.initial_pos)
        if any([g[0] in sub_init0.coordinates for g in state['ghosts'] if g[1] == False]):
            sub_init0.safe = CORRIDOR_SAFETY.UNSAFE
        if any([g[0] in sub_init1.coordinates for g in state['ghosts'] if g[1] == False]):
            sub_init1.safe = CORRIDOR_SAFETY.UNSAFE
        self.update_domain(self.initial_corr, self.initial, sub_init0, sub_init1)

        if goal_pos in sub_init0.coordinates:
            self.goal_corr = sub_init0
        elif goal_pos in sub_init1.coordinates:
            self.goal_corr = sub_init1

        self.goal = Corridor([self.goal_pos])

        sub_goal0, sub_goal1 = self.goal_corr.sub_corridors(self.goal_pos)
        if any([g[0] in sub_goal0.coordinates for g in state['ghosts'] if g[1] == False]):
            sub_goal0.safe = CORRIDOR_SAFETY.UNSAFE
        if any([g[0] in sub_goal1.coordinates for g in state['ghosts'] if g[1] == False]):
            sub_goal1.safe = CORRIDOR_SAFETY.UNSAFE
        self.update_domain(self.goal_corr, self.goal, sub_goal0, sub_goal1)


    def update_domain(self, corridor, sub_corr, sub_corr0, sub_corr1):
        
        new_adjacencies = []

        if corridor.coordinates != sub_corr0.coordinates and corridor.coordinates != sub_corr1.coordinates:

            for [corrA, corrB] in self.domain.adjacencies:
                
                
                if corridor.coordinates == corrA.coordinates:
                    if any(e in sub_corr0.ends for e in corrB.ends):
                        new_adjacencies += [[sub_corr0, corrB]]
                    elif any(e in sub_corr1.ends for e in corrB.ends):
                        new_adjacencies += [[sub_corr1, corrB]]
                    
                elif corridor.coordinates == corrB.coordinates:                
                    if any(e in sub_corr0.ends for e in corrA.ends):
                        new_adjacencies += [[sub_corr0, corrA]]
                    elif any(e in sub_corr1.ends for e in corrA.ends):
                        new_adjacencies += [[sub_corr1, corrA]]

            # eliminar das adjacencias o corredor inicial que foi dividido e j'a nao existe inteiro
            
            self.domain.adjacencies = [[A,B] for [A, B] in self.domain.adjacencies if (corridor != A and corridor != B)]
            self.domain.adjacencies += new_adjacencies

        else:
            for [corrA, corrB] in self.domain.adjacencies:

                if sub_corr0.coordinates == sub_corr.coordinates:
                    
                    if corridor.coordinates == corrA.coordinates:
                        if any(e in sub_corr.ends for e in corrB.ends):
                            new_adjacencies += [[sub_corr, corrB]]
                        elif any(e in sub_corr1.ends for e in corrB.ends):
                            new_adjacencies += [[sub_corr1, corrB]]
                        
                    elif corridor.coordinates == corrB.coordinates:                
                        if any(e in sub_corr.ends for e in corrA.ends):
                            new_adjacencies += [[sub_corr, corrA]]
                        elif any(e in sub_corr1.ends for e in corrA.ends):
                            new_adjacencies += [[sub_corr1, corrA]]

                if sub_corr1.coordinates == sub_corr.coordinates:
                    
                    if corridor.coordinates == corrA.coordinates:
                        if any(e in sub_corr.ends for e in corrB.ends):
                            new_adjacencies += [[sub_corr, corrB]]
                        elif any(e in sub_corr0.ends for e in corrB.ends):
                            new_adjacencies += [[sub_corr0, corrB]]
                        
                    elif corridor.coordinates == corrB.coordinates:                
                        if any(e in sub_corr.ends for e in corrA.ends):
                            new_adjacencies += [[sub_corr, corrA]]
                        elif any(e in sub_corr0.ends for e in corrA.ends):
                            new_adjacencies += [[sub_corr0, corrA]]

            self.domain.adjacencies = [[A,B] for [A, B] in self.domain.adjacencies if (corridor != A and corridor != B)]
            self.domain.adjacencies += new_adjacencies


        if sub_corr.coordinates != sub_corr0.coordinates:
            self.domain.adjacencies += [[sub_corr, sub_corr0]]
        if sub_corr.coordinates != sub_corr1.coordinates:
            self.domain.adjacencies += [[sub_corr, sub_corr1]]
    
    def goal_test(self, state):
        return all([ coord in self.goal.coordinates for coord in state.coordinates])
        
        

# NODE ------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Nos de uma arvore de pesquisa
class SearchNode:
   
    def __init__(self, state, parent, cost, heuristic): 
        self.state = state #corridor
        self.parent = parent #SearchNode
        self.cost = cost
        self.heuristic = heuristic
        
    def inParent(self, state):
        if self.parent == None:
            return False
        if self.parent.state == state:
            return True
        return self.parent.inParent(state)
    
    def __str__(self):
        return "no(" + str(self.state) +  ")" # "," + str(self.parent) +
    
    def __repr__(self):
        return str(self)



# TREE ------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Arvores de pesquisa
class SearchTree:
    
    def __init__(self, problem, strategy='a*'): 
        
        self.problem = problem
        heur = abs(self.problem.goal.ends[0][0]-self.problem.initial.ends[0][0]) \
               + abs(self.problem.goal.ends[0][1]-self.problem.initial.ends[0][1])   
        root = SearchNode(self.problem.initial, parent=None, cost=0, heuristic=heur)
        self.open_nodes = [root]
        self.strategy = strategy
        self.lvisited = [root.state]
        self.cost = None


    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)


    # procurar a solucao
    def search(self):

        while self.open_nodes != []:
     
            node = self.open_nodes.pop()

            if self.problem.goal_test(node.state):
                self.cost = node.cost

                if node.parent != None:
                    if node.parent.state.ends[0] in node.state.ends:
                        return node.parent.state.coordinates[1], self.cost, self.get_path(node)
                    elif node.parent.state.ends[1] in node.state.ends:
                        return node.parent.state.coordinates[-2], self.cost, self.get_path(node)
                return None

            lnewnodes = []
            for action in self.problem.domain.actions(node.state):

                new_state = self.problem.domain.result(node.state, action)

                if new_state in self.lvisited:
                    pass
                else:
                    # calculate cost of next node
                    cost = node.cost + self.problem.domain.cost(node.state, action)
                    # calculate heuristic of next node
                    heuristic = self.problem.domain.heuristic(curr_state=node.state, \
                                                              new_state=new_state, \
                                                              goal=self.problem.goal, \
                                                              hor_tunnel=self.problem.map_.hor_tunnel_exists, \
                                                              ver_tunnel=self.problem.map_.ver_tunnel_exists)
                    # create new node
                    new_node = SearchNode(state=new_state, parent=node, cost=cost, heuristic=heuristic)
                    
                    # add new node to list of new nodes
                    lnewnodes += [new_node]

            lnewnodes = [ newNode for newNode in lnewnodes \
                                    if newNode.state not in self.lvisited ]

            self.add_to_open(lnewnodes)
            self.lvisited.extend(node.state for node in lnewnodes)

        return None


    # procurar todos os caminhos para a solucao
    def all_path_search(self, avoid_coordinates):
        # print()
        # print('TREE SEARCH - NEW SEARCH')
        # print('avoid_coordinates are ' + str(avoid_coordinates))
        # print('goal is ' + str(self.problem.goal))
        all_paths = []
        
        while self.open_nodes != []:
            # print('TREE SEARCH: open nodes: ' + str(self.open_nodes))
            node = self.open_nodes.pop()
            
            if self.problem.goal_test(node.state):
                if node.parent != None:
                    path = self.get_path(node)
                    if path[1].ends[0] in self.problem.initial.coordinates:
                        all_paths += [ (path[1].coordinates[1], node.cost, path) ]
                    
                    elif path[1].ends[1] in self.problem.initial.coordinates:
                        all_paths += [ (path[1].coordinates[-2], node.cost, path) ]

                    if len(all_paths) == 1:
                        #print('TREE SEARCH: returning because number of searches were completed')
                        return sorted(all_paths, key=lambda move: move[1])

            lnewnodes = []
            # print('TREE SEARCH actions: ' + str(self.problem.domain.actions(node.state)))
            for action in self.problem.domain.actions(node.state):

                new_state = self.problem.domain.result(node.state, action)
                
                #if starting point is found, does nothing and continue to another iteration
                if new_state == None or self.problem.initial == None:
                    raise ValueError
                    
                if all([c in self.problem.initial.coordinates for c in new_state.coordinates]):
                    continue

                elif avoid_coordinates != []:

                    if all([av not in self.problem.goal.coordinates for av in avoid_coordinates]):

                        if any([av in new_state.coordinates for av in avoid_coordinates]):
                            continue
                    elif any([av in self.problem.goal.coordinates for av in avoid_coordinates]):
                        if any([av in new_state.coordinates for av in avoid_coordinates]):
                            if self.problem.initial.coordinates[0] in new_state.coordinates:
                                continue

                elif new_state in self.lvisited:
                    continue
                
                cost = node.cost + self.problem.domain.cost(node.state, action)
                heuristic = self.problem.domain.heuristic(curr_state=node.state, \
                                                            new_state=new_state, \
                                                            goal=self.problem.goal, \
                                                            hor_tunnel=self.problem.map_.hor_tunnel_exists, \
                                                            ver_tunnel=self.problem.map_.ver_tunnel_exists)
                # create new node
                new_node = SearchNode(state=new_state, parent=node, cost=cost, heuristic=heuristic)
                # add new node to list of new nodes
                lnewnodes += [new_node]
                lnewnodes = [ newNode for newNode in lnewnodes \
                                if newNode.state not in self.lvisited ]

            self.add_to_open(lnewnodes)
            self.lvisited.extend(node.state for node in lnewnodes)

        return sorted(all_paths, key=lambda move: move[1])


    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node: node.heuristic + node.cost, reverse=True)
        elif self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[0:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node : node.cost)
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes = sorted(self.open_nodes, key=lambda node: node.heuristic)