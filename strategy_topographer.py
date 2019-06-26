from corridor import Corridor
from game_consts import *

debug = True

# logger
# logs are written to file static_analysis.log after the client is closed
# possible messages: debug, info, warning, error, critical 
# how to use: logger.typeOfMessage('message')
logger = setup_logger('static_analysis', 'static_analysis.log')


class StrategyTopographer():
    """Makes the static analysis of the Map instance for the game. 

    Args:
    map_: instance of Map for the current level

    Attr:
    map_: instance of Map for the current level
    pathways: list of all coordinates that are not walls
    adjacencies: list of pairs of adjacent pathways
    corridors: list of coordinates that create a corridor
    crossroads: list of all coordinates that separate corridors
    """

    def __init__(self, map_):
        self.hor_tunnel_exists = False
        self.ver_tunnel_exists = False
        self.map_ = map_
        self.pathways = self.create_pathways_list()
        self.crossroads = self.create_crossroads_list(self.pathways)
        self.corridors = self.create_corridors(self.pathways, self.crossroads)
        self.corridors = [ Corridor(corr) for corr in self.corridors ]
        self.corr_adjacencies =self.create_corridor_adjacencies(self.corridors)
        self.ghosts_den = []
        self.average_corridor_cost = self.calc_average_corridor_cost()


    #* ##########   TESTED AND VERIFIED   ##########
    def create_pathways_list(self):
        """Create a list with all coordinates that are not walls

        Returns:
        Tuple of lists (for efficiency purposes):
        pathways_hor: pathways organized by row
        pathways_ver: pathways organized by column
        """

        # find ghosts den. This area will not be used in any search or strategy
        # and should be avoided by PACMAN
        self.ghosts_den = self.get_ghosts_den(self.map_)
        #self.ghosts_den = self.get_den_interior()

        pathways_hor = []
        for y in range(self.map_.ver_tiles):
            for x in range(self.map_.hor_tiles):
                
                if not self.map_.is_wall((x,y)): 
                    pathways_hor += [[x,y]]

        pathways_hor = [ p for p in pathways_hor if p not in self.ghosts_den ]
        pathways_ver = sorted(pathways_hor, key=lambda y: (x,y))

        return pathways_hor, pathways_ver

#------------------------------------------------------------------------------#
    
    #* ##########   TESTED AND VERIFIED   ##########
    def create_crossroads_list(self, pathways):
        """Create a list with all coordinates that are crossroads

        Args:
        pathways: tuple with two list with all coordinates that are not walls

        Returns:
        crossroads: list of all coordinates that are crossroads:
        """

        pathways_hor, _ = pathways
        crossroads = []
        for [x,y] in pathways_hor:
            adj = 0
            if x > 0 and not self.map_.is_wall((x-1,y)):
                adj += 1
            if x < self.map_.hor_tiles-1 and not self.map_.is_wall((x+1,y)):
                adj += 1
            if y > 0 and not self.map_.is_wall((x,y-1)):
                adj += 1
            if y < self.map_.ver_tiles-1 and not self.map_.is_wall((x,y+1)):
                adj += 1
            if adj > 2:
                crossroads += [[x,y]]

        return crossroads

#------------------------------------------------------------------------------#

    #* ##########   TESTED AND VERIFIED   ##########
    def get_ghosts_den(self, map_):
        """delimit the coordinates that make up the ghosts den

        Args:
        map_       : map of the game

        Returns:
        den_corners: list of coordinates of the points inside the den (including the walls and entrances)
        """

        # get ghots spawn point (which is itself part of the den)
        spawn = map_.ghost_spawn
        
        # list of the 4 corners of the den (den is a rectangle)
        den_corners = []

        # possible directions to go from a given point in the map
        # format (dir_x, dir_y)
        # currently init is equivalent to left, right, up, down
        possible_dirs =[(-1,0), (1,0), (0, 1), (0, -1)]    

        # initialize to_visit queue
        # to_visit is a queue with the points to visit
        # each position is a tuple (pos_x, pos_y, list of possible directions)
        to_visit = [(spawn, possible_dirs)]     

        while len(to_visit) > 0:
            # "pop" element from queue to_visit
            current_pos, current_dirs = to_visit[0]
            current_x, current_y = current_pos
            to_visit = to_visit[1:] 
            
            adj_walls = []

            for current_dir in current_dirs:
                current_dir_x, current_dir_y = current_dir    
                remaining_dirs = [dir_ for dir_ in current_dirs if dir_ != current_dir]
                
                # New position is obtained traveling in the current_direction from the (current_x, current_y)
                new_pos = current_x + current_dir_x, current_y + current_dir_y

                # if it's a wall, add the new position to the list of the adjacent walls
                if (self.map_.is_wall(new_pos)):                    
                    adj_walls += [new_pos]
                  
                # if it's not a wall, add the new position to the positions to visit. 
                else:
                    # from the new position we can go to the remaning_dirs + the oposite direction of where it came from 
                    # (thus avoiding repetead points, ie going back)
                    possible_dirs = [current_dir] + [dir_ for dir_ in remaining_dirs if dir_ != (current_dir_x * -1, current_dir_y * -1)]
                    to_visit += [(new_pos, possible_dirs)]
            
            # the current point is a candidate to be a corner (2 adjacent walls)
            if len(adj_walls) == 2: 

                # verify if adjacent walls are valid
                # all corners in a rectangle has 2 adjacent walls
                # but we can have points with 2 adjacent walls 
                # without being a corner (see point (3, 15) of the original map, for example)
                wall1_x, wall1_y = adj_walls[0]
                wall2_x, wall2_y = adj_walls[1]
                
                if (abs(wall1_x - wall2_x) == 1 and abs(wall1_y - wall2_y) == 1):
                    # we can have repeteaded corners 
                    # we can reach corners from different paths
                    den_corners = list(set(den_corners + [(current_x, current_y)]))
                    
                    # Found all den corners (a rectangular den has 4 corners)
                    # Since the den is rectangular so, we can define the bounds of the den 
                    # and its inside points using the corners
                    if (len(den_corners) == 4):
                        
                        # previously
                        #return den_corners

                        # return all positions of the outer square
                        # 4 corners, two possible values for x and y: the min and max
                        x_values, y_values = set([x for (x, y) in den_corners]), set([y for (x, y) in den_corners])
                        big_x, big_y = max(x_values), max(y_values)
                        small_x, small_y = min(x_values), min(y_values)
                        
                        # include the walls
                        small_x -= 1
                        small_y -= 1
                        big_x   += 1
                        big_y   += 1
                        den = []

                        for i in range(small_x, big_x + 1, 1):
                            for j in range(small_y, big_y + 1, 1):
                                den += [[i, j]]

                        return den

                    # clean up to_visit
                    # after finding a corner, we no longer have to
                    # search using the points in that quadrant 
                    # so we can clean up the list based on zones

                    # Note:
                    # visit[0] -> pos
                    # visit[0][0/1] -> pos_x/pos_y
                    if (current_x < spawn[0]):
                        if (current_y > spawn[0]): # left up corner
                            to_visit = [visit for visit in to_visit if visit[0][0] > spawn[0] or (visit[0][0]  < spawn[0] and visit[0][1] < spawn[1])]
                        if (current_y < spawn[0]): # left down corner
                            to_visit = [visit for visit in to_visit if visit[0][0] > spawn[0] or (visit[0][0]  < spawn[0] and visit[0][1] > spawn[1])]
                    elif (current_x > spawn[0]):
                        if (current_y > spawn[0]): # right up corner
                            to_visit = [visit for visit in to_visit if visit[0][0] < spawn[0] or (visit[0][0]  > spawn[0] and visit[0][1] < spawn[1])]
                        if (current_y < spawn[0]): # right down corner
                            to_visit = [visit for visit in to_visit if visit[0][0] < spawn[0] or (visit[0][0]  > spawn[0] and visit[0][1] > spawn[1])]
                               
        # Should never reach this      
        return []
        

#------------------------------------------------------------------------------#

#     def get_den_corners(self):

#         ulc = self.ghosts_den[0]
#         urc = self.ghosts_den[0]
#         llc = self.ghosts_den[0]
#         lrc = self.ghosts_den[0]
#         for c in self.ghosts_den[1:]:
#             # upper left corner
#             if c[0] < ulc[0] and c[1] < ulc[1]:
#                 ulc = c
#             # upper right corner
#             if c[0] > urc[0] and c[1] < urc[1]:
#                 urc = c
#             # lower left corner
#             if c[0] < llc[0] and c[1] > llc[1]:
#                 llc = c
#             # lower righ corner
#             if c[0] > lrc[0] and c[1] > lrc[1]:
#                 lrc = c
        
#         return ulc, urc, llc, lrc

# # #------------------------------------------------------------------------------#

#     def get_den_interior(self):

#         ulc, urc, llc, lrc = self.get_den_corners()

#         x = ulc[0]+1
#         y = ulc[1]+1
#         interior = []
#         while x < lrc[0]:
#             while y < lrc[1]:
#                 interior += [[x,y]]
#                 y = y+1
#             x = x+1

#         return interior
#------------------------------------------------------------------------------#

    #* ##########   TESTED AND VERIFIED   ##########
    def create_corridors(self, pathways, crossroads):
        """Creates a list with all adjacencies of coordinates that are not walls
        Uses two cycles for horizontal and vertical adjacencies for efficiency
        purposes

        Args:
        pathways: a tuple of list of the coordinates that are not walls

        Returns: A tuple with 2 lists
        adjacencies: list with pairs of adjacent coordinates
        corridors: list with groups of horizontal and vertical Corridors
        """

        pathways_hor, pathways_ver = pathways
        corridors = []
        tunnel_points = []

        # horizontal search
        [x,y] = pathways_hor[0]
        corridor = [[x,y]]
        i = 0
        for i in range(1,len(pathways_hor)):

            [a,b] = pathways_hor[i]

            # check for row change (coordinates are not adjacent)
            if b != y:
                if len(corridor) > 1: # length 1 is a section of a vertical corridor
                    corridors += [corridor]
                corridor = [[a,b]]
                [x,y] = [a,b]
                continue

            # if horizontally adjacent, add to current horizontal corridor
            if a == x+1:
                corridor += [[a,b]]
                if [a,b] in crossroads:
                    corridors += [corridor]
                    corridor = [[a,b]]
            else:
                if len(corridor) > 1: # length 1 is a section of a vertical corridor
                    corridors += [corridor]
                corridor = [[a,b]]

            # check for spherical map adjacencies
            if a == self.map_.hor_tiles-1:
                [i,j] = [ [i,j] for [i,j] in pathways_hor if i == 0 and j == b ][0]
                tunnel_points += [[i,j]]
                tunnel_points += [[a,b]]

            [x,y] = [a,b]
        
        # add last horizontal corridor
        if len(corridor) > 1:
            corridors += [corridor]

        # vertical search
        [x,y] = pathways_ver[0]
        corridor = [[x,y]]
        i = 0
        for i in range(1,len(pathways_ver)):

            [a,b] = pathways_ver[i]

            # check for column change (coordinates are not adjacent)
            if a != x:
                if len(corridor) > 1:
                    corridors += [corridor] # length 1 is a section of a horizontal corridor
                corridor = [[a,b]]
                [x,y] = [a,b]
                continue

            # if vertically adjacent, add to adjacencies, add to current
            # vertical corridor
            if b == y+1:
                corridor += [[a,b]]
                if [a,b] in crossroads:
                    corridors += [corridor]
                    corridor = [[a,b]]
            else:
                if len(corridor) > 1: # length 1 is a section of a vertical corridor
                    corridors += [corridor]
                corridor = [[a,b]]

            # check for spherical map adjacencies
            if b == self.map_.ver_tiles-1:
                [i,j] = [ [i,j] for [i,j] in pathways_ver if j == 0 and i == a ][0]
                tunnel_points += [[i,j]]
                tunnel_points += [[a,b]]

            [x,y] = [a,b]

        # add last vertical corridor
        if len(corridor) > 1:
            corridors += [corridor]        

        # connect corridors
        corridors = self.connect_corridors(corridors, tunnel_points, crossroads)

        return corridors

#------------------------------------------------------------------------------#

    #* ##########   TESTED AND VERIFIED   ##########
    def connect_corridors(self, corridors, tunnel_points, crossroads):
        """connects horizontal and vertical subcorridors that make up the
        same corridor

        Args:
        corridors: a list of horizontal and vertical subcorridors

        Returns:
        a list of complete corridors
        """

        # connect vertical and horizontal adjacent corridors
        connected = []
        while corridors != []:

            corr = corridors.pop()
            
            found = True
            while found:
                found = False
                end0 = corr[0]
                end1 = corr[len(corr)-1]
                for c in corridors[:]: # copy of list to allow removals while iterating

                    #if end0 == (0,_)

                    if end0 == c[0] and end0 not in crossroads:
                        corr = corr[::-1] + c[1:]
                        corridors.remove(c)
                        found = True
                        break
                    elif end0 == c[len(c)-1] and end0 not in crossroads:
                        corr = c + corr[1:]
                        corridors.remove(c)
                        found = True
                        break
                    elif end1 == c[0] and end1 not in crossroads:
                        corr = corr + c[1:]
                        corridors.remove(c)
                        found = True
                        break
                    elif end1 == c[len(c)-1] and end1 not in crossroads:
                        corr = c[0:len(c)-1] + corr[::-1]
                        corridors.remove(c)
                        found = True
                        break

            connected += [corr]

        # connect corridors that form a tunnel (spherical map)
        tunnels = self.find_tunnels(connected, tunnel_points)
        corridors = [ c for c in connected if c not in tunnels]
        tunnels = self.connect_tunnels(tunnels, crossroads)
        corridors += tunnels
        #corridors += connected

        return corridors

#------------------------------------------------------------------------------#

    #* ##########   TESTED AND VERIFIED   ##########
    def find_tunnels(self, corridors, tunnel_points):
        tunnels = [ corr for corr in corridors \
                            if corr[0] in tunnel_points \
                            or corr[len(corr)-1] in tunnel_points ]
        return tunnels

#------------------------------------------------------------------------------#

    #* ##########   TESTED AND VERIFIED   ##########
    def connect_tunnels(self, tunnels, crossroads):

        connected = []
        while tunnels != []:

            tun = tunnels.pop()
            
            if tun[0][0] == 0: # end 0, x coordinate
                o_tun = [tun for tun in tunnels if tun[len(tun)-1][0] == self.map_.hor_tiles-1]
                connected += [o_tun[0] + tun]
                tunnels.remove(o_tun[0])

            elif tun[len(tun)-1][0] == self.map_.hor_tiles -1: # end 0, x coordinate
                o_tun = [tun for tun in tunnels if tun[0][0] == 0]
                connected += [tun + o_tun[0]]
                tunnels.remove(o_tun[0])

            elif tun[0][1] == 0: # end 0, x coordinate
                o_tun = [tun for tun in tunnels if tun[len(tun)-1][1] == self.map_.ver_tiles-1]
                connected += [o_tun[0] + tun]
                tunnels.remove(o_tun[0])

            elif tun[len(tun)-1][1] == self.map_.ver_tiles -1: # end 0, x coordinate
                o_tun = [tun for tun in tunnels if tun[0][1] == 0]
                connected += [tun + o_tun[0]]
                tunnels.remove(o_tun[0])
        
        for corr in connected:
            hor = [x for [x,y] in corr]
            ver = [y for [x,y] in corr]
            if all([x == hor[0] for x in hor]):
                self.ver_tunnel_exists = True
            if all([y == ver[0] for y in ver]):
                self.hor_tunnel_exists = True

        return connected

#------------------------------------------------------------------------------#

    #* ##########   TESTED AND VERIFIED   ##########
    def create_corridor_adjacencies(self, corridors):
        """Creates pairs of adjacent corridors

        Args:
        corridors: a list of corridors

        Returns:
        a list of sorted tuples of adjacent corridors
        """
        corridor_adjacencies = []
        for i in range(len(corridors)):
            for j in range(i+1,len(corridors)):
                if (corridors[i].ends[0] == corridors[j].ends[0] \
                or corridors[i].ends[0] == corridors[j].ends[1] \
                or corridors[i].ends[1] == corridors[j].ends[0] \
                or corridors[i].ends[1] == corridors[j].ends[1]):
                    corridor_adjacencies += [ [corridors[i], corridors[j]] ]

        return corridor_adjacencies


    def calc_average_corridor_cost(self):
        sum = 0
        for corr in self.corridors:
            sum += corr.cost
        return sum / len(self.corridors)  
