from BlockOnMap import BlockOnMapNode

class AStar:
    def __init__(self, blocks_on_map):
        self.blocks_on_map = blocks_on_map

    def get_neighbors(self, block):
        x, y = block.block_on_map.x, block.block_on_map.y
        neighbors = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            for neighbor in self.blocks_on_map:
                if neighbor.x == new_x and neighbor.y == new_y:
                    neighbors.append(BlockOnMapNode(neighbor, block.g_value+1, block.g_value+1+neighbor.heuristics, str(neighbor.x) + str(neighbor.y),block))
        return neighbors

    def astar(self, start):
        frontier = []

        frontier.append(BlockOnMapNode(start, 0, start.heuristics,str(start.x) + str(start.y),None))
        reached_state = []

        pursuing_node = frontier[0]
        while not(len(frontier) == 0):
            reached_state.append(pursuing_node.symbole)
            for node in frontier:
                if node.symbole in reached_state:
                    frontier.remove(node)

            if pursuing_node.block_on_map.value == "E":
                return pursuing_node

            neighbors = self.get_neighbors(pursuing_node)

            for neighbor in neighbors:
                if not neighbor.symbole in reached_state:
                    frontier.append(neighbor)
            if not(len(frontier) == 0):
                next_in_persuit = frontier[0]
                for node in frontier:
                    if node.f_value < next_in_persuit.f_value:
                        next_in_persuit = node
            else:
                break

            pursuing_node = next_in_persuit
        return None

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)
        return path