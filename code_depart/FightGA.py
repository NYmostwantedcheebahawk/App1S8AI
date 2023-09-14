# Class of the genetic algorithm for fighting the monster.
import numpy as np
import random
from Constants import *

class TestPlayer:
    def __init__(self) -> None:
        self.attributes = []
    
    def set_attributes(self, newAttributes):
        self.attributes = newAttributes

class FightGA:
    def __init__(self, monster):
        self.num_attributes = NUM_ATTRIBUTES
        self.range_attributes = MAX_ATTRIBUTE
        self.mutation_prob = 0.01
        self.crossover_prob = 0.8
        self.crossover_cutting_point = 43
        self.pop_size = 1500
        self.nbits = 11
        self.bestAttributes = []
        self.bestAttributesFitness = (0, -100)
        self.current_gen = 0

        self.monster = monster
        self.population = []
    
    def pop_init(self):
        # Initialization of random attributes
        self.attributes_values = [[random.randrange(-self.range_attributes, self.range_attributes) for _ in range(self.num_attributes)] for _ in range(self.pop_size)]
        #print(f"attributes : {self.attributes_values}")

    def encode(self):
        # Encode population from attributes values
        for attribute in self.attributes_values:
            binary_concatenated = ''.join([twos_complement(gene, self.nbits) for gene in attribute])
            self.population.append(binary_concatenated)
        #print(f"population : {self.population}")

    def decode(self):
        # Decode new population from binary to signed integers
        for j in range(self.pop_size):
            binary_concatenated = self.population[j]
            binary_substrings = [binary_concatenated[i:i+self.nbits] for i in range(0, len(binary_concatenated), self.nbits)]
            self.attributes_values[j] = [twos_complement_decode(substring) for substring in binary_substrings]
        #print(f"attributes : {self.attributes_values}")

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
        round_won_coef = [item for item in self.attributes_rounds_won]
        #print(f"{self.attributes_rounds_won}, {round_won_coef}")
        if any(value < 0 for value in self.attributes_val_score):
            fit_ratios = self.attributes_val_score + abs(min(self.attributes_val_score)) + 1 + round_won_coef
        else:
            fit_ratios = [self.attributes_val_score[i] + round_won_coef[i] for i in range(len(self.attributes_val_score))]
            #fit_ratios = self.attributes_val_score
        
        # Select pairs
        selection_probs = np.array(fit_ratios) / sum(fit_ratios)
        pairs = []
        for _ in range(self.pop_size // 2):
            parent1 = np.random.choice(len(fit_ratios), p=selection_probs)
            second_sel_probs = np.delete(selection_probs, parent1)
            second_sel_probs /= sum(second_sel_probs)
            parent2 = np.random.choice(len(fit_ratios)-1, p=second_sel_probs)
            pairs.append((parent1, parent2))
        #print(f"{pairs}")
        return pairs

    def doCrossover(self, pairs):
        # Perform a crossover operation between two individuals, with a given probability
        # and constraint on the cutting point
        new_pop = []
        for i in range(len(pairs)):
            sequence1 = list(self.population[pairs[i][0]])
            sequence2 = list(self.population[pairs[i][1]])
            if random.random() < self.crossover_prob: # do crossover for every attributes
                cross_point = random.randint(1, self.num_attributes - 1) * self.nbits
                #cross_point = self.crossover_cutting_point
                new_seq1 = sequence1[:cross_point] + sequence2[cross_point:]
                new_seq2 = sequence2[:cross_point] + sequence1[cross_point:]
                new_pop.append(''.join(new_seq1))
                new_pop.append(''.join(new_seq2))
            else:   # childs = parents
                new_pop.append(''.join(sequence1))
                new_pop.append(''.join(sequence2))
        
        #print(f"pop : {self.population}")
        #print(f"new pop : {new_pop}")
        self.population = new_pop

    def doMutation(self):
        # Perform a mutation operation over the entire population
        for i in range(self.pop_size):
            sequence = self.population[i]
            for j in range(0, len(self.population[i]), self.nbits):
                if random.random() < self.mutation_prob:
                    # Apply mutation to random bit on individual attributes
                    random_bit = random.randint(0, self.nbits - 1)
                    subsequence = list(sequence[j:j+self.nbits])
                    subsequence[random_bit] = '0' if subsequence[random_bit] == '1' else '1'
                    subsequence = ''.join(subsequence)
                    sequence = sequence[:j] + subsequence + sequence[j+self.nbits:]
            self.population[i] = sequence
        #print(f"population : {self.population}")

    def new_gen(self):
        # Perform a the pair selection, crossover and mutation and
        # generate a new population for the next generation
        pairs = self.doSelection()
        self.doCrossover(pairs)
        self.doMutation()
        self.current_gen += 1

    def main(self):
        player = TestPlayer()
        
        # Initialize GA
        self.pop_init()
        self.encode()

        while(self.current_gen < 1500):
            # Mock fights for every attributes in list
            val_results = []
            rounds_won = []
            for att in self.attributes_values:
                player.set_attributes(att)
                n, v = self.do_test_fight(player)
                val_results.append(v)
                rounds_won.append(n)
            self.set_attributes_score(val_results, rounds_won)
            
            best_score = np.max(val_results)
            if best_score > self.bestAttributesFitness[1]:
                best_score_index = val_results.index(best_score)
                best_run_atts = self.attributes_values[best_score_index]
                best_rw = rounds_won[best_score_index]
                self.bestAttributes = best_run_atts
                self.bestAttributesFitness = (best_rw, best_score)
                print(f"BEST : fitness = {self.bestAttributesFitness}, {self.bestAttributes}")

            if (self.bestAttributesFitness[0] == 4) and (self.bestAttributesFitness[1] >= 3.95):
                print(f"Threshold reached. n = {self.bestAttributesFitness[0]}, v = {self.bestAttributesFitness[1]}, atts : {self.bestAttributes}")
                return 0
            
            self.new_gen()
            self.decode()

        print("Max gen reached.")
        return 0


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
