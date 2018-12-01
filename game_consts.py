from enum import Enum
import logging

#------------------------------------------------------------------------------#
# ENUMERATES

# Usage MODE.EATING
class MODE(Enum):
    EATING  = 1
    FLIGHT  = 2
    PURSUIT = 3
    COUNTER = 4

class CORRIDOR_SAFETY(Enum):
    SAFE   = 1
    UNSAFE = 2

# crossroad_safety
class SEMAPHORE(Enum):
    GREEN  = 1
    YELLOW = 2
    RED    = 3


#------------------------------------------------------------------------------#
# GLOBAL VARIABLES

# minimum escape margin if pacman is racing towards crossroad against a ghost
SAFE_DIST_TO_CROSSROAD = 1
# distance at which ghost probably isn't in pursuit of pacman
SAFE_DIST_TO_GHOST = 7
# value from 0 to 1.
# 0 -> Pac-Man does not pursue the ghots
# 1 -> Pac-Man pursues ant ghost in maximum range until timeout
GHOST_PURSUIT_MULTIPLIER = 0.7

#------------------------------------------------------------------------------#
# LOGGER 
# After many solutions, I found an elegant one (kudos to 
# https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings)


def setup_logger(name, log_file, level=logging.DEBUG):
    """Function setup as many loggers as you want"""

    # currently writing over the logger file, change filemode to a to append
    handler = logging.FileHandler(log_file, mode='w')        
    
    # '%(levelname)s:\t%(message)' # simpler format
    format = logging.Formatter('[%(lineno)s - %(funcName)20s() - %(levelname)s] %(message)s\n')
    handler.setFormatter(format)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger