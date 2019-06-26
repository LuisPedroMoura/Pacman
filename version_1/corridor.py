from game_consts import CORRIDOR_SAFETY

class Corridor():
    """Represents an uninterrupted path of adjacent coordinates with a
    crossroad at each end

    Args:
        coordinates: list of coordinates of the Corridor

    Attr:
        coordinates: list of coordinates of the Corridor
        length: length of coordinates without crossroad ends
        cost: distance of going through the Corridor from one crossroad
              to the other
        ends: the two exit coordinates of the Corridor
        safe: Enumerate CORRIDOR_SAFETY where UNSAFE means a ghost is inside the Corridor
              and SAFE means that no ghost is inside the Corridor 
    """

    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.length = len(coordinates) - 2 if len(coordinates) > 1 else 0
        self.cost = len(coordinates) - 1
        self.ends = [coordinates[0], coordinates[-1]]
        self.safe = CORRIDOR_SAFETY.SAFE
        
    def dist_end0(self, coord):
        return len(self.coordinates[:self.coordinates.index(coord)])

    def dist_end1(self, coord):
        return len(self.coordinates[self.coordinates.index(coord)+1:])

    def dist_to_end(self, coord, end):
        if end == self.ends[0]:
            return self.dist_end0(coord)
        return self.dist_end1(coord)

    def dist_between_coords(self, coord1, coord2):
        if coord1 not in self.coordinates or coord2 not in self.coordinates:
            return None
        return abs(self.coordinates.index(coord1)-self.coordinates.index(coord2))

    def get_other_end(self,end):
        if end == self.ends[0]:
            return self.ends[1]
        elif end == self.ends[1]:
            return self.ends[0]
        else:
            return None

    def closest_end(self, coord):
        return self.dist_end0(coord) \
            if self.dist_end0(coord) <= self.dist_end1(coord) \
            else self.dist_end1(coord)

    def sub_corridors(self, coord):
        """Creates two Corridors spliting this coordinates at the given
        coordinate. The coordinate will be the end of both new Corridors

        Args:
            coord: coordinate where to split Corridor

        Returns:
            tuple with two new Corridor objects where 'coord' will be the end0 of
            one and end1 of the other
        """
        index = self.coordinates.index(coord)
        return Corridor(self.coordinates[:index+1]), Corridor(self.coordinates[index:])

    def get_coord_next_to_end0(self):
        if len(self.coordinates) > 1:
            return self.coordinates[1]
        else:
            return None

    def get_coord_next_to_end1(self):
        if len(self.coordinates) > 1:
            return self.coordinates[-2]
        else:
            return None

    def get_coord_next_to_end(self, end):
        if end == self.ends[0]:
            return self.get_coord_next_to_end0()
        elif end == self.ends[1]:
            return self.get_coord_next_to_end1()
        else:
            return None

    def get_next_coord_to_the_side_of_crossroad(self, initial, crossroad):
        """Given any initial coordinate, calculates the adjacent coordinate
        to the side of given Crossroad

        Args:
            initial: coordinate from where to get adjacent
            crossroad: the crossroad in the side of Corridor, of the coordinate
            wanted

        Returns:
            the coordinate adjacent to 'initial' in the side of 'crossroad'
            returns None if initial == crossroad or if given values are no valid
        """
        # verify that crossroad exists
        if crossroad == None:
            return None

        # calculate index of 'initial'
        initial_index = None
        for i in range(len(self.coordinates)):
            if initial == self.coordinates[i]:
                initial_index = i
                break
        
        if initial_index == None or initial == crossroad:
            return None

        # calculate adjacent coordinate
        if crossroad == self.ends[0]:
            return self.coordinates[initial_index-1]
        elif crossroad == self.ends[1]:
            return self.coordinates[initial_index+1]
        else:
            return None

    def __str__(self):
        return 'corr<' + str(self.coordinates) + '>'

    def __repr__(self):
        return self.__str__()