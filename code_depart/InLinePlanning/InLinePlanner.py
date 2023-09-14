from InLinePlanning.AStar import AStar
from InLinePlanning.BlockOnMap import BlockOnMap



class InLinePlanner:
    def __init__(self, maze, allowed_deviation):
        self.maze = maze
        self.path_temp = []
        self.path = []
        self.visited = []
        self.values = ['C','T']
        self.allowed_deviation = allowed_deviation
        self.on_side_path = False

    def define_coordinates_value_heuristics(self, maze_matrix):
        end_x, end_y = None, None
        for y, row in enumerate(maze_matrix):
            for x, value in enumerate(row):
                if value == 'E':
                    end_x, end_y = x, y
                    break

        # Initialize BlockOnMap objects and calculate heuristics
        block_objects = []
        if end_x is not None and end_y is not None:
            for y, row in enumerate(maze_matrix):
                for x, value in enumerate(row):
                    if value != '1':
                        heuristic = abs(x - end_x) + abs(y - end_y)
                        block = BlockOnMap(x, y, value, heuristic)
                        block_objects.append(block)
        return block_objects

    def __in_line_planning__(self):
        blocks_on_map = self.define_coordinates_value_heuristics(self.maze.maze)
        start_block = None
        end_block = None
        for block in blocks_on_map:
            if block.value == 'S':
                start_block = block
            elif block.value == 'E':
                end_block = block
        if start_block and end_block:
            astar = AStar(blocks_on_map)
            path = astar.astar(start_block, end_block)
        self.path_temp = []
        current_path = path
        while current_path.parent != None:
            self.path_temp.append(current_path)
            current_path = current_path.parent
        self.path_temp.append(current_path)
        self.path.append(self.path_temp)
        #print(len(self.path_temp))
        while len(self.path_temp) > 0:
            current_node = self.path_temp.pop()
            #print(str(current_node.block_on_map.x) + str(current_node.block_on_map.y) )
            if (len(self.path_temp) == 0 and self.on_side_path) or not self.on_side_path:
                costs = []
                possible_paths = []
                for block in blocks_on_map:
                    if block.value in self.values and not (block in self.visited):
                        if current_node and block:
                            astar = AStar(blocks_on_map)
                            path = astar.astar(current_node.block_on_map, block)
                            possible_paths.append(path)
                            costs.append(path.f_value)
                if len(costs) > 0 and  min(costs) < self.allowed_deviation:
                    min_index = costs.index(min(costs))
                    self.on_side_path = True
                    self.path_temp = possible_paths[min_index]
                    current_path = path
                    self.visited.append(path.block_on_map)
                    self.path_temp = []
                    while current_path.parent != None:
                        self.path_temp.append(current_path)
                        current_path = current_path.parent
                    self.path_temp.append(current_path)
                    self.path.append(self.path_temp)
                elif self.on_side_path:
                    self.on_side_path = False
                    for block in blocks_on_map:
                        if block == current_node.block_on_map:
                            start_block = block
                        elif block.value == 'E':
                            end_block = block

                    if start_block and end_block:
                        astar = AStar(blocks_on_map)
                        path = astar.astar(start_block, end_block)
                    self.path_temp = []
                    current_path = path
                    while current_path.parent != None:
                        self.path_temp.append(current_path)
                        current_path = current_path.parent
                    self.path_temp.append(current_path)
                    self.path.append(self.path_temp)

        self.path = [self.path[i] for i in range(len(self.path)) if i == 0 or self.path[i] != self.path[i - 1]]
        self.path[0].append(self.path[0][len(self.path[0])-1].parent)
        return self.path


