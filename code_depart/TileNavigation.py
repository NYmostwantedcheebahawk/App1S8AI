import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from pygame import Rect
from pygame.locals import *
from InLinePlanning.BlockOnMap import *

#class FuzzyNavigation:
#    def __init__(self):
#        right_wall_dist = ctrl.Antecedent(np.arange(0, 1, 0.1), "right_wall_dist")
#        left_wall_dist = ctrl.Antecedent(np.arange(0, 1, 0.1), "left_wall_dist")
#        direction = ctrl.Consequent(np.arange(-90, 90, 1), "direction", defuzzify_method='centroid')
#        direction.accumulation_method = np.fmax
#
#        right_wall_dist.automf(3)
#        left_wall_dist.automf(3)
#
#        direction['left'] = fuzz.trimf(direction.universe, [-90, -90, -45])
#        direction['left_front'] = fuzz.trimf(direction.universe, [-45, 0, 0])
#        direction['front'] = fuzz.trimf(direction.universe, [-45, 0, 45])
#        direction['right_front'] = fuzz.trimf(direction.universe, [0, 0, 45])
#        direction['right'] = fuzz.trimf(direction.universe, [45, 90, 90])
#        left_wall_dist.view()
#
#FuzzyNavigation()

def _is_inside(rect1, rect2):
    return rect1.left >= rect2.left and rect1.right <= rect2.right and rect1.top >= rect2.top and rect1.bottom <= rect2.bottom

class TileNavigation:
    def __init__(self, player, tile_shape, obstacle_avoidance, send_key):
        self._player = player
        self._tile_shape = np.array(tile_shape)
        self._obstacle_avoidance = obstacle_avoidance
        self._send_key = send_key
        self._path = []
        self._path_progress = 0

    def set_path(self, path):
        self._path = []
        temp_tile = None
        for tile in path:
            if temp_tile is None:
                temp_tile = tile
                self._path.append(tile)
            elif temp_tile != tile:
                self._path.append(tile)
            temp_tile = tile
        self._path_progress = 0

    def step(self):
        self._handle_tile_change()
        next_tile_index = self._get_next_tile_index()
        current_tile_index = self._path[self._path_progress]
        if current_tile_index == next_tile_index:
            return

        target_direction = 0
        if current_tile_index[0] < next_tile_index[0]:
            target_direction = K_RIGHT
        elif current_tile_index[0] > next_tile_index[0]:
            target_direction = K_LEFT
        elif current_tile_index[1] < next_tile_index[1]:
            target_direction = K_DOWN
        elif current_tile_index[1] > next_tile_index[1]:
            target_direction = K_UP
        key_presses = self._obstacle_avoidance.get_keypress(target_direction)
        for key_press in set(key_presses):
            self._send_key(key_press)

    def _tile_index_to_floor_tile(self, tileIndex2d):
        top_left = self._tile_shape * tileIndex2d
        return Rect(top_left[0], top_left[1], self._tile_shape[0], self._tile_shape[1])
    
    def _get_next_tile_index(self):
        next_tile_index = self._path_progress + 1
        if next_tile_index < len(self._path):
            return self._path[next_tile_index]
        else:
            return self._path[self._path_progress]

    def _handle_tile_change(self):
        player_rect = self._player.get_rect()
        next_tile_index = self._get_next_tile_index()
        current_tile_index = self._path[self._path_progress]
        if current_tile_index == next_tile_index:
            return
        next_floor_tile = self._tile_index_to_floor_tile(next_tile_index)
        if _is_inside(player_rect, next_floor_tile):
            self._path_progress += 1
