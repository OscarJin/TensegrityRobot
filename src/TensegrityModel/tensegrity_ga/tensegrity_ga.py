import random
import numpy as np
from operator import attrgetter
import copy
from concurrent import futures


class Chromosome(object):
    """
    Chromosome class that encapsulates an individual's fitness and solution
    representation.
    """
    def __init__(self, genes):
        """Initialise the Chromosome"""
        self.genes = genes
        self.fitness = 0

    def __repr__(self):
        """Return initialised Chromosome representation in readable form.
        """
        return repr((self.fitness, self.genes))


class TensegGA(object):

    def __init__(
            self,
            strut_num,
            population_size=20,
            generations=100,
            tournament_size=3,
            maximize_fitness=True,
            random_state=None
    ):
        """
        Args:
            strut_num: number of struts
            population_size: number of candidate solutions in each generation
            generations: number of generations to evolve
            random_state: random seed. defaults to None
        """

        self._strut_num = strut_num
        self._node_num = 2 * strut_num
        self._link_num = 4 * strut_num
        self._cable_num = 3 * strut_num
        # original links, do not directly modify!
        self._links = np.empty(shape=(self._link_num, 2), dtype=int)
        for i in range(self._node_num):
            self._links[2*i][0] = self._links[2*i+1][0] = i
            self._links[2*i][1] = (i+1) % self._node_num
            self._links[2*i+1][1] = (i+2) % self._node_num
        self._struts = np.array([4*i for i in range(self._strut_num)], dtype=int)
        self._cables = np.delete(np.arange(self._link_num), self._struts)

        self._population_size = population_size
        self._generations = generations
        self._tournament_size = tournament_size
        self._mutation_probability = 38 * self._strut_num / 10000
        self._crossover_probability = 1-self._mutation_probability

        self._current_generation = []

        self._maximize_fitness = maximize_fitness

        self._random = random.Random(random_state)

    def create_individual(self):
        x = np.random.rand(self._node_num)
        y = np.random.rand(self._node_num)
        z = np.random.rand(self._node_num)
        gene = np.column_stack((x, y, z)).flatten()

        for _ in range(2 * self._strut_num):
            random_i = self._random.sample(range(self._strut_num), 2)
            strut_chosen = np.array([self._struts[i] for i in random_i])
            gene = np.append(gene, strut_chosen).flatten()
            random_node_1 = self._random.randint(0, 1)
            random_node_2 = self._random.randint(0, 1)
            # node_chosen = np.array([self._links[strut_chosen[0]][random_node_1],
            #                         self._links[strut_chosen[1]][random_node_2]])
            node_chosen = np.array([random_node_1, random_node_2], dtype=int)
            gene = np.append(gene, node_chosen).flatten()

        for _ in range(2 * self._cable_num):
            random_i = self._random.sample(range(self._cable_num), 2)
            cable_chosen = np.array([self._cables[i] for i in random_i])
            gene = np.append(gene, cable_chosen).flatten()
            random_node_1 = self._random.randint(0, 1)
            random_node_2 = self._random.randint(0, 1)
            # node_chosen = np.array([self._links[cable_chosen[0]][random_node_1],
            #                         self._links[cable_chosen[1]][random_node_2]])
            node_chosen = np.array([random_node_1, random_node_2], dtype=int)
            gene = np.append(gene, node_chosen).flatten()

        return gene

    def decode(self, gene):
        """
        Decode gene into xml-readable data
        Args:
            gene:

        Returns: node (node num * 3), bars (bar num * 2), cables (cable num * 2),
        actuators(cable num, default all cables)

        """
        nodes = gene[:self._node_num * 3].reshape(self._node_num, 3)

        shuffles = gene[self._node_num * 3:].reshape(8 * self._strut_num, 4)
        links = np.copy(self._links)
        for shuffle in shuffles:
            link1, link2 = int(shuffle[0]), int(shuffle[1])
            node1, node2 = int(shuffle[2]), int(shuffle[3])
            if links[link1][1-node1] != links[link2][node2] and links[link2][1-node2] != links[link1][node1]:
                links[link1][node1], links[link2][node2] = links[link2][node2], links[link1][node1]
        bars = np.array([links[i] for i in self._struts])
        cables = np.array([links[i] for i in self._cables])
        actuators = np.arange(self._cable_num)

        return nodes, bars, cables, actuators

    def crossover(self, parent1, parent2):
        crossover_index = self._random.randrange(1, len(parent1))
        child1 = np.append(parent1[:crossover_index], parent2[crossover_index:])
        child2 = np.append(parent2[:crossover_index], parent1[crossover_index:])
        return child1, child2

    def mutate(self, individual):
        """Reverse the bit of a random index in an individual."""
        mutate_index = self._random.randrange(len(individual))
        print(mutate_index)
        individual[mutate_index] = (0, 1)[individual[mutate_index] == 0]

    def random_selection(self, population):
        """Select and return a random member of the population."""
        return self._random.choice(population)

    def tournament_selection(self, population):
        """Select a random number of individuals from the population and
        return the fittest member of them all.
        """
        members = self._random.sample(population, self._tournament_size)
        members.sort(
            key=attrgetter('fitness'), reverse=self._maximize_fitness)
        return members[0]

    def create_initial_population(self):
        """Create members of the first population randomly"""
        initial_population = []
        for _ in range(self._population_size):
            gene = self.create_individual()
            individual = Chromosome(gene)
            initial_population.append(individual)
        self._current_generation = initial_population

    def calculate_population_fitness(self, n_workers=None, parallel_type="processing"):
        pass

    def rank_population(self):
        """Sort the population by fitness according to the order defined by
                maximise_fitness.
        """
        self._current_generation.sort(
            key=attrgetter('fitness'), reverse=self._maximize_fitness
        )

    def create_new_population(self):
        """Create a new population using the genetic operators (selection,
        crossover, and mutation) supplied.
        """

        pass

    def create_first_generation(self, n_workers=None, parallel_type="processing"):
        pass

    def create_next_generation(self, n_workers=None, parallel_type="processing"):
        pass

    def run(self, n_workers=None, parallel_type="processing"):
        pass

    def best_individual(self):
        pass

    def last_generation(self):
        pass
