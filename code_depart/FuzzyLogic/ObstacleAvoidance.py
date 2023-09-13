from pygame.locals import *
import numpy as np
import pygame
from pygame import Rect
from Player import Player
from Constants import *

def opposite_direction(direction):
    if direction == K_DOWN:
        return K_UP
    if direction == K_UP:
        return K_DOWN
    if direction == K_LEFT:
        return K_RIGHT
    if direction == K_RIGHT:
        return K_LEFT

class ObstacleAvoidance:
    def __init__(self, player: Player):
        self._display_surface = None
        self.show_corridor_debug = True
        self.show_obstacle_debug = True
        self._tile_size = 0
        self._player = player
        self._wall_list = []
        self._obstacle_list = []
        self._item_list = []
        self._monster_list = [] 
        self._door_list = []

    def set_perception_list(self, perception_list: []):
        self._wall_list = perception_list[0]
        self._obstacle_list = perception_list[1]
        self._item_list = perception_list[2]
        self._monster_list = perception_list[3]
        self._door_list = perception_list[4]

    def set_display_surface(self, display_surface):
        self._display_surface = display_surface

    #def get_keypress(self, target_direction):
    #    # TODO: compute navigation direction based on current and next navigation blocks.
    #    corridor_walls = self._find_corridor(target_direction)
    #    if self.show_corridor_debug:
    #        self._visualize_corridor(corridor_walls, target_direction)
    #    obstacles_in_path = self._collisions_in_path(target_direction, self._obstacle_list, corridor_walls, should_avoid=True)
    #
    #    keypresses = [target_direction]
    #    if len(obstacles_in_path):
    #        avoidance_keypress = self._avoid_collision(target_direction, corridor_walls, obstacles_in_path[0])
    #        keypresses.append(avoidance_keypress)
    #    elif len(self._item_list):
    #        aim_keypresses = self._aim_collider(self._item_list[0])
    #        [keypresses.append(aim_keypress) for aim_keypress in aim_keypresses]
    #    return keypresses

    def _find_corridor(self, target_direction):

        is_vertical_direction = target_direction[1] == 1
        player_position = self._player.get_position()
        # List of X values if vertical corridor, Y values if horizontal.
        # First value corresponds to left/bottom coordinate (depending on the corridor direction), the second is the right/top.
        corridor_walls = [None, None]
        for tile in self._wall_list:
            wall_pos_along_dim = np.array([-1,-1])
            player_pos_along_dim = -1
            if is_vertical_direction:
                # only check corridor distances along X.
                wall_pos_along_dim[0] = tile.left
                wall_pos_along_dim[1] = tile.right
                player_pos_along_dim = player_position[0]
            else:
                # only check corridor distances along Y.
                wall_pos_along_dim[0] = tile.bottom
                wall_pos_along_dim[1] = tile.top
                player_pos_along_dim = player_position[1]
            closest_wall_index = np.argmin(np.array(np.abs(wall_pos_along_dim - player_pos_along_dim)))
            closest_wall_along_dim = wall_pos_along_dim[closest_wall_index]
            # Assing the corridor wall coordinate depending on its position around the player.
            corridor_wall_test = closest_wall_along_dim > player_pos_along_dim 
            corridor_wall_idx = corridor_wall_test if is_vertical_direction else not corridor_wall_test
            corridor_walls[corridor_wall_idx] = closest_wall_along_dim
        return corridor_walls

    def _collisions_in_path(self, target_direction, should_avoid):
        player_rect = self._player.get_rect()
        colliders_in_path = []
        for collider in self._obstacle_list:
            # Check if the collider is in the direction of motion
            is_in_front = False
            if target_direction == K_UP:
                is_in_front = player_rect.top >= collider.bottom
            elif target_direction == K_DOWN:
                is_in_front = player_rect.bottom <= collider.top
            elif target_direction == K_LEFT:
                is_in_front = player_rect.left >= collider.right
            elif target_direction == K_RIGHT:
                is_in_front = player_rect.right <= collider.left
            if not is_in_front:
                continue

            # Check if the movement of the player will intersect with the collider in it's path.
            avoid_without_moving = False
            if target_direction == K_UP or target_direction == K_DOWN:
                avoid_without_moving |= player_rect.left > collider.right
                avoid_without_moving |= player_rect.right < collider.left
            else:
                avoid_without_moving |= player_rect.bottom < collider.top
                avoid_without_moving |= player_rect.top > collider.bottom
            if avoid_without_moving and should_avoid:
                continue

            distance_to_obstacle = -1
            if target_direction == K_UP:
                distance_to_obstacle = abs(player_rect.top - collider.bottom)
            elif target_direction == K_DOWN:
                distance_to_obstacle = abs(player_rect.bottom - collider.top)
            elif target_direction == K_LEFT:
                distance_to_obstacle = abs(player_rect.left - collider.right)
            elif target_direction == K_RIGHT:
                distance_to_obstacle = abs(player_rect.right - collider.left)
            colliders_in_path.append([distance_to_obstacle, collider])

        if len(colliders_in_path) == 0:
            return []
        # Sort by distance.
        colliders_in_path.sort(key=lambda x: x[0])
        # Return obstacles only.
        return colliders_in_path

    #def _avoid_collision(self, target_direction, corridor, collider):
    #    player_rect = self._player.get_rect()
    #    avoidance_direction = 0
    #    affinity_bias = 3
    #    if target_direction in [K_UP, K_DOWN]:
    #        left_affinity = abs(collider.right - player_rect.left) + affinity_bias > abs(collider.left - player_rect.right)
    #        can_avoid_left = True
    #        can_avoid_right = True
    #        if corridor[0]: # Left wall
    #            can_avoid_left = abs(collider.left - corridor[0]) >= player_rect.width
    #        if corridor[1]: # Right wall
    #            can_avoid_right = abs(collider.right - corridor[1]) >= player_rect.width
    #
    #        if left_affinity and can_avoid_left:
    #            avoidance_direction = K_LEFT
    #        elif not left_affinity and can_avoid_right:
    #            avoidance_direction = K_RIGHT
    #        elif not left_affinity and not can_avoid_right and can_avoid_left:
    #            avoidance_direction = K_LEFT
    #        elif left_affinity and not can_avoid_left and can_avoid_right:
    #            avoidance_direction = K_RIGHT
    #    else:
    #        down_affinity = abs(collider.top - player_rect.bottom) + affinity_bias > abs(collider.bottom - player_rect.top)
    #        can_avoid_down = True
    #        can_avoid_up = True
    #        if corridor[0]: # Bottom Wall
    #            can_avoid_down = abs(collider.bottom - corridor[0]) >= player_rect.height
    #        if corridor[1]: # Top Wall
    #            can_avoid_up = abs(collider.top - corridor[1]) >= player_rect.height
#
    #        if down_affinity and can_avoid_down:
    #            avoidance_direction = K_DOWN
    #        elif not down_affinity and can_avoid_up:
    #            avoidance_direction = K_UP
    #        elif not down_affinity and not can_avoid_up and can_avoid_down:
    #            avoidance_direction = K_DOWN
    #        elif down_affinity and not can_avoid_down and can_avoid_up:
    #            avoidance_direction = K_UP
    #    if self.show_obstacle_debug:
    #        self._visualize_collision_planning(collider, None, RED)
    #    return self._check_secondary_collision(avoidance_direction, collider)
#
    #def _check_secondary_collision(self, avoidance_direction, collider):
    #    player_rect = self._player.get_rect()
    #    colliders_in_path = self._collisions_in_path(avoidance_direction, self._obstacle_list, [None, None], should_avoid=True)
    #    for collider_in_path in colliders_in_path:
    #        should_replan = False
    #        if avoidance_direction == K_LEFT:
    #            if abs(collider.left - collider_in_path.right) < player_rect.width:
    #                should_replan = True
    #        elif avoidance_direction == K_RIGHT:
    #            if abs(collider.right - collider_in_path.left) < player_rect.width:
    #                should_replan = True
    #        elif avoidance_direction == K_DOWN:
    #            if abs(collider.bottom - collider_in_path.top) < player_rect.height:
    #                should_replan = True
    #        elif avoidance_direction == K_UP:
    #            if abs(collider.top - collider_in_path.bottom) < player_rect.height:
    #                should_replan = True
    #        if should_replan:
    #            if self.show_obstacle_debug:
    #                self._visualize_collision_planning(collider_in_path, None, YELLOW)
    #            return opposite_direction(avoidance_direction)
    #    return avoidance_direction
#
    #def _aim_collider(self, collider):
    #    player_rect = self._player.get_rect()
    #    epsillon = 4
    #    key_presses = []
    #    delta_x = player_rect.center[0] - collider.center[0]
    #    delta_y = player_rect.center[1] - collider.center[1]
    #    if delta_x > 0 and delta_x > epsillon:
    #        key_presses.append(K_LEFT)
    #    if delta_x < 0 and abs(delta_x) > epsillon:
    #        key_presses.append(K_RIGHT)
    #    if delta_y > 0 and delta_y > epsillon:
    #        key_presses.append(K_UP)
    #    if delta_y < 0 and abs(delta_y) > epsillon:
    #        key_presses.append(K_DOWN)
    #    return key_presses
#
    #def _visualize_corridor(self, corridor_walls, target_direction):
    #    if not self._display_surface:
    #        return
    #    player_position = self._player.get_position()
    #    display_line_lenght = 100
    #    if target_direction in [K_UP, K_DOWN]:
    #        flip = False
    #        if not corridor_walls[0] is None:
    #            wall_rect_left = Rect(corridor_walls[0], player_position[1] - int(display_line_lenght / 2), 2, display_line_lenght)
    #            pygame.draw.rect(self._display_surface, BLUE, wall_rect_left)
    #            flip = True
    #        if not corridor_walls[1] is None:
    #            wall_rect_right = Rect(corridor_walls[1], player_position[1] - int(display_line_lenght / 2), 2, display_line_lenght)
    #            pygame.draw.rect(self._display_surface, BLUE, wall_rect_right)
    #            flip = True
    #        if flip:
    #            pygame.display.flip()
    #    else:
    #        flip = False
    #        if not corridor_walls[0] is None:
    #            wall_rect_down = Rect(player_position[0] - int(display_line_lenght / 2), corridor_walls[0], display_line_lenght, 2)
    #            pygame.draw.rect(self._display_surface, BLUE, wall_rect_down)
    #            flip = True
    #        if not corridor_walls[1] is None:
    #            wall_rect_up = Rect(player_position[0] - int(display_line_lenght / 2), corridor_walls[1], display_line_lenght, 2)
    #            pygame.draw.rect(self._display_surface, BLUE, wall_rect_up)
    #            flip = True
    #        if flip:
    #            pygame.display.flip()
#
    #def _visualize_collision_planning(self, collider, target_location, color):
    #    if not self._display_surface:
    #        return
    #    pygame.draw.rect(self._display_surface, color, collider, 2)
    #    pygame.display.flip()