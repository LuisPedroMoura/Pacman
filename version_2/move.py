class Move:

    def __init__(self, target, cost, target_path_to_pacman):
        self.target = target
        self.cost = cost
        self.path_to_target = list(reversed(target_path_to_pacman))
        self.next_node = self.path_to_target[1] if len(self.path_to_target) > 1 else None
        self.ghost_in_position = self.calculate_ghost_in_position()
        self.ghost_in_path = True if self.ghost_in_position != None else False
        self.danger_cost = 0


    def calculate_ghost_in_position(self):
        for i in range(len(self.path_to_target)):
            if self.path_to_target[i].is_ghost:
                return i
        return None

    def __str__(self):
        return 'MOVE: danger cost is '+str(self.danger_cost)+' and move target is '+str(self.target)

    def __repr__(self):
        return self.__str__()