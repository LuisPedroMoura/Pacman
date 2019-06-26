from enum import Enum
import logging

#------------------------------------------------------------------------------#
# ENUMERATES

# Usage MODE.EATING
class MODE(Enum):
    PURSUIT = 1
    EATING  = 2
    COUNTER = 3
    FLIGHT  = 4
    PANIC = 5

class CORRIDOR_SAFETY(Enum):
    SAFE   = 1
    UNSAFE = 2

# crossroad_safety
class COLOR(Enum):
    BLACK = 0
    GREEN  = 1
    YELLOW1 = 100
    YELLOW2 = 10000
    YELLOW3 = 1000000
    YELLOW4 = 100000000
    RED     = 10000000000
    PACMAN = 2
    GHOST  = 3
    ZOMBIE = 4
    ENERGY_GREEN = 5
    ENERGY_YELLOW = 6
    ENERGY_RED = 7
    ENERGY_BLACK = 10
    BOOST_GREEN = 8
    BOOST_RED = 9

#------------------------------------------------------------------------------#
# GLOBAL VARIABLES

# distance at which ghost probably isn't in pursuit of pacman
SAFE_DIST_TO_GHOST = 8 #! test from 5 to 8

# value from 0 to 1.
# 0 -> Pac-Man does not pursue the ghots
# 1 -> Pac-Man pursues ant ghost in maximum range until timeout
GHOST_PURSUIT_MULTIPLIER = 0.6 #! test from 0.4 to 0.7

# number of ghosts at unsafe distance to prefer offensive strategy (counter first)
# the value must be double the ghosts, because ghosts are duplicated in ghosts_info
NUMBER_OF_GHOST_TO_OFFENSIVE = 2 #! test from 3 to 4 only with 4 ghosts, less ghosts test with 3

MAX_MOVE_SELECT_ON_EATING_MODE = 20
MAX_TIME_TO_CALCULATE_PACMAN_TREE = 50
MAX_PACMAN_TREE_SIZE = 2000
YELLOW_MARGIN = 4


#------------------------------------------------------------------------------#
# LOGGER 
# After many solutions, I found an elegant one (kudos to 
# https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings)

def setup_logger(name, log_file, level=logging.DEBUG, mode='w', format='[%(lineno)s - %(funcName)20s() - %(levelname)s] %(message)s\n'):
    # Function setup as many loggers as you want

    # currently writing over the logger file, change filemode to a to append
    handler = logging.FileHandler(log_file, mode)        
    
    # '%(levelname)s:\t%(message)' # simpler format
    format = logging.Formatter(format)
    handler.setFormatter(format)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger