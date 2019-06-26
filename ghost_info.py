class Ghost_Info():
    """Creates the Ghost Info, which is a collection of information on a ghost
    in a specific moment of gameplay.

    Attr:
    position: the coordinates of the ghost
    zombie: a boolean tag that determines if the ghosts is dangerous to Pac-Man
        False means ghost can eat Pac-Man, True means Pac-man can eat ghost
    timeout: the number of steps the ghosts will remain in zombie mode
    corridor: the corridor where ghosts is positioned
    dist_to_pacman: the shortest distance of the ghost to Pac-Man
    crossroad_to_pacman: the crossroad of Pac-Man's corridor from where the
        ghost will get to Pac-Man
    dist_to_crossroad: the distance of the ghost to 'crossroad_to_pacman'
    path: the shortest path that the ghost will take to get to Pac-Man
    """

    def __init__(self, ghost, zombie, timeout, corridor, dist_to_pacman, crossroad_to_pacman, dist_to_crossroad, path):
        self.position = ghost
        self.zombie = zombie
        self.timeout = timeout
        self.corridor = corridor
        self.dist_to_pacman = dist_to_pacman
        self.crossroad_to_pacman = crossroad_to_pacman
        self.dist_to_crossroad = dist_to_crossroad
        self.path = path


    def is_coord_in_path(self, coord):
        """Verifies if the coordinate 'coord' is in this ghost 'path'

        Args:
        coord: the coordinate to be verified

        Returns:
        True if the coordinate is in this ghost's path, False if not
        """
        for c in [c for corr in self.path for c in corr.coordinates]:
            if c == coord:
                return True
        return False

    def side_interception(self, pacman_path, flight=False):
        """Calculates if this ghost path will intercept Pac-Man's path

        Args:
        pacman_path: the path of Pac-Man to verify interception with
        flight: a flag that indicates Pac-Man's state (changes the search method)
        
        Returns:
        True if there is an interception, False if not
        """

        intercept_coord = None
        path = [c for c in self.path[-2].coordinates]
        pacman_path_coords = [c for corr in pacman_path for c in corr.coordinates]

        # find coordinate of interception
        for c in path:
            if c in pacman_path_coords:
                found_interception = True
                intercept_coord = c
                break
        if intercept_coord == None:
            return False
        ghost_intercept_dist = self.path[-2].dist_to_end(self.position, intercept_coord)    

        # calculate distance of ghost and path to the coordinate of interception
        pac_intercept_dist = 0
        if flight == False:
            for corr in pacman_path[::-1]:
                if intercept_coord in corr.coordinates:
                    pac_intercept_dist += corr.cost
                    break
                else:
                    pac_intercept_dist += corr.cost
        else:
            for corr in pacman_path:
                if intercept_coord in corr.coordinates:
                    pac_intercept_dist += corr.cost
                    break
                else:
                    pac_intercept_dist += corr.cost

        return pac_intercept_dist >= ghost_intercept_dist


    def __str__(self):
        return 'ghost('+str(self.position)+', '+str(self.dist_to_pacman)+')'

    def __repr__(self):
        return self.__str__()

    def print(self):
        string = \
        'Ghost ' + str(self.position) + ' is at distance ' + str(self.dist_to_pacman) + \
        ' from Pac-Man and ' + str(self.dist_to_crossroad) + ' from crossroad ' + str(self.crossroad_to_pacman)

        return string