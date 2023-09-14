class BlockOnMap:
    def __init__(self, x, y, value, heuristics):
        self.x = x
        self.y = y
        self.value = value
        self.heuristics = heuristics

class BlockOnMapNode:
    def __init__(self, block_on_map, g_value, f_value, symbole, parent):
        self.block_on_map = block_on_map
        self.g_value = g_value
        self.f_value = f_value
        self.symbole = symbole
        self.parent = parent
