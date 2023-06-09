import random
import numpy as np
from operator import attrgetter
import copy
from concurrent import futures
from src.TensegrityModel.tensegrity_builder import Tensegrity
from scipy.spatial import ConvexHull


def bounding_box(vertices):
    """Calculate 3D minimal bounding box volume of a tensegrity"""
    hull = ConvexHull(vertices)
    return hull.volume


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


class TensegrityGA(object):

    def __init__(
            self,
            strut_num,
            population_size=20,
            generations=100,
            tournament_size=3,
            elitism=True,
            maximize_fitness=True,
            verbose=False,
            random_state=None,
            gym_des=None,
            dirname=None,
    ):
        """
        Args:
            strut_num: number of struts
            population_size: number of candidate solutions in each generation
            generations: number of generations to evolve
            random_state: random seed. defaults to None
            gym_des: destination folder of 'asset' in Gymnasium package,
            usually `/home/$username$/anaconda3/envs/gym/lib/python3.8/site-packages/gymnasium/envs/mujoco/assets`
            dirname: where to store .xml, just use osp.dirname(__file__)
        """

        self._strut_num = strut_num
        self._node_num = 2 * strut_num
        self._link_num = 4 * strut_num
        self._cable_num = 3 * strut_num
        # original links, do not directly modify!
        self._links = np.empty(shape=(self._link_num, 2), dtype=int)
        for i in range(self._node_num):
            self._links[2 * i][0] = self._links[2 * i + 1][0] = i
            self._links[2 * i][1] = (i + 1) % self._node_num
            self._links[2 * i + 1][1] = (i + 2) % self._node_num
        self._struts = np.asarray([4 * i for i in range(self._strut_num)], dtype=int)
        self._cables = np.delete(np.arange(self._link_num), self._struts)

        self._population_size = population_size
        self._generations = generations
        self._tournament_size = tournament_size
        self._mutation_probability = 38 * self._strut_num / 10000
        self._crossover_probability = 1 - self._mutation_probability
        self._elitism = elitism

        self._current_generation = []

        self._maximize_fitness = maximize_fitness

        self._verbose = verbose
        self._random = random.Random(random_state)

        self._gym_des = gym_des
        self._dirname = dirname

    def create_individual(self):
        x = np.random.rand(self._node_num)
        y = np.random.rand(self._node_num)
        z = np.random.rand(self._node_num)
        gene = np.column_stack((x, y, z)).flatten()

        for _ in range(2 * self._strut_num):
            random_i = self._random.sample(range(self._strut_num), 2)
            strut_chosen = np.asarray([self._struts[i] for i in random_i])
            gene = np.append(gene, strut_chosen).flatten()
            random_node_1 = self._random.randint(0, 1)
            random_node_2 = self._random.randint(0, 1)
            # node_chosen = np.array([self._links[strut_chosen[0]][random_node_1],
            #                         self._links[strut_chosen[1]][random_node_2]])
            node_chosen = np.asarray([random_node_1, random_node_2], dtype=int)
            gene = np.append(gene, node_chosen).flatten()

        for _ in range(2 * self._cable_num):
            random_i = self._random.sample(range(self._cable_num), 2)
            cable_chosen = np.asarray([self._cables[i] for i in random_i])
            gene = np.append(gene, cable_chosen).flatten()
            random_node_1 = self._random.randint(0, 1)
            random_node_2 = self._random.randint(0, 1)
            # node_chosen = np.array([self._links[cable_chosen[0]][random_node_1],
            #                         self._links[cable_chosen[1]][random_node_2]])
            node_chosen = np.asarray([random_node_1, random_node_2], dtype=int)
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
            if links[link1][1 - node1] != links[link2][node2] and links[link2][1 - node2] != links[link1][node1]:
                links[link1][node1], links[link2][node2] = links[link2][node2], links[link1][node1]
        bars = np.asarray([links[i] for i in self._struts])
        cables = np.asarray([links[i] for i in self._cables])
        actuators = np.arange(self._cable_num)

        return nodes, bars, cables, actuators

    def fitness(self, gene):
        """Temporarily volume of the tensegrity"""
        nodes, bars, cables, actuators = self.decode(gene)
        temp = Tensegrity('temp', nodes, bars, cables, actuators,
                          path=self._dirname, solver="Newton", integrator="RK4", stiffness=1, damping=.05)
        temp.create_xml()
        env = temp.register_gym(self._gym_des)

        observation, info = env.reset()
        stable = True
        for _ in range(1000):
            observation, reward, terminated, truncated, info = env.step(action=np.zeros(env.action_space.shape))
            if terminated:
                stable = False
                break

        env.close()
        temp.clean(self._gym_des, clean_file=True)

        if stable:
            return bounding_box(nodes)
        else:
            return 0
        pass

    def crossover(self, parent1, parent2):
        crossover_index = self._random.randrange(1, len(parent1))
        child1 = np.append(parent1[:crossover_index], parent2[crossover_index:])
        child2 = np.append(parent2[:crossover_index], parent1[crossover_index:])
        return child1, child2

    def mutate(self, individual):
        """Reverse the bit of a random index in an individual."""
        mutate_index = self._random.randrange(3 * self._node_num)
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
        """Calculate the fitness of every member of the given population using
           the supplied fitness_function.
        """
        if n_workers == 1:
            for individual in self._current_generation:
                individual.fitness = self.fitness(individual.genes)
        else:
            if "process" in parallel_type.lower():
                executor = futures.ProcessPoolExecutor(max_workers=n_workers)
            else:
                executor = futures.ThreadPoolExecutor(max_workers=n_workers)
                # Create two lists from the same size to be passed as args to the
                # map function.
            genes = [individual.genes for individual in self._current_generation]

            with executor as pool:
                results = pool.map(self.fitness, genes)

            for individual, result in zip(self._current_generation, results):
                individual.fitness = result

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
        new_population = []
        elite = copy.deepcopy(self._current_generation[0])
        selection = self.tournament_selection

        while len(new_population) < self._population_size:
            parent_1 = copy.deepcopy(selection(self._current_generation))
            parent_2 = copy.deepcopy(selection(self._current_generation))

            child_1, child_2 = parent_1, parent_2
            child_1.fitness, child_2.fitness = 0, 0

            can_crossover = self._random.random() < self._crossover_probability
            can_mutate = self._random.random() < self._mutation_probability

            if can_crossover:
                child_1.genes, child_2.genes = self.crossover(parent_1.genes, parent_2.genes)

            if can_mutate:
                self.mutate(child_1.genes)
                self.mutate(child_2.genes)

            new_population.append(child_1)
            if len(new_population) < self._population_size:
                new_population.append(child_2)

        if self._elitism:
            new_population[0] = elite

        self._current_generation = new_population

    def create_first_generation(self, n_workers=None, parallel_type="processing"):
        """Create the first population, calculate the population's fitness and
                rank the population by fitness according to the order specified.
        """
        self.create_initial_population()
        self.calculate_population_fitness(
            n_workers=n_workers, parallel_type=parallel_type
        )
        self.rank_population()

    def create_next_generation(self, n_workers=None, parallel_type="processing"):
        """Create subsequent populations, calculate the population fitness and
           rank the population by fitness in the order specified.
        """
        self.create_new_population()
        self.calculate_population_fitness(
            n_workers=n_workers, parallel_type=parallel_type
        )
        self.rank_population()
        if self._verbose:
            print("Fitness: %f" % self.best_individual[0])

    def run(self, n_workers=None, parallel_type="processing"):
        """Run (solve) the Genetic Algorithm."""
        self.create_first_generation(
            n_workers=n_workers, parallel_type=parallel_type
        )

        for _ in range(1, self._generations):
            self.create_next_generation(
                n_workers=n_workers, parallel_type=parallel_type
            )

    @property
    def best_individual(self):
        """Return the individual with the best fitness in the current
           generation.
        """
        best = self._current_generation[0]
        return best.fitness, best.genes
        pass

    @property
    def last_generation(self):
        """Return members of the last generation as a generator function."""
        return ((member.fitness, member.genes) for member
                in self._current_generation)
        pass
