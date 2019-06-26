import game_consts
from strategy_topographer import StrategyTopographer
from pathways import Pathways
from tree_search import SearchTree, SearchProblem
from corridor import Corridor
from strategy_advisor import StrategyAdvisor
from strategy_analyst import StrategyAnalyst
import logging
import sys
import json
import asyncio
import websockets
import os
from mapa import Map
from eating_agent import *
from counter_agent import *
from pursuit_agent import *
from flight_agent import *
from time import time
import logging


# logger
# logs are written to file student.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logger.typeOfMessage('message')
logger = setup_logger('student', 'student.log')
time_logger = setup_logger('key_times', 'key_times.log', format='%(message)s\n')
time_logger.debug("TIMES IN MILISECONDS (*1000)")


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
        self.map_ = StrategyTopographer(map_)
        self.debug = False


    def get_next_move(self, state):
        """Objective of Pacman_agent - calculates the next position using
        multiple auxiliar methods

        Args:
        state: a list of lists with the state of every element in the game

        Returns: the key corresponding to the next move of PACMAN
        """

        # get information on the current game situation
        strategy_advisor = StrategyAdvisor(self.map_, state)

        # devise a strategy to play and get the next advise move
        strategy_analyst = StrategyAnalyst(strategy_advisor)
        next_move = strategy_analyst.decide()

        # if next_move is None, the the game is finished
        if next_move == None:
            return None

        return self.calculate_key(state['pacman'], next_move)
        



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

        if nx == px + 1:
            key = 'd'
        elif nx == px -1:
            key = 'a'
        elif ny == py + 1:
            key = 's'
        elif ny == py -1:
            key = 'w'
        elif nx > px:
            key = 'a'
        elif nx < px:
            key = 'd'
        elif ny > py:
            key = 'w'
        else:
            key = 's'
        
        return key



#------------------------------------------------------------------------------#
# MAIN METHOD - INTERFACES WITH SERVER TO RECEIVE AND SEND GAME 'WASD' KEYS
#------------------------------------------------------------------------------#

async def agent_loop(server_address = "localhost:8000", agent_name="student"):
    async with websockets.connect("ws://{}/player".format(server_address)) as websocket:

        #----------------------------------------------------------------------#
        # Receive information about static game properties 
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)
        

        #----------------------------------------------------------------------#
        # for debug purposes (save scores and stress testing)
        # create apropriated logger based on ghosts and level
        if game_properties['ghosts'] == []:
            name = 'scores_empty.log'
        else:
            name = 'scores_ghosts_level' + str(game_properties['ghosts_level']) + '.log'

        score_logger = setup_logger('scores', name, mode='a', format='%(message)s\n')
        

        #----------------------------------------------------------------------#
        # Define game constants
        num_ghosts = game_properties['ghosts']
        ghosts_level = game_properties['ghosts_level']

        if num_ghosts < 2:
            game_consts.SAFE_DIST_TO_GHOST = 7
            game_consts.GHOST_PURSUIT_MULTIPLIER = 0.8 
            game_consts.NUMBER_OF_GHOST_TO_OFFENSIVE = 1
        
        if num_ghosts == 2:
            game_consts.SAFE_DIST_TO_GHOST = 8
            game_consts.GHOST_PURSUIT_MULTIPLIER = 0.7 
            game_consts.NUMBER_OF_GHOST_TO_OFFENSIVE = 3

        if num_ghosts > 2 and ghosts_level <= 2:
            game_consts.SAFE_DIST_TO_GHOST = 7
            game_consts.GHOST_PURSUIT_MULTIPLIER = 0.6 
            game_consts.NUMBER_OF_GHOST_TO_OFFENSIVE = 3

        if num_ghosts > 2 and ghosts_level >= 3:
            game_consts.SAFE_DIST_TO_GHOST = 8
            game_consts.GHOST_PURSUIT_MULTIPLIER = 0.7 
            game_consts.NUMBER_OF_GHOST_TO_OFFENSIVE = 3

        # Create the pacman agent
        pacman = Pacman_agent(Map(game_properties['map']))
        lives = game_properties['lives']
        key = 'w'           # W is for Winner
        previous_key = 'w'  # W is for Winner
        
        #----------------------------------------------------------------------#
        #----------------------------------------------------------------------#
        # play!
        while True:

            r = await websocket.recv()
            start = time()          # saved on key_times.log
            state = json.loads(r)   # receive game state

            try:

                #------------------------------------------------------------------#
                # lost a life
                if state['lives'] != lives:
                    lives = state['lives']
                    #print('\n############\nPACMAN HAS LOST A LIFE\n#############\n')
                    stop0 = time()
                    #print('Last move time: ' + str((stop0-start) * 1000))
                    print("\033[93mLOST A LIFE\033[0m\n")

                #------------------------------------------------------------------#
                # game won (ended)
                if state['energy'] == [] and state['boost'] == []:
                    print("\n\033[92mGAME ENDED. SCORE IS " + str(state['score']) + "\033[0m")
                    score_logger.debug(str(state['score']))
                    return

                #------------------------------------------------------------------#
                # game lost (no more lives)
                if not state['lives']:
                    print("\n\033[91mGAME OVER. SCORE IS " + str(state['score'])  + "\033[0m")
                    score_logger.debug(str(state['score']))
                    return

                #------------------------------------------------------------------#
                # next move is None
                key = pacman.get_next_move(state)
                if key == None:
                    key = previous_key
                else:
                    previous_key = key

            
            except ValueError:
                pass

            #-send new key-----------------------------------------------------#
            await websocket.send(json.dumps({"cmd": "key", "key": key}))

            #------------------------------------------------------------------#
            # debug purposes (time)
            stop = time()            
            time_logger.debug(str(state['step']) + " " + str(key) + "-> " + str((stop-start) * 1000))

loop = asyncio.get_event_loop()
SERVER = os.environ.get('SERVER', 'localhost')
PORT = os.environ.get('PORT', '8000')
NAME = os.environ.get('NAME', 'student')
loop.run_until_complete(agent_loop("{}:{}".format(SERVER,PORT), NAME))

#------------------------------------------------------------------------------#
