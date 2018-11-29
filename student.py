from game_consts import *
from static_analysis import Static_Analysis
from pathways import Pathways
from tree_search import SearchTree, SearchProblem
from corridor import Corridor
from strategy_advisor import Strategy_Advisor
import logging
import sys
import json
import asyncio
import websockets
import os
from mapa import Map





#$ PORT=80 SERVER=pacman-aulas.ws.atnog.av.it.pt python client.py
# to kill server: fuser 8000/tcp

# logger
# logs are written to file student.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logger.typeOfMessage('message')
logger = setup_logger('student', 'student.log')

# for debug purposes
debug = True


#! ##########   PAC-MAN AGENT GLOBAL STRATEGY   ##########

    #! ###    CONCEPTS    ###

    #! Corridor
        #* A list of path coordinates with only two adjacent coordinates
        #* and two crossroads as ends

    #! Crossroad
        #* A coordinate that joins corridors. The crossroad belong to all
        #* corridors it joins

    #! Corridor SAFE vs UNSAFE
        #* SAFE - Has no ghosts
        #* UNSAFE - Has one or more ghosts

    #! Crossroad GREEN - YELLOW - RED
        #* Refers to the crossroads directly accessible to Pac-Man (the
        #* ends of it's corridor)
        #* GREEN - No ghosts in proximity
        #* YELLOW - There are ghosts at a dangerous distance of the crossroad
        #*          (default = 1). Pac-Man can escape if he goes directly through
        #*          that end
        #* RED - Considering that the ghosts is in pursuit of Pac-Man, it is
        #*       impossible for Pac-Man to escape from that end before the ghost
        #*       gets to it (or the ghost is already inside Pac-Man's Corridor)


    #! Strategy Game Modes
        #* EATING_MODE - Pac-Man is safe. Focus on eating energies. Tries to
        #*               find closest energies through safest paths
        #* COUNTER_MODE - Pac-Man is almost surrounded. Focus on eating boosts.
        #* PURSUIT_MODE - Pac-Man is safe and there are zombie ghosts.
        #*               Focus on eating ghosts.
        #* FLIGHT_MODE - Pac-Man is almost surrounded. There are no boosts
        #*               available. Focus on finding the closest safest Corridor.

    #! Static Analysis of Map provides
        #* pathways
        #* corridors
        #* crossroads
        #* corridor_adjacencies
    
    #! Strategy Guidelines
        #* Pac-Man Agent calls Strategy Advisor
        #*      Strategy Advisor analyses:
        #*          Corridor Safety
        #*          Crossroads Semaphores
        #*          Distance to ghosts
        #*      Strategy Advisor advises a Game Mode
        #* Pac-Man calls Game Mode Agent to get next move
        #*      Game Mode tries to find the next move
        #* Pac-Man analyses next move
        #*      Is it specific (only one solution)
        #*          Pac-Man accepts next move
        #*      It's not specific (strategy was not correct)
        #*          Pac-Man calls Strategy Adjuster
        #*              Strategy Adjuster evaluates new info and advises a new Game Mode
        #*          Pac-Man call Game Mode Agent to get next move
        #*              Game Mode tries to find a solution
        #*          Pac-Man accepts best solution found (if more than one)



class Pacman_agent():
    """Creates the PACMAN agent that analyses the given 'Map' and 'state'
    to decide which direction to take and win the game 

    Args:
    map_: instance of Map for the current level

    Attr:
    map_: instance of Map for the current level
    static_analysis: instance of Static_Analysis containing:
                - pathways: list of all coordinates that are not walls
                - adjacencies: list of pairs of adjacent pathways
                - corridors: list of coordinates that create a corridor
                - crossroads: list of all coordinates that separate corridors
    """

    def __init__(self, map_,): 
        logger.warning('\n\n\n ========================== NEW EXECUTION ==========================\n')
        logger.debug('CREATING PACMAN AGENT\n')

        self.map_ = Static_Analysis(map_)
        self.debug = False

        logger.debug('CREATED PACMAN AGENT')


    def get_next_move(self, state):
        """Objective of Pacman_agent - calculates the next position using
        multiple auxiliar methods

        Args:
        state: a list of lists with the state of every element in the game

        Returns: the key corresponding to the next move of PACMAN
        """

        #logger.debug(nt("\nEnergy size is : " + str(len(state['energy'])) + "\n")

        

        # get advice on the next move
        strategy_advisor = Strategy_Advisor(self.map_, state)
        mode_handler = strategy_advisor.advise()
        next_move = self.mode(mode_handler, strategy_advisor, state)

        # if advice is not specific, adjustments to the strategy may be needed
        if (next_move == False): # correct when methods are implemented
            strategy_adjuster = Strategy_Adjuster()
            mode_handler = strategy_adjuster.adjustStrategy()
            next_move = self.mode(mode_handler, state)
        
        # calculate and return the key
        # if (next_move == [5,23] or next_move == [6,7]):
        #     print("KEY IS " + str(self.calculate_key(state['pacman'], next_move)))

        # logger.debug("KEY IS " + str(self.calculate_key(state['pacman'], next_move)) + "\n\n")
        return self.calculate_key(state['pacman'], next_move)



    def mode(self, mode_handler, advisor, state):
        if mode_handler == MODE.EATING:
            next_move = self.eating_agent(advisor, state)
        elif mode_handler == MODE.FLIGHT:
            next_move = self.flight_agent()
        elif mode_handler == MODE.PURSUIT:
            next_move = self.pursuit_agent()
        else: # next_move == MODE.COUNTER
            next_move = self.counter_agent(advisor, state)
        return next_move



    def calculate_key(self, pacman, next_move):
        """Calculates the 'wasd' key that corresponds to the next move

        Args:
        pacman: the coordinates of Pac-Man position
        next_move: the coordinates of the position to go to

        Returns:
        The 'wasd' key for moving from pacman to next_move
        """
        #print("NEXT MOVE: " + str(pacman) + ", " + str(next_move))
        px, py = pacman
        nx, ny = next_move
        if nx > px:
            key = 'd'
        elif nx < px:
            key = 'a'
        elif ny > py:
            key = 's'
        else: # ny < py
            key = 'w'
        
        return key



    def eating_agent(self, advisor, state):

        domain = Pathways(self.map_.corr_adjacencies, state['energy'] + state['boost'])

        acessible_energies = []
        targets = state['energy'] + state['boost']
        possible_moves = []
        
        for energy in targets:

            domain = Pathways(self.map_.corr_adjacencies.copy(), state['energy'] + state['boost'])
            # print("Energy #######################################")
            # print(energy)
            # print("#######################################")

            corridor = None
            for corr in self.map_.corridors:
                if energy in corr.coordinates:
                    corridor = corr

            # print("Corridor #######################################")
            # print(corridor)
            # print("#######################################")
            if (self.debug):
                pass
                #print(energy)
            my_prob = SearchProblem(domain, corridor, energy, advisor.pacman_info.corridor, advisor.pacman_info.position)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.search()
            

            if search_results != None:
                #? avoid repetead energies. 
                #if (search_results[0] not in acessible_energies):       
                    #acessible_energies += [search_results[0]]
                acessible_energies += [energy]
                possible_moves += [(search_results[0], search_results[1])]

        logger.debug("NEW! PACMAN POS" + str(advisor.pacman_info.position))
        #acessible_energies = [a for a in acessible_energies if a != advisor.pacman_info.position]
        if advisor.pacman_info.position == [4,15] or advisor.pacman_info.position == [4,14] \
        or advisor.pacman_info.position == [4,12] or advisor.pacman_info.position == [4,13] \
        or advisor.pacman_info.position == [4,11] or advisor.pacman_info.position == [4,10] \
        or advisor.pacman_info.position == [3,10] or advisor.pacman_info.position == [2,10] \
        or advisor.pacman_info.position == [1,10] or advisor.pacman_info.position == [1,9] \
        or advisor.pacman_info.position == [1,8] or advisor.pacman_info.position == [1,7] \
        or advisor.pacman_info.position == [2,7]:
            logger.debug("Acessible_Energies #######################################")
            logger.debug(acessible_energies)
            logger.debug("#######################################")
        
        logger.debug("Returning " + str(possible_moves[0]))


        possible_moves = sorted(possible_moves,key=lambda t: t[1])
        return possible_moves[0][0]
    

    def flight_agent(self, advisor):
        #crossroads YY, YR, RR -> semaphore.Y or semaphore.R for end[0] and end[1]
        #ghost.distPac
        #corr adj SAFE, UNSAFE 

        #pac corr UNSAFE? (ghost no mesmo corr do pac)
            #crossroad[0].RED and crossroad[1].RED?
                #distGhostPac >= SAFE_DIST_TO_GHOST?
                    #escolhe lado
                #distGhostPac < SAFE_DIST_TO_GHOST?
                    #lado com maior dist
            
            #crossroad[0].YELLOW?
                #próximo corr SAFE?
                    #escolhe saída
                #proximo corr UNSAFE?
                    #ghost do prox corr (crossroad[0]) pode nao estar em perseguiçao, so...
                    #distGhostPac >= SAFE_DIST_TO_GHOST?
                        #escolhe saida
                    #distGhostPac < SAFE_DIST_TO_GHOST?
                        #escolhe o 1º corr
                    

            #else crossroad[1].YELLOW?
                #próximo corr SAFE?
                    #escolhe saída
                #proximo corr UNSAFE?
                    #ghost do prox corr (crossroad[1]) pode nao estar em perseguiçao, so...
                    #distGhostPac >= SAFE_DIST_TO_GHOST?
                        #escolhe saida
                    #distGhostPac < SAFE_DIST_TO_GHOST?
                        #escolhe o 1º corr
                    

        #else pac corr SAFE? (corr do pac nao tem ghost)
            #crossroad[0].YELLOW and crossroad[1].YELLOW?
                #pesquisar todos os prox corredores
                #SAFE?
                    #escolhe saida
                #UNSAFE? 
                    #escolhe o 1º corr do crossroad mais perto

            #crossroad[0].RED?
                #crossroad[1].YELLOW?
                    #próximo corr SAFE?
                        #escolhe saída do ghost mais longe
                    #próximo corr UNSAFE?
                        #ghost do prox corr (crossroad[1]) pode nao estar em perseguiçao, so...
                        #distGhostPac >= SAFE_DIST_TO_GHOST?
                            #escolhe saida
                        #distGhostPac < SAFE_DIST_TO_GHOST?
                            #escolhe o 1º corr
                #else crossroad[1].RED?
                    #morrer com dignidade

            #crossroad[1].RED?
                #crossroad[0].YELLOW?
                    #próximo corr SAFE?
                        #escolhe saída
                    #próximo corr UNSAFE?
                        #ghost do prox corr (crossroad[0]) pode nao estar em perseguiçao, so...
                        #distGhostPac >= SAFE_DIST_TO_GHOST?
                            #escolhe saida
                        #distGhostPac < SAFE_DIST_TO_GHOST?
                            #escolhe o 1º corr
                #else crossroad[0].RED?
                    #morrer com dignidade


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
        
        
        
        #ghosts_info = advisor.ghosts_info
        pac_info = advisor.pacman_info
        pac_crossroads = pac_info.crossroads

        ########################################################################
        ## PAC CORR UNSAFE #####################################################
        ########################################################################

        #corr pacman tem ghost do lado do crossroad0       
        if pac_info.crossroad0_is_safe == CORRIDOR_SAFETY.UNSAFE:

            #pacman esta encurralado (corr do pacman tem ghosts dos 2 lados)
            if pac_info.crossroad1_is_safe == CORRIDOR_SAFETY.UNSAFE:
                
                #escolhe lado com ghost mais afastado
                if pac_info.dist_to_ghost_at_crossroad0 >= pac_info.dist_to_ghost_at_crossroad1:
                    #escolhe crossroad0
                    return self.calc_next_coord(pac_info.position, pac_info.crossroad0)
                else:
                    #escolhe crossroad1
                    return self.calc_next_coord(pac_info.position, pac_info.crossroad1)

            #ghost no corr do pacman apenas do lado do crossroad0 -> crossroad0 is RED
            else:
    
                #pacman consegue fugir pelo crossroad1
                if pac_info.semaphore1 == SEMAPHORE.YELLOW:   

                    pac_adj1 = [ [cA, cB] for [cA, cB] in self.map_.corr_adjacencies\
                                        if pac_crossroads[1] in cA.ends\
                                        or pac_crossroads[1] in cB.ends]


                    pac_safe_corr1 = [[cA, cB] for [cA, cB] in pac_adj1\
                                        if (cA.coordinates == pac_info.coordinates and cB.safe == CORRIDOR_SAFETY.SAFE)\
                                        or (cB.coordinates == pac_info.coordinates and cA.safe == CORRIDOR_SAFETY.SAFE)]

                    #ha corr safe
                    if pac_safe_corr1 != []:
                        #escolhe pac_safe_corr1[0]
                        return self.calc_next_coord(pac_info.position, pac_info.crossroad1)
                    
                    #NAO ha corr safe
                    else:
                        pass
                        #escolhe corr com ghost mais afastado
                        #?return self.calc_corridor_ghost_farther(pac_info, pac_adj1, ghosts_info)
                        return self.calc_next_coord(pac_info.position, pac_info.crossroad1)

                #pacman NAO consegue fugir pelo crossroad1 -> crossroad1 is RED
                else:
                    pass
                    #escolhe crossroad1
                    return self.calc_next_coord(pac_info.position, pac_info.crossroad1)

        #corr do pacman NAO tem ghost do lado crossroad0
        else:

            pac_adj0 = [ [cA, cB] for [cA, cB] in self.map_.corr_adjacencies\
                                        if pac_crossroads[0] in cA.ends\
                                        or pac_crossroads[0] in cB.ends]
           
            pac_safe_corr0 = [[cA, cB] for [cA, cB] in pac_adj0\
                                if (cA.coordinates == pac_info.coordinates and cB.safe == CORRIDOR_SAFETY.SAFE)\
                                or (cB.coordinates == pac_info.coordinates and cA.safe == CORRIDOR_SAFETY.SAFE)]



            pac_adj1 = [ [cA, cB] for [cA, cB] in self.map_.corr_adjacencies\
                                        if pac_crossroads[1] in cA.ends\
                                        or pac_crossroads[1] in cB.ends]

            pac_safe_corr1 = [[cA, cB] for [cA, cB] in pac_adj1\
                                if (cA.coordinates == pac_info.coordinates and cB.safe == CORRIDOR_SAFETY.SAFE)\
                                or (cB.coordinates == pac_info.coordinates and cA.safe == CORRIDOR_SAFETY.SAFE)]


            #corr do pacman tem ghost apenas do lado crossroad1 -> crossroad1 is RED
            if pac_info.crossroad1_is_safe == CORRIDOR_SAFETY.UNSAFE:

                #pacman consegue fugir apenas pelo crossroad0
                if pac_info.semaphore0 == SEMAPHORE.YELLOW:
                    #crossroad0 liga a corr SAFE
                    if pac_safe_corr0 != []:
                        #escolhe pac_safe_corr0[0]
                        return self.calc_next_coord(pac_info.position, pac_info.crossroad0)
                    
                    #NAO ha corr SAFE pelo crossroad0
                    else:
                        pass
                        #escolhe corr com ghost mais afastado
                        #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0, ghosts_info)
                        return self.calc_next_coord(pac_info.position, pac_info.crossroad0)

                #pacman NAO consegue fugir por nenhum crossroad -> crossroad0 is RED
                else:
                    pass
                    #escolhe lado com ghost mais afastado
                    #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0 + pac_adj1, ghosts_info)
                    return self.calc_next_coord(pac_info.position, pac_info.crossroad0)


            ####################################################################
            ## PAC CORR SAFE ###################################################
            ####################################################################

            #corr do pacman NAO tem ghosts -> crossroad[0].SAFE and crossroad[1].SAFE
            else:
                
                #pacman consegue fugir pelo crossroad0
                if pac_info.semaphore0 == SEMAPHORE.YELLOW:
                
                    #pacman consegue fugir por qualquer crossroad
                    if pac_info.semaphore1 == SEMAPHORE.YELLOW:

                        #crossroad0 liga a corr SAFE
                        if pac_safe_corr0 != []:
                            #ambos os crossroads ligam a corr SAFE
                            if pac_safe_corr1 != []:
                                #escolhe o crossroad mais longe
                                #crossroad0 mais longe do pacman
                                if pac_info.dist_to_crossroad0 >= pac_info.dist_to_crossroad1:
                                    #escolhe pac_safe_corr0[0]
                                    return self.calc_next_coord(pac_info.position, pac_info.crossroad0)

                                #crossroad1 mais longe do pacman    
                                else:
                                    #escolhe pac_safe_corr1[0]
                                    return self.calc_next_coord(pac_info.position, pac_info.crossroad1)

                            #apenas crossroad0 liga a corr SAFE
                            else:
                                #escolhe pac_safe_corr0[0]
                                return self.calc_next_coord(pac_info.position, pac_info.crossroad0)
                        
                        #crossroad0 nao liga a corr SAFE
                        else:
                            #apenas crossroad1 liga a corr SAFE
                            if pac_safe_corr1 != []:
                                #escolhe pac_safe_corr1[0]
                                return self.calc_next_coord(pac_info.position, pac_info.crossroad1)

                            #NAO ha corr SAFE        
                            else:
                                pass
                                #escolhe corr com ghost mais afastado
                                #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0 + pac_adj1, ghosts_info)
                                return self.calc_next_coord(pac_info.position, pac_info.crossroad0)#, return self.calc_next_coord(pac_info.position, pac_info.crossroad1)
                    
                    #pacman consegue fugir apenas pelo crossroad0
                    else:

                        #crossroad0 liga a corr SAFE
                        if pac_safe_corr0 != []:
                            #escolhe pac_safe_corr0[0]
                            return self.calc_next_coord(pac_info.position, pac_info.crossroad0)
                        
                        #NAO ha corr SAFE pelo crossroad0
                        else:
                            pass
                            #escolhe corr com ghost mais afastado
                            #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0, ghosts_info)
                            return self.calc_next_coord(pac_info.position, pac_info.crossroad0)
                
                #pacman NAO consegue fugir pelo crossroad0
                else:

                    #pacman consegue fugir apenas pelo crossroad1
                    if pac_info.semaphore1 == SEMAPHORE.YELLOW:
                        #crossroad1 liga a corr SAFE
                        if pac_safe_corr1 != []:
                            #escolhe pac_safe_corr1[0]
                            return self.calc_next_coord(pac_info.position, pac_info.crossroad1)
                        
                        #NAO ha corr SAFE pelo crossroad1
                        else:
                            pass
                            #escolhe corr com ghost mais afastado
                            #?return self.calc_corridor_ghost_farther(pac_info, pac_adj1, ghosts_info)
                            return self.calc_next_coord(pac_info.position, pac_info.crossroad1)

                    #pacman NAO consegue fugir por nenhum crossroad
                    else:
                        pass
                        #escolhe lado com ghost mais afastado
                        #?return self.calc_corridor_ghost_farther(pac_info, pac_adj0 + pac_adj1, ghosts_info)
                        return self.calc_next_coord(pac_info.position, pac_info.crossroad0)

        
                
    def calc_next_coord(self, pos, end):
        [px, py] = pos
        [ex, ey] = end
        
        if py == ey:
            if px >= ex:
                return [px-1, py]
            return [px+1, py]
        elif px == ex:
            if py >= ey:
                return [px, py-1]
            return [px, py+1]
            


    #escolhe corr com ghost mais afastado
    def calc_corridor_ghost_farther(self, pac_info, pac_adj, ghosts_info):
        dist = 0
        corr = []
        for adj_corr in pac_adj:
            for g_info in ghosts_info:
                if g_info.corridor == adj_corr and dist < g_info.dist_to_pacman:
                    dist = g_info.dist_to_pacman
                    corr = g_info.corridor                                                   
        
        #TODO devolver prox coord
        pass

    
    def pursuit_agent(self, state):
        pass


    def counter_agent(self, advisor, state):
        """Calculates the next position of the next move, when in counter mode.
        In Counter Mode, Pac-Man is almost surrounded by ghosts and must focus on eating boosts.
        
        Args:
        advisor
        state

        Returns:
        The [x,y] position of the next_move

        Considerations/Strategy:
        -> For each corridor where the boosts are, check for safe ones
        -> From the safest ones, choose the closest (if no one is safe, choose the closest one)
        
        ghost [[9, 15], False, 0],
        """
        
        boosts = state['boost'].copy()
        acessible_boosts = []
        possible_moves   = []
        safeties         = []

        for boost in boosts:
            domain = Pathways(self.map_.corr_adjacencies.copy(), boosts)

            corridor = None
            for corr in self.map_.corridors:
                if boost in corr.coordinates:
                    corridor = corr
                    safety = corridor.safe

            my_prob = SearchProblem(domain, corridor, boost, advisor.pacman_info.corridor, advisor.pacman_info.position)
            my_tree = SearchTree(my_prob, "a*")
            search_results = my_tree.search()
            
            if search_results != None:
                #? avoid repetead boosts
                if boost not in acessible_boosts:
                    acessible_boosts += [boost]
                    possible_moves   += [(search_results[0], search_results[1])]
                    safeties         += [safety]

        # print("BOOSTS"   + str(acessible_boosts) + "\n")
        # print("MOVES"    + str(possible_moves)+ "\n")
        # print("SAFETIES" + str(safeties)+ "\n")

        if len([safety for safety in safeties if safety == CORRIDOR_SAFETY.SAFE]): #if any corridor is safe
            #remove unsafe corridors info
            for i in range(0, len(acessible_boosts)):
                if safeties[i] == CORRIDOR_SAFETY.UNSAFE:
                #TODO it crashed one here but I can't replicate it now :(
                    del safeties[i]
                    del acessible_boosts[i]
                    del possible_moves[i]        

        # should not be on this mode (no more boosts)
        if (len(possible_moves) == 0):
            return False
        
        # choose the closest boost 
        # either there are several boosts in a safe corridor 
        # OR there are only boosts in unsafe corridors)
        possible_moves = sorted(possible_moves,key=lambda elem: elem[1])
        return possible_moves[0][0]



#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
async def agent_loop(server_address = "localhost:8000", agent_name="student"):
    async with websockets.connect("ws://{}/player".format(server_address)) as websocket:

        #----------------------------------------------------------------------#
        # Receive information about static game properties 
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        #----------------------------------------------------------------------#
        
        
        # Create the pacman agent
        pacman = Pacman_agent(Map(game_properties['map']))

        # play!
        while True:
            #------------------------------------------------------------------#
            r = await websocket.recv()
            state = json.loads(r) #receive game state

            # game over (unnecessary for actual play
            if not state['lives']:
                print("GAME OVER")
                return
            #------------------------------------------------------------------#

            
            #print(state)
            # get next move from pacman agent
            key = pacman.get_next_move(state)

            
            #-send new key-----------------------------------------------------#
            await websocket.send(json.dumps({"cmd": "key", "key": key}))
            #------------------------------------------------------------------#

loop = asyncio.get_event_loop()
SERVER = os.environ.get('SERVER', 'localhost')
PORT = os.environ.get('PORT', '8000')
NAME = os.environ.get('NAME', 'student')
loop.run_until_complete(agent_loop("{}:{}".format(SERVER,PORT), NAME))
if __name__ == "__main__":
    agent_loop()
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#