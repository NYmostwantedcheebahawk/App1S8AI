# Class of the genetic algorithm for fighting the monster.
import os
import time
import numpy as np
import random
from Constants import *
import matplotlib.pyplot as plt

class TestPlayer:
    def __init__(self) -> None:
        self.attributes = []
    
    def set_attributes(self, newAttributes):
        self.attributes = newAttributes

class FightGA:
    def __init__(self, monster):
        # Constants
        self.num_attributes = NUM_ATTRIBUTES
        self.range_attributes = MAX_ATTRIBUTE

        # Hyperparameters
        self.mutation_prob = 0.01
        self.crossover_prob = 0.8
        self.rw_coef = 3
        self.pop_size = 850
        self.crossover_cutting_point = 5
        self.nbits = 11
        
        # Monster object
        self.monster = monster
        
        # Init
        self.bestAttributes = []
        self.bestAttributesFitness = (0, -100)
        self.current_gen = 0
        self.population = []
        self.fitness_vdata = []
        self.fitness_ndata = []
    
    def pop_init(self):
        # Initialization of random attributes
        self.attributes_values = [[random.randrange(-self.range_attributes, self.range_attributes) for _ in range(self.num_attributes)] for _ in range(self.pop_size)]

    def encode(self):
        # Encode population to binary from attributes values
        for individual in self.attributes_values:
            self.population.append([twos_complement(attribute, self.nbits) for attribute in individual])

    def decode(self):
        # Decode new population from binary to signed integers
        for j in range(self.pop_size):
            binary_attributes = self.population[j]
            self.attributes_values[j] = [twos_complement_decode(attribute) for attribute in binary_attributes]

    def do_test_fight(self, player):
        nb, val = self.monster.mock_fight(player)
        return nb, val
    
    def get_best_attributes(self):
        return self.bestAttributes
    
    def get_best_attributes_fitness(self):
        return self.bestAttributesFitness
    
    def set_attributes_score(self, val_score, rounds_won):
        self.attributes_val_score = val_score
        self.attributes_rounds_won = rounds_won

    def doSelection(self):
        # Select pairs of individuals from the population
        # Do manipulation on score values
        round_won_coef = [item * self.rw_coef for item in self.attributes_rounds_won]
        if any(value < 0 for value in self.attributes_val_score):
            fit_ratios = self.attributes_val_score + abs(min(self.attributes_val_score)) + 1 + round_won_coef
        else:
            fit_ratios = [self.attributes_val_score[i] + round_won_coef[i] for i in range(len(self.attributes_val_score))]
        
        # Select pairs
        selection_probs = np.array(fit_ratios) / sum(fit_ratios)
        pairs = []
        for _ in range(self.pop_size // 2):
            parent1 = np.random.choice(len(fit_ratios), p=selection_probs)
            second_sel_probs = np.delete(selection_probs, parent1)
            second_sel_probs /= sum(second_sel_probs)
            parent2 = np.random.choice(len(fit_ratios)-1, p=second_sel_probs)
            pairs.append((parent1, parent2))
        return pairs

    def doCrossover(self, pairs):
        # Perform a crossover operation between two individuals, with a given probability
        # and constraint on the cutting point
        new_pop = []

        for i in range(len(pairs)):
            parent1 = self.population[pairs[i][0]]
            parent2 = self.population[pairs[i][1]]
            if random.random() < self.crossover_prob: # do crossover for every attributes
                cross_point = random.randint(1, self.num_attributes - 1)
                #cross_point = self.crossover_cutting_point
                child1 = parent1[:cross_point] + parent2[cross_point:]
                child2 = parent2[:cross_point] + parent1[cross_point:]
                new_pop.append(child1)
                new_pop.append(child2)
            else:   # childs = parents
                new_pop.append(parent1)
                new_pop.append(parent2)

        self.population = new_pop

    def doMutation(self):
        # Perform a mutation operation over the entire population
        for i in range(self.pop_size):
            for j in range(self.num_attributes):
                if random.random() < self.mutation_prob:
                    attribute = self.population[i][j]

                    # Apply mutation to random bit on individual attributes
                    random_bit = random.randint(0, self.nbits - 1)
                    subsequence = list(attribute)
                    subsequence[random_bit] = '0' if subsequence[random_bit] == '1' else '1'
                    subsequence = ''.join(subsequence)
                    self.population[i][j] = subsequence

    def new_gen(self):
        # Perform a the pair selection, crossover and mutation and
        # generate a new population for the next generation
        pairs = self.doSelection()
        self.doCrossover(pairs)
        self.doMutation()
        self.current_gen += 1

    def main(self):
        start_time = time.time()
        player = TestPlayer()
        
        # Initialize GA
        self.pop_init()
        self.encode()

        while(self.current_gen < 500):
            val_results = np.zeros(self.pop_size)
            rounds_won = np.zeros(self.pop_size)
            for i, att in enumerate(self.attributes_values):
                player.set_attributes(att)
                n, v = self.do_test_fight(player)
                val_results[i] = v
                rounds_won[i] = n
            self.set_attributes_score(list(val_results), list(rounds_won))

            # If any mock fight returns 4 rounds won, stop search and return attributes
            if np.any(rounds_won == 4):
                index = int(np.where(rounds_won == 4)[0])
                best_rw = rounds_won[index]
                best_val = val_results[index]
                best_atts = self.attributes_values[index]
                self.bestAttributes = list(best_atts)
                self.bestAttributesFitness = (best_rw, best_score)
                self.fitness_ndata.append(best_rw)
                self.fitness_vdata.append(best_val)
                print(f"[New best] Gen_{self.current_gen} Fitness_{self.bestAttributesFitness}")
                print(f"Threshold reached in {time.time() - start_time} s")
                self.save_graph()
                return 0
            else:
                val_results = list(val_results)
                rounds_won = list(rounds_won)
                best_score = np.max(val_results)
                best_score_index = val_results.index(best_score)
                best_rw = rounds_won[best_score_index]
            
                if best_score > self.bestAttributesFitness[1]:
                    best_score_index = val_results.index(best_score)
                    best_run_atts = self.attributes_values[best_score_index]
                    best_rw = rounds_won[best_score_index]
                    self.bestAttributes = best_run_atts
                    self.bestAttributesFitness = (best_rw, best_score)
                    print(f"[New best] Gen_{self.current_gen} Fitness_{self.bestAttributesFitness}")
            
            # Append data for graph generation
            self.fitness_ndata.append(best_rw)
            self.fitness_vdata.append(best_score)
            
            # Generate new gen and decode binary
            self.new_gen()
            self.decode()

        print(f"Max gen reached. Time it took : {time.time() - start_time} s")
        self.save_graph()
        return 0
    
    def save_graph(self):
        fig, ax1 = plt.subplots(figsize=(8, 6))
        v = np.array(self.fitness_vdata)
        n = np.array(self.fitness_ndata)

        ax1.plot(v, color='b', label='v')
        ax1.set_xlabel('Generations')
        ax1.set_ylabel('Valeur cumul. de succès v', color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax2 = ax1.twinx()

        ax2.plot(n, color='r', label='n')
        ax2.set_ylabel('Nombre de round(s) remporté(s) n', color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc='upper left')

        plt.title('Performance algo. génétique')

        path = 'MonsterGraphs/'
        if not os.path.exists(path):
            os.makedirs(path)
        contenu = os.listdir(path)
        nb_file = len([f for f in contenu if os.path.isfile(os.path.join(path, f))])
        plt.savefig(path + 'graph-' + f'{nb_file}.png')


def twos_complement(n, nbits):
    if n < -1000 or n > 1000:
        raise ValueError("La valeur doit être comprise entre -1000 et 1000.")
    if n < 0:
        binary_str = bin(2**nbits + int(n))[2:]  # Encoder en complément à deux
    else:
        binary_str = bin(int(n))[2:].zfill(nbits)  # Positive, remplir de zéros à gauche
    return binary_str


def twos_complement_decode(binary_str):
    if binary_str[0] == '1':  # Le bit le plus significatif est 1 (nombre négatif)
        inverted_str = ''.join('1' if bit == '0' else '0' for bit in binary_str)
        decimal_value = -(int(inverted_str, 2) + 1)
    else:
        decimal_value = int(binary_str, 2)
    return decimal_value
