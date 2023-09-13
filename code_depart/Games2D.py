from collections import deque

from pygame.locals import *
import pygame
from ObstacleAvoidance import ObstacleAvoidance
from Player import *
from Maze import *
from Constants import *
from BlockOnMap import *
from AStar import *
from Prolog.EgnimaSolver import *


class App:
    windowWidth = WIDTH
    windowHeight = HEIGHT
    player = 0

    def __init__(self, mazefile):
        self._running = True
        self._win = False
        self._dead = False
        self._display_surf = None
        self._clock = None
        self._image_surf = None
        self.level = 0
        self.score = 0
        self.timer = 0.0
        self.player = Player()
        self.maze = Maze(mazefile)
        self._obstacle_avoidance = ObstacleAvoidance(self.player)

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._obstacle_avoidance.set_display_surface(self._display_surf)
        self._clock = pygame.time.Clock()
        pygame.display.set_caption("Dungeon Crawler")
        pygame.time.set_timer(pygame.USEREVENT, 10)
        self._running = True
        self.maze.make_maze_wall_list()
        self.maze.make_maze_item_lists()
        self._image_surf = pygame.image.load("assets/Images/knight.png")
        self.player.set_position(self.maze.start[0], self.maze.start[1])
        self.player.set_size(PLAYER_SIZE*self.maze.tile_size_x, PLAYER_SIZE*self.maze.tile_size_x)
        self._image_surf = pygame.transform.scale(self._image_surf, self.player.get_size())
        self.enigma_solver = EnigmaSolver()
        self.path = []
        self.visited = []
        self.values = ['C','T']
        self.allowed_deviation = 1000
        self.on_side_path = False

    def on_keyboard_input(self, keys):
        perception_list = self.maze.make_perception_list(self.player, self._display_surf)
        self._obstacle_avoidance.set_perception_list(perception_list)

        obstacle_avoidance_keys = []
        if keys[K_RIGHT] or keys[K_d]:
            obstacle_avoidance_keys = self._obstacle_avoidance.get_keypress(K_RIGHT)
        elif keys[K_LEFT] or keys[K_a]:
            obstacle_avoidance_keys = self._obstacle_avoidance.get_keypress(K_LEFT)
        elif keys[K_UP] or keys[K_w]:
            obstacle_avoidance_keys = self._obstacle_avoidance.get_keypress(K_UP)
        elif keys[K_DOWN] or keys[K_s]:
            obstacle_avoidance_keys = self._obstacle_avoidance.get_keypress(K_DOWN)

        for avoidance_key in obstacle_avoidance_keys:
            if (avoidance_key == K_RIGHT):
                self.move_player_right()
            if (avoidance_key == K_LEFT):
                self.move_player_left()
            if (avoidance_key == K_UP):
                self.move_player_up()
            if (avoidance_key == K_DOWN):
                self.move_player_down()

        # Utility functions for AI
        if keys[K_p]:
            self.maze.make_perception_list(self.player, self._display_surf, visualize=True)
            # returns a list of 5 lists of pygame.rect inside the perception radius
            # the 4 lists are [wall_list, obstacle_list, item_list, monster_list, door_list]
            # item_list includes coins and treasure

        if keys[K_m]:
            for monster in self.maze.monsterList:
                print(monster.mock_fight(self.player))
            # returns the number of rounds you win against the monster
            # you need to win all four rounds to beat it

        if keys[K_SPACE]:
            env = self.maze.look_at_door(self.player, self._display_surf)
            print(env)
            self.enigma_solver.__set_enigma_state__(env)
            # returns the state of the doors you can currently see
            # you need to unlock it by providing the correct key

        if keys[K_u]:
            self.maze.unlock_door(self.enigma_solver.__solve_enigma__())
            # returns true if the door is unlocked, false if the answer is incorrect and the door remains locked
            # if the door is unlocked you can pass through it (no visible change... yet)

        if (keys[K_ESCAPE]):
            self._running = False

    # FONCTION À Ajuster selon votre format d'instruction
    def on_AI_input(self, instruction):
        if instruction == 'RIGHT':
            self.move_player_right()

        if instruction == 'LEFT':
            self.move_player_left()

        if instruction == 'UP':
            self.move_player_up()

        if instruction == 'DOWN':
            self.move_player_down()

    def on_collision(self):
        return self.on_wall_collision() or self.on_obstacle_collision() or self.on_door_collision()

    def move_player_right(self):
        self.player.moveRight()
        if self.on_collision():
            self.player.moveLeft()

    def move_player_left(self):
        self.player.moveLeft()
        if self.on_collision():
            self.player.moveRight()

    def move_player_up(self):
        self.player.moveUp()
        if self.on_collision():
            self.player.moveDown()

    def move_player_down(self):
        self.player.moveDown()
        if self.on_collision():
            self.player.moveUp()

    def on_wall_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.wallList)
        if not collide_index == -1:
            # print("Collision Detected!")
            return True
        return False

    def on_obstacle_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.obstacleList)
        if not collide_index == -1:
            # print("Collision Detected!")
            return True
        return False

    def on_coin_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.coinList)
        if not collide_index == -1:
            self.maze.coinList.pop(collide_index)
            return True
        else:
            return False

    def on_treasure_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.treasureList)
        if not collide_index == -1:
            self.maze.treasureList.pop(collide_index)
            return True
        else:
            return False

    def on_monster_collision(self):
        for monster in self.maze.monsterList:
            if self.player.get_rect().colliderect(monster.rect):
                return monster
        return False

    def on_door_collision(self):
        for door in self.maze.doorList:
            if self.player.get_rect().colliderect(door.rect):
                return True
        return False

    def on_exit(self):
        return self.player.get_rect().colliderect(self.maze.exit)

    def maze_render(self):
        self._display_surf.fill((0, 0, 0))
        self.maze.draw(self._display_surf)
        font = pygame.font.SysFont(None, 32)
        text = font.render("Coins: " + str(self.score), True, WHITE)
        self._display_surf.blit(text, (WIDTH - 120, 10))
        text = font.render("Time: " + format(self.timer, ".2f"), True, WHITE)
        self._display_surf.blit(text, (WIDTH - 300, 10))

    def on_render(self):
        self.maze_render()
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        pygame.display.flip()

    def on_win_render(self):
        self.maze_render()
        font = pygame.font.SysFont(None, 120)
        text = font.render("CONGRATULATIONS!", True, GREEN)
        self._display_surf.blit(text, (0.1 * self.windowWidth, 0.4 * self.windowHeight))
        pygame.display.flip()

    def on_death_render(self):
        self.maze_render()
        font = pygame.font.SysFont(None, 120)
        text = font.render("YOU DIED!", True, RED)
        self._display_surf.blit(text, (0.1 * self.windowWidth, 0.4 * self.windowHeight))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

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

    def on_execute(self):
        self.on_init()
        # get the matrix of the maze
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
        self.path = []
        current_path = path
        while current_path.parent != None:
            self.path.append(current_path)
            current_path = current_path.parent
        self.path.append(current_path)

        print(len(self.path))
        while len(self.path) > 0:
            current_node = self.path.pop()
            print(str(current_node.block_on_map.x) + str(current_node.block_on_map.y) )
            if (len(self.path)  == 0 and self.on_side_path) or not self.on_side_path:
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
                    self.path = possible_paths[min_index]
                    current_path = path
                    self.visited.append(path.block_on_map)
                    self.path = []
                    while current_path.parent != None:
                        self.path.append(current_path)
                        current_path = current_path.parent
                    self.path.append(current_path)
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
                    self.path = []
                    current_path = path
                    while current_path.parent != None:
                        self.path.append(current_path)
                        current_path = current_path.parent
                    self.path.append(current_path)
        for vis in self.visited:
            print(str(vis.x) + str(vis.y))
        while self._running:
            self._clock.tick(GAME_CLOCK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.USEREVENT:
                    self.timer += 0.01
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            self.on_keyboard_input(keys)
            # self.on_AI_input(instruction)
            if self.on_coin_collision():
                self.score += 1
            if self.on_treasure_collision():
                self.score += 10
            monster = self.on_monster_collision()
            if monster:
                if monster.fight(self.player):
                    self.maze.monsterList.remove(monster)
                    self.score += 50
                else:
                    self._running = False
                    self._dead = True
            if self.on_exit():
                self._running = False
                self._win = True
            self.on_render()

        while self._win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._win = False
            self.on_win_render()

        while self._dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._dead = False
            self.on_death_render()

        self.on_cleanup()
