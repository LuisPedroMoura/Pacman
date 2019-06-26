from game_consts import *
from pursuit_agent import *
from eating_agent import *
from counter_agent import *
from flight_agent import *
from panic_agent import *
from move_risk_assessor import *

class StrategyAnalyst():
    """Creates the Strategy Analist, which coordinates the possible moves given
    by the Pursuit, Eating, Counter and Flight Agents and chooses the best Pac-Man
    next move overall

    Attr:
    advisor: provides extensive information about the current situation of the map
    """

    def __init__(self, advisor):
        self.advisor = advisor
        self.pursuer_possible_moves = []
        self.eater_possible_moves = []
        self.counter_possible_moves = []
        self.fleer_possible_moves = []
        self.ghosts_in_pursuit = 0
        self.move_risk_assessor = None
        self.avoid_coordinates = []
        self.invalid_corridors = []
    
    def decide(self):
        """ Main method of the StrategyAnalyst class, which goal is to verify 
        current game condition and call, accordingly, for advice in the next
        Pac-Man's move from the Execution Agents. Relies on MoveRiskAssessor to
        validate Execution Agents advices.

        Returns:
        The next advised position for Pac-Man to go to
        """

        # if there are no ghosts to pursue pacman counters if is surrounded or eats if not
        for ghost in self.advisor.ghosts_info:
            
            if self._ghost_is_in_pursuit(ghost.position):
                self.ghosts_in_pursuit += 1
            
        self.move_risk_assessor = MoveRiskAssessor(self.advisor, self.ghosts_in_pursuit)


        # always tries to pursue ghosts first
        next_move = self._try_pursuit()
        if next_move != None:
            return next_move

        # counter (if not possible, try eating)
        if self.ghosts_in_pursuit >= NUMBER_OF_GHOST_TO_OFFENSIVE:
            
            next_move = self._try_counter(surrounded_counter=True)
            if next_move != None:
                return next_move
        
            next_move = self._try_eating(surrounded_eating=True)
            if next_move != None:
                return next_move

            next_move = self._try_flight(avoid_suggestion=False)
            if next_move != None:
                return next_move
        
        # eat (if not possible, try counter)
        else:
            next_move = self._try_eating()
            if next_move != None:
                return next_move

            next_move = self._try_counter()
            # if next_move != None:
            #     return next_move
            
            next_move = self._try_flight(avoid_suggestion=True)
            if next_move != None:
                return next_move
        
        
        # no strategy available, time to panic! Goes for the first safe corridor
        panicked_for_a_way_out = self._panic()

        # ----- no agent got a move - this should never happen
        if panicked_for_a_way_out == None:
            return None

        return panicked_for_a_way_out


    def _get_best_moves_from_agent(self, possible_moves):
        """ Auxiliary method for MODE.FLIGHT that selects the best moves of given
        Agent (Pursuit, Eating and Counter) according to different criteria

        Args:
        possible_moves: the ordered list of possible_moves of the Agent

        Returns:
        A list with the chosen best moves
        """

        if possible_moves == []:
            return []
        return sorted(possible_moves, key=lambda move: move[1])


    def _try_pursuit(self):
        targets = [ghost[0] for ghost in self.advisor.state['ghosts'] if ghost[1] == True]

        # verify that zombies ghosts are not in the den, if they are, don't pursue
        targets = [ghost for ghost in targets if ghost in self.advisor.map_.pathways[0]]

        if targets != []:
            pursuer = PursuitAgent(self.advisor, targets)
            self.pursuer_possible_moves = pursuer.pursue()
            valid_next_move = self.move_risk_assessor.analyse_best_move(self.pursuer_possible_moves)
            if valid_next_move:
                return self.pursuer_possible_moves[0][0]
        return None

    def _try_eating(self, surrounded_eating=False):
        targets = self.advisor.state['energy'] + self.advisor.state['boost']

        if len(self.advisor.state['energy']) > 50:
            if self.ghosts_in_pursuit < NUMBER_OF_GHOST_TO_OFFENSIVE:
                
                remove_coords = []
                for boost in self.advisor.state['boost']:
                    for corr in self.advisor.map_.corridors:
                        if boost in corr.coordinates:
                            remove_coords += corr.coordinates
                targets = [t for t in targets if t not in remove_coords]


        if targets != []:
            eater = EatingAgent(self.advisor, targets)
            self.eater_possible_moves = eater.eat()
            valid_next_move = self.move_risk_assessor.analyse_best_move(self.eater_possible_moves, flight=False, surrounded_eating=surrounded_eating)
            if valid_next_move:
                return self.eater_possible_moves[0][0]
        return None
    
    def _try_counter(self, surrounded_counter=False):
        targets = self.advisor.state['boost']
        # Pac-Man can only counter if there are boost targets
        if targets != []:
            counter = CounterAgent(self.advisor, targets)
            self.counter_possible_moves = counter.counter()
            valid_next_move = self.move_risk_assessor.analyse_best_move(self.counter_possible_moves, flight=False, surrounded_eating= surrounded_counter, counter=True)
            if valid_next_move:
                return self.counter_possible_moves[0][0]
        return None
        
    def _try_flight(self, avoid_suggestion=False):
        pacman = self.advisor.pacman_info

        # get best move from every agent
        pursuer_best_moves = self._get_best_moves_from_agent(self.pursuer_possible_moves)
        pursuer_best_moves = sorted(pursuer_best_moves, key=lambda move: move[1])
        eater_best_moves = self._get_best_moves_from_agent(self.eater_possible_moves)
        eater_best_moves = sorted(eater_best_moves, key=lambda move: move[1])
        counter_best_moves = self._get_best_moves_from_agent(self.counter_possible_moves)
        counter_best_moves = sorted(counter_best_moves, key=lambda move: move[1])

        best_moves = []
        best_moves += self._get_best_moves_from_agent(counter_best_moves)
        best_moves += self._get_best_moves_from_agent(pursuer_best_moves)
        
        for move in best_moves:

            # flee to a safe corridor (if possible, one in a best_move path)
            # args: target coordinate, coordinate to avoid
            targets = [(move[2][0].coordinates[0], [move[2][-2].get_coord_next_to_end(pacman.position)])]
            
            fleer = FlightAgent(self.advisor, targets)
            next_move = fleer.flee()

            valid_next_move = self.move_risk_assessor.analyse_best_move(possible_moves=next_move, flight=True)
            if valid_next_move:
                return next_move[0][0]
            else:
                if pacman.position in self.advisor.map_.crossroads:
                    if next_move[0][2][1].coordinates == pacman.corridor.coordinates:
                        self.invalid_corridors = [next_move[0][2][2]]
                    else:
                        self.invalid_corridors = [next_move[0][2][1]]
                else:
                    self.invalid_corridors += [next_move[0][2][2]]

 
        best_moves = self._get_best_moves_from_agent(eater_best_moves)

        for move in best_moves:

            # define which corridor flight_mode will avoid
            sub_corr0, sub_corr1 = pacman.corridor.sub_corridors(pacman.position)
            path_coords = [c for corr in move[2] for c in corr.coordinates]
            self.avoid_coordinates = []
            avoid = None

            if all([c in path_coords for c in sub_corr0.coordinates]):
                if avoid_suggestion:
                    avoid = sub_corr0.get_coord_next_to_end(pacman.position)
                else:
                    avoid = sub_corr1.get_coord_next_to_end(pacman.position)
            elif all([c in path_coords for c in sub_corr1.coordinates]):
                if avoid_suggestion:
                    avoid = sub_corr1.get_coord_next_to_end(pacman.position)
                else:
                    avoid = sub_corr0.get_coord_next_to_end(pacman.position)
            
            if avoid == None:
                for corr in self.advisor.map_.corridors:
                    if corr != pacman.corridor:
                        if pacman.position in corr.ends:
                            av = corr.get_coord_next_to_end(pacman.position)
                            if av != None:
                                self.avoid_coordinates += [av]
            else:
               self.avoid_coordinates += [avoid]

            # flee to a safe corridor (if possible, one in a best_move path)
            targets = [(move[2][0].coordinates[0], self.avoid_coordinates)]
            
            fleer = FlightAgent(self.advisor, targets)
            next_move = fleer.flee()

            valid_next_move = self.move_risk_assessor.analyse_best_move(possible_moves=next_move, flight=True)
            if valid_next_move:
                return next_move[0][0]
            else:
                if pacman.position in self.advisor.map_.crossroads:
                    if next_move[0][2][1].coordinates == pacman.corridor.coordinates:
                        self.invalid_corridors = [next_move[0][2][2]]
                    else:
                        self.invalid_corridors = [next_move[0][2][1]]
                else:
                    self.invalid_corridors += [next_move[0][2][2]]

        return None
    
    def _panic(self):
        panicker = PanicAgent(self.advisor)
        # ignore one previously verified bad move (not possible to block more than one)
        next_move = panicker.panic(self.invalid_corridors)
        return next_move


#--------------------------------------------------------------------------#
# AUXILIAR METHODS
#--------------------------------------------------------------------------#

    def _ghost_is_in_pursuit(self, ghost_position):

            px, py = self.advisor.pacman_info.position
            gx, gy = ghost_position

            internal_hor_heuristic = abs(gx-px)
            internal_ver_heuristic = abs(gy-py)
            internal_heuristic = internal_hor_heuristic + internal_ver_heuristic

            hor_tunnel_hor_heuristic = self.advisor.map_.map_.hor_tiles - abs(gx-px) if self.advisor.map_.hor_tunnel_exists else None
            hor_tunnel_ver_heuristic = abs(gy-py) if self.advisor.map_.hor_tunnel_exists else None
            
            ver_tunnel_hor_heuristic = abs(gx-px) if self.advisor.map_.ver_tunnel_exists else None
            ver_tunnel_ver_heuristic = self.advisor.map_.map_.ver_tiles - abs(gy-py) if self.advisor.map_.ver_tunnel_exists else None
            
            
            if hor_tunnel_hor_heuristic != None:
                hor_tunnel_heuristic = hor_tunnel_hor_heuristic + hor_tunnel_ver_heuristic
            else:
                hor_tunnel_heuristic = 1000 # will no be considered

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

            if dx <= SAFE_DIST_TO_GHOST and dy <= SAFE_DIST_TO_GHOST:
                self.ghosts_in_pursuit += 1
    