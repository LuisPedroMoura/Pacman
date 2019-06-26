from game_consts import *
from ghost_tree import GhostNode, GhostTree
from move import Move

class StrategyAnalyst:
    """Creates the Strategy Analist, which coordinates the possible moves given
    by the Pursuit, Eating, Counter and Flight Agents and chooses the best Pac-Man
    next move overall

    Attr:
    advisor: provides extensive information about the current situation of the map
    """

    def __init__(self, advisor):
        self.debug = False
        self.advisor = advisor
        self.possible_moves = []

        
    
    def decide(self):
        """ Main method of the StrategyAnalyst class, which goal is to verify 
        current game condition and call, accordingly, for advice in the next
        Pac-Man's move from the Execution Agents. Relies on MoveRiskAssessor to
        validate Execution Agents advices.

        Returns:
        The next advised position for Pac-Man to go to
        """

        #self.repaint_green()

        # always tries to pursue ghosts first
        move = self._try_pursuit()
        if move != None:
            #self.paint_yellow(move, True)
            self.paint_move(move)
            self.debug_print('Pacman: '+str(self.advisor.pacman))
            self.debug_print('Target: '+str(move.target))
            self.debug_print('Move  : '+str(move))
            return move.next_node

        if len(self.advisor.ghosts_in_pursuit) >= NUMBER_OF_GHOST_TO_OFFENSIVE:
            move = self._try_counter()
            if move != None:
                #self.paint_yellow(move, True)
                self.paint_move(move)
                self.debug_print('Pacman: '+str(self.advisor.pacman))
                self.debug_print('Target: '+str(move.target))
                self.debug_print('Move  : '+str(move))
                return move.next_node

            move = self._try_eating()
            if move != None:
                #self.paint_yellow(move, True)
                self.paint_move(move)
                self.debug_print('Pacman: '+str(self.advisor.pacman))
                self.debug_print('Target: '+str(move.target))
                self.debug_print('Move  : '+str(move))
                self.debug_print("")
                return move.next_node

        else:
            move = self._try_eating()
            if move != None:
                #self.paint_yellow(move, True)
                self.paint_move(move)
                self.debug_print('Pacman: '+str(self.advisor.pacman))
                self.debug_print('Target: '+str(move.target))
                self.debug_print('Move  : '+str(move))
                self.debug_print("")
                return move.next_node
            
            move = self._try_counter()
            if move != None:
                #self.paint_yellow(move, True)
                self.paint_move(move)
                self.debug_print('Pacman: '+str(self.advisor.pacman))
                self.debug_print('Target: '+str(move.target))
                self.debug_print('Move  : '+str(move))
                self.debug_print("")
                return move.next_node
        
        move = self._try_flight()
        if move != None:
            #self.paint_yellow(move, True)
            self.paint_move(move)
            self.debug_print('Pacman: '+str(self.advisor.pacman))
            self.debug_print('Target: '+str(move.target))
            self.debug_print('Move  : '+str(move))
            self.debug_print("")
            return move.next_node
        
        
        # no strategy available, time to panic! Goes for the first safe corridor
        # move = self._panic()

        # ----- no agent got a move - this should never happen
        if move == None:
            return None

        return move.next_node



    def _try_pursuit(self):
        self.debug_print('PURSUIT MODE')
        targets = self.advisor.zombies
        #! verify that zombies ghosts are not in the den, if they are, don't pursue
        #! have an idea to make this happen
        if targets != []:
            self.possible_moves = [Move(target, target.cost, self.advisor.tree.path_to_pacman(target)) for target in targets]
            self.possible_moves = [move for move in self.possible_moves if move.cost <= move.target.timeout * GHOST_PURSUIT_MULTIPLIER]
            self.possible_moves = self.filter_haunted_moves(self.possible_moves)
            if self.possible_moves != []:
                for move in self.possible_moves:
                    #self.paint_yellow(move, False)
                    move.danger_cost = self.calculate_danger_cost(move)
                    #self.repaint_green()
                self.possible_moves = sorted(self.possible_moves, key=lambda m: m.danger_cost)
                #self.debug_print('Pursuer Moves: '+str(self.possible_moves), len(self.possible_moves) > 0)
                return self.possible_moves[0]
        return None

    def _try_eating(self):
        self.debug_print('EATING MODE')
        targets = self.advisor.energies
        if len(targets) < 50:
            targets += self.advisor.boosts
        if targets != []:
            targets = targets[:MAX_MOVE_SELECT_ON_EATING_MODE]
            self.possible_moves = [Move(target, target.cost, self.advisor.tree.path_to_pacman(target)) for target in targets]
            self.possible_moves = self.filter_haunted_moves(self.possible_moves)
            if self.possible_moves != []:
                for move in self.possible_moves:
                    #self.paint_yellow(move, False)
                    move.danger_cost = self.calculate_danger_cost(move)
                    #self.repaint_green()
                self.possible_moves = sorted(self.possible_moves, key=lambda m: m.danger_cost)
                #self.debug_print('Eater Moves: '+str(self.possible_moves), len(self.possible_moves) > 0)
                return self.possible_moves[0]
        return None
    
    def _try_counter(self):
        self.debug_print('COUNTER MODE')
        targets = self.advisor.boosts
        if targets != []:
            self.possible_moves = [Move(target, target.cost, self.advisor.tree.path_to_pacman(target)) for target in targets]
            self.possible_moves = self.filter_haunted_moves(self.possible_moves)
            if self.possible_moves != []:
                for move in self.possible_moves:
                    #self.paint_yellow(move, False)
                    move.danger_cost = self.calculate_danger_cost(move)
                    #self.repaint_green()
                self.possible_moves = sorted(self.possible_moves, key=lambda m: m.danger_cost)
                #self.debug_print('Counter Moves: '+str(self.possible_moves), len(self.possible_moves) > 0)
                return self.possible_moves[0]
        return None

    def _try_flight(self):
        self.debug_print('FLIGHT MODE')

        map_middle_x = self.advisor.map_.hor_tiles // 2
        map_middle_y = self.advisor.map_.ver_tiles // 2
        target = None

        if self.advisor.pacman.coordinates[0] < map_middle_x:
            if self.advisor.pacman.coordinates[1] < map_middle_y:
                for node in self.advisor.tree.tree_as_list:
                    if node.coordinates[0] > map_middle_x and node.coordinates[1] > map_middle_y:
                        target = node
            else:
                for node in self.advisor.tree.tree_as_list:
                    if node.coordinates[0] > map_middle_x and node.coordinates[1] < map_middle_y:
                        target = node
        else:
            if self.advisor.pacman.coordinates[1] < map_middle_y:
                for node in self.advisor.tree.tree_as_list:
                    if node.coordinates[0] < map_middle_x and node.coordinates[1] > map_middle_y:
                        target = node
            else:
                for node in self.advisor.tree.tree_as_list:
                    if node.coordinates[0] < map_middle_x and node.coordinates[1] < map_middle_y:
                        target = node

        if target != None:
            targets = [node for node in self.advisor.tree.tree_as_list if node.coordinates == target.coordinates]
            targets = targets[:MAX_MOVE_SELECT_ON_EATING_MODE//2]
            self.possible_moves = [Move(target, target.cost, self.advisor.tree.path_to_pacman(target)) for target in targets]
            self.possible_moves = self.filter_haunted_moves(self.possible_moves)
            if self.possible_moves != []:
                for move in self.possible_moves:
                    #self.paint_yellow(move, False)
                    move.danger_cost = self.calculate_danger_cost(move)
                    #self.repaint_green()
                self.possible_moves = sorted(self.possible_moves, key=lambda m: m.danger_cost)
                #self.debug_print('Fleer Moves: '+str(self.possible_moves), len(self.possible_moves) > 0)
                return self.possible_moves[0]
        else:
            pac_children = self.advisor.pacman.children
            red_dist = 0
            target = pac_children[0]
            for child in pac_children:
                open_nodes = [child]
                while open_nodes != []:
                    node = open_nodes.pop(0)
                    if node.color == COLOR.RED:
                        if node.cost > red_dist:
                            red_dist = node.cost
                            target = node.parent
                        break
                    open_nodes.extend(node.children)
            move = Move(target, target.cost, self.advisor.tree.path_to_pacman(target))
            move.danger_cost = self.calculate_danger_cost(move)
            return move


    def filter_haunted_moves(self, moves):
        return [move for move in moves if not any([node.is_ghost for node in move.path_to_target])]


    # PREVIOUS DYNAMIC YELLOW CALCULATION - TOO HEAVY PROCESSING - GREAT RESULTS THOUGH
    # def paint_yellow(self, move, print_bool=False):
    #     #self.debug_print('STRATEGY ANALYST: paint_yellow(): ghosts are: '+str(self.advisor.ghosts), print_bool)
    #     avoid_nodes = []
    #     for ghost in self.advisor.ghosts:

    #         if ghost.coordinates not in [g.coordinates for g in self.advisor.ghosts_in_pursuit]:
    #             continue

    #         #self.debug_print('\t- '+str(ghost))
    #         # calculate halfway point in ghosts path to pacman
    #         #self.debug_print('\t- ghost is: '+str(ghost), print_bool)
    #         halfway = self.advisor.tree.last_red_position_above_ghost(ghost)
    #         #self.debug_print('\t- halfway in: '+str(halfway)+' with cost '+str(halfway.cost), print_bool)
    #         yellow_limit = halfway.cost - len(move.path_to_target)
    #         #self.debug_print('\t- yellow limit is: '+str(yellow_limit), print_bool)
    #         # create tree (ghost is root) with halfway_cost -1 depth
    #         limit = ghost.cost - yellow_limit -1
    #         #self.debug_print('\t- limit is: '+str(limit), print_bool)

    #         root = GhostNode(ghost.coordinates)
    #         ghost_tree = GhostTree(self.advisor.map_, root, avoid_nodes, limit)
    #         ghost_tree.create()
    #         _list = ghost_tree.tree_as_list
    #         avoid_nodes += _list
    #         coord_list = [n.coordinates for n in _list if n.cost >= halfway.cost]

    #         # paint yellow the ghost tree in pacman tree
    #         yellow_margin = halfway.cost + yellow_limit+1
    #         for pac_node in self.advisor.tree.tree_as_list:
    #             if pac_node.color == COLOR.RED:
    #                 continue
    #             # if pac_node.cost < yellow_margin:
    #             #     continue
    #             if pac_node.coordinates in coord_list:
    #                 pac_node.color = COLOR.YELLOW


    def repaint_green(self):
        open_nodes = [self.advisor.tree.root]
        while open_nodes != []:
            node = open_nodes.pop(0)
            if node.color == COLOR.RED:
                continue
            node.color = COLOR.GREEN


    def paint_move(self, move):
        move_coords = [n.coordinates for n in move.path_to_target]
        for pac_node in self.advisor.tree.tree_as_list:
            if pac_node.coordinates in move_coords:
                pac_node.color = COLOR.BLACK



        tree = self.advisor.tree.tree_as_list
        move_coords = [node.coordinates for node in move.path_to_target]
        for node in tree:
            if node.coordinates in move_coords:
                node.color == COLOR.BLACK

    def calculate_danger_cost(self, move):
        path_len = len(move.path_to_target)
        cost = sum([ (path_len-node.cost+1)*node.color.value for node in move.path_to_target])
        return cost


    def debug_print(self, string, boolean=True):
        if self.debug and boolean:
            print(string)
