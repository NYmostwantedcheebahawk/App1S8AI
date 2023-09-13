import numpy as np
import skfuzzy as fuzz
import math
from skfuzzy import control as ctrl

class FuzzyLogic():

    def __init__(self):
        self.fuzzyController = self.createFuzzyController()

    def createFuzzyController(self):
        # TODO: Create the fuzzy variables for inputs and outputs.
        # Defuzzification (defuzzify_method) methods for fuzzy variables:
        #    'centroid': Centroid of area
        #    'bisector': bisector of area
        #    'mom'     : mean of maximum
        #    'som'     : min of maximum
        #    'lom'     : max of maximum
        angularAntecedent = ctrl.Antecedent(np.linspace(-np.pi, np.pi, 1000), 'angularInput')
        positionAntecedent = ctrl.Antecedent(np.linspace(-4.8, 4.8, 1000), 'positionInput')
        # ant1 = ctrl.Antecedent(np.linspace(-1, 1, 1000), 'input1')
        # ant2 = ctrl.Antecedent(np.linspace(-1, 1, 1000), 'input2')
        cons1 = ctrl.Consequent(np.linspace(-5, 5, 1000), 'output1', defuzzify_method='centroid')

        # Accumulation (accumulation_method) methods for fuzzy variables:
        #    np.fmax
        #    np.multiply
        cons1.accumulation_method = np.fmax

        # TODO: Create membership functions
        angularAntecedent['angleleft'] = fuzz.trimf(angularAntecedent.universe, [-np.pi, -np.pi, (-np.pi * 0.5) / 90])
        angularAntecedent['anglecenter'] = fuzz.trimf(angularAntecedent.universe,[(-np.pi * 1) / 90, 0, (np.pi * 1) / 90])
        angularAntecedent['angleright'] = fuzz.trimf(angularAntecedent.universe, [(np.pi * 0.5) / 90, np.pi, np.pi])
        positionAntecedent['positionleft'] = fuzz.trimf(angularAntecedent.universe, [-4.8, -4.8, -0.05])
        positionAntecedent['positioncenter'] = fuzz.trimf(angularAntecedent.universe, [-0.1, 0, 0.1])
        positionAntecedent['positionright'] = fuzz.trimf(angularAntecedent.universe, [0.05, 4.8, 4.8])

        cons1['left'] = fuzz.trimf(cons1.universe, [-10, -10, -0.1])
        cons1['nomove'] = fuzz.trimf(cons1.universe, [-0.5, 0, 0.5])
        cons1['right'] = fuzz.trimf(cons1.universe, [0.1, 10, 10])

        # TODO: Define the rules.
        rules = []
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['angleleft'] & positionAntecedent['positionleft']),
                               consequent=cons1['left']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['anglecenter'] & positionAntecedent['positioncenter']),
                               consequent=cons1['nomove']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['angleright'] & positionAntecedent['positionright']),
                               consequent=cons1['right']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['angleleft'] & positionAntecedent['positioncenter']),
                               consequent=cons1['left']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['anglecenter'] & positionAntecedent['positionleft']),
                               consequent=cons1['nomove']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['angleright'] & positionAntecedent['positioncenter']),
                               consequent=cons1['right']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['angleleft'] & positionAntecedent['positionright']),
                               consequent=cons1['left']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['anglecenter'] & positionAntecedent['positionright']),
                               consequent=cons1['nomove']))
        rules.append(ctrl.Rule(antecedent=(angularAntecedent['angleright'] & positionAntecedent['positionleft']),
                               consequent=cons1['right']))

        # Conjunction (and_func) and disjunction (or_func) methods for rules:
        #     np.fmin
        #     np.fmax
        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        system = ctrl.ControlSystem(rules)
        sim = ctrl.ControlSystemSimulation(system)
        return sim


    def convertTileDirectionToGeneralDirection(self, tile1, tile2):
        x1 = tile1.blockOnMap.x
        y1 = tile1.blockOnMap.y
        x2 = tile2.blockOnMap.x
        y2 = tile2.blockOnMap.y
        x_angle = math.cos(x2-x1)
        y_angle = math.sin(y2-y1)
        return (x_angle, y_angle)

    def convertAngleOutputToKeyStroke(self):
        pass

    def processOutput(self, wallLeft, wallRight, wallTop, wallBottom, rock, general_direction ,gold):
        pass
