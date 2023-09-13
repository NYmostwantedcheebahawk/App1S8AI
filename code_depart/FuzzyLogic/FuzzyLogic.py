import numpy as np
import skfuzzy as fuzz
import math
from skfuzzy import control as ctrl
from FuzzyLogic.ObstacleAvoidance import ObstacleAvoidance
import pygame
from pygame.locals import *
import copy
class FuzzyLogic():

    def __init__(self,player, width, height):
        self.width = width
        self.height = height
        self.obstacle_avoidance = ObstacleAvoidance(player)
        self.player = player
        self.x = 0
        self.y = 0
        self.next_in_path = None
        self.current_tile = None
        self.next_tile = None
        self.path = []
        self.fuzzyController = self.createFuzzyController()

    def createFuzzyController(self):
        # TODO: Create the fuzzy variables for inputs and outputs.
        # Defuzzification (defuzzify_method) methods for fuzzy variables:
        #    'centroid': Centroid of area
        #    'bisector': bisector of area
        #    'mom'     : mean of maximum
        #    'som'     : min of maximum
        #    'lom'     : max of maximum
        playerDirection = ctrl.Antecedent(np.linspace(0, np.pi, 1000), 'directionInput')
        leftWallAntecedent = ctrl.Antecedent(np.linspace(0, self.width, 1000), 'leftWallInput')
        rightWallAntecedent = ctrl.Antecedent(np.linspace(0, self.width, 1000), 'rightWallInput')
        topWallAntecedent = ctrl.Antecedent(np.linspace(0, self.height, 1000), 'topWallInput')
        bottomWallAntecedent = ctrl.Antecedent(np.linspace(0, self.height, 1000), 'bottomWallInput')

        # ant1 = ctrl.Antecedent(np.linspace(-1, 1, 1000), 'input1')
        # ant2 = ctrl.Antecedent(np.linspace(-1, 1, 1000), 'input2')
        cons1 = ctrl.Consequent(np.linspace(0, 2*np.pi, 1000), 'output1', defuzzify_method='centroid')

        # Accumulation (accumulation_method) methods for fuzzy variables:
        #    np.fmax
        #    np.multiply
        cons1.accumulation_method = np.fmax

        # TODO: Create membership functions
        playerDirection['Up'] = fuzz.trimf(cons1.universe, [0, np.pi/2 , np.pi])
        playerDirection['Right'] = fuzz.trimf(cons1.universe, [0,0,np.pi])
        playerDirection['Left'] = fuzz.trimf(cons1.universe, [0,np.pi,np.pi])

        leftWallAntecedent['goRight'] = fuzz.trimf(leftWallAntecedent.universe, [0, 0, (self.width /2)])
        leftWallAntecedent['noMovement'] = fuzz.trimf(leftWallAntecedent.universe,[(self.width /2), self.width , self.width ])
        rightWallAntecedent['goLeft'] = fuzz.trimf(rightWallAntecedent.universe, [0, 0, (self.width /2)])
        rightWallAntecedent['noMovement'] = fuzz.trimf(rightWallAntecedent.universe, [(self.width /2), self.width , self.width ])
        topWallAntecedent['goDown'] = fuzz.trimf(topWallAntecedent.universe, [0, 0, self.height/2])
        topWallAntecedent['noMovement'] = fuzz.trimf(topWallAntecedent.universe, [self.height/2, self.height, self.height])
        bottomWallAntecedent['goUp'] = fuzz.trimf(bottomWallAntecedent.universe, [0, 0, self.height/2])
        bottomWallAntecedent['noMovement'] = fuzz.trimf(bottomWallAntecedent.universe, [self.height/2, self.height, self.height])

        cons1['Up'] = fuzz.trimf(cons1.universe, [0, np.pi/2, np.pi])
        cons1['Right'] = fuzz.trimf(cons1.universe, [0,0,np.pi])
        cons1['Left'] = fuzz.trimf(cons1.universe, [0,np.pi,np.pi])

        # TODO: Define the rules.
        rules = []

        rules.append(ctrl.Rule(antecedent=(leftWallAntecedent['goRight']),
                               consequent=cons1['Right']))
        rules.append(ctrl.Rule(antecedent=(leftWallAntecedent['noMovement'] & playerDirection['Up']),
                               consequent=cons1['Up']))
        rules.append(ctrl.Rule(antecedent=(rightWallAntecedent['goLeft']),
                               consequent=cons1['Left']))
        rules.append(ctrl.Rule(antecedent=(rightWallAntecedent['noMovement'] & playerDirection['Up']),
                               consequent=cons1['Up']))
        rules.append(ctrl.Rule(antecedent=(topWallAntecedent['noMovement'] & playerDirection['Right']),
                               consequent=cons1['Right']))
        rules.append(ctrl.Rule(antecedent=(topWallAntecedent['noMovement'] & playerDirection['Left']),
                               consequent=cons1['Left']))
        rules.append(ctrl.Rule(antecedent=(bottomWallAntecedent['goUp']),
                               consequent=cons1['Up']))
        rules.append(ctrl.Rule(antecedent=(bottomWallAntecedent['noMovement'] & playerDirection['Right']),
                               consequent=cons1['Right']))
        rules.append(ctrl.Rule(antecedent=(bottomWallAntecedent['noMovement'] & playerDirection['Left']),
                               consequent=cons1['Left']))
        # Conjunction (and_func) and disjunction (or_func) methods for rules:
        #     np.fmin
        #     np.fmax
        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        sim = ctrl.ControlSystemSimulation(system)
        return sim


    def set_path(self, path):
        self.next_in_path = len(path)-2
        self.path = copy.deepcopy(path)
        print(len(path))
    def set_original_coord(self, tile1, tile2):
        self.x = tile1.block_on_map.x
        self.y = tile1.block_on_map.y
        self.current_tile = tile1
        self.next_tile = tile2

    def getUltimatePosition(self):
        x = 0
        indexX = 0
        while x < self.player.x:
            x = x + self.width
            indexX = indexX + 1
        indexX = indexX - 1
        y = 0
        indexY = 0
        while y < self.player.y:
            y = y + self.height
            indexY =  indexY + 1
        indexY  = indexY - 1
        if indexX != self.x or indexY != self.y:
            self.x = indexX
            self.y = indexY
            self.current_tile = self.next_tile
            self.next_tile = self.path[self.next_in_path]
            self.next_in_path = self.next_in_path -1


    def prepareInputs(self, perception_list):
        self.getUltimatePosition()
        self.obstacle_avoidance.set_perception_list(perception_list)
        direction_tuple, target_direction = self.convertTileDirectionToGeneralDirection()
        corridors_array = self.obstacle_avoidance._find_corridor(direction_tuple)
        obstacles = self.obstacle_avoidance._collisions_in_path(target_direction, True)
        return self.processOutput(corridors_array[0], corridors_array[1], direction_tuple)

    def convertTileDirectionToGeneralDirection(self):
        x1 = self.current_tile.block_on_map.x
        y1 = self.current_tile.block_on_map.y
        x2 = self.next_tile.block_on_map.x
        y2 = self.next_tile.block_on_map.y
        x_angle = x2-x1
        y_angle = y2-y1
        if x_angle == 1:
            target_direction = K_RIGHT
        elif x_angle == -1:
            target_direction = K_LEFT
        elif y_angle == 1:
            target_direction = K_DOWN
        elif y_angle == -1 :
            target_direction = K_UP

        return (x_angle, y_angle), target_direction

    def convertAngleOutputToKeyStroke(self, output ,target_direction):
        key_stroke = []
        if output > 0 and output < np.pi:
            if target_direction[0] == -1:
                key_stroke.append(K_UP)
            else:
                key_stroke.append(K_DOWN)
        if output > (np.pi/2) and output < 3*np.pi/2:
            key_stroke.append(K_LEFT)
        if output > -np.pi/2 and output < np.pi/2:
            key_stroke.append(K_RIGHT)
        return key_stroke

    def processOutput(self, wall1, wall2, general_direction):
        if(wall1 == None):
            distance_from_wall1 = 53
        else:
            distance_from_wall1 = self.player.x - wall1
        if(wall2 == None):
            distance_from_wall2 = 53
        else:
            distance_from_wall2 = wall2 - self.player.x
        x_angle = general_direction[0]
        y_angle = general_direction[1]
        if x_angle == 1:
            target_direction = 0
        elif x_angle == -1:
            target_direction = np.pi
        elif y_angle == 1:
            target_direction = np.pi/2
        elif y_angle == -1:
            target_direction = np.pi/2

        self.fuzzyController.input['directionInput'] = target_direction
        if (target_direction == np.pi/2 or target_direction == 3*np.pi/2):
            self.fuzzyController.input['leftWallInput'] = distance_from_wall1
            self.fuzzyController.input['rightWallInput'] = distance_from_wall2
            self.fuzzyController.input['topWallInput'] = 60
            self.fuzzyController.input['bottomWallInput'] = 60
        if (target_direction == 0 or target_direction == np.pi):
            self.fuzzyController.input['topWallInput'] = distance_from_wall1
            self.fuzzyController.input['bottomWallInput'] = distance_from_wall2
            self.fuzzyController.input['leftWallInput'] = 53
            self.fuzzyController.input['rightWallInput'] = 53

        self.fuzzyController.compute()
        return self.convertAngleOutputToKeyStroke(self.fuzzyController.output['output1'], general_direction)


