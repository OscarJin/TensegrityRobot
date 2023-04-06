import random
import numpy as np


class TensegGA:

    def __init__(
            self,
            strut_num,
            population_size=20,
            generations=100,
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
        self._links = np.empty(shape=(self._link_num, 2), dtype=int)
        for i in range(self._node_num):
            self._links[2*i][0] = self._links[2*i+1][0] = i
            self._links[2*i][1] = (i+1) % self._node_num
            self._links[2*i+1][1] = (i+2) % self._node_num
        self._struts = np.array([4*i for i in range(self._strut_num)], dtype=int)
        self._cables = np.delete(np.arange(self._link_num), self._struts)

        self._population_size = population_size
        self._generations = generations

        self._random = random.Random(random_state)

    def create_individual(self):
        x = y = z = np.random.rand(self._node_num)
        gene = np.column_stack((x, y, z)).flatten()

        for _ in range(2 * self._strut_num):
            random_i = self._random.sample(range(self._strut_num), 2)
            strut_chosen = np.array([self._struts[i] for i in random_i])
            gene = np.append(gene, strut_chosen).flatten()
            random_node_1 = self._random.randint(0, 1)
            random_node_2 = self._random.randint(0, 1)
            node_chosen = np.array([self._links[strut_chosen[0]][random_node_1],
                                    self._links[strut_chosen[1]][random_node_2]])
            gene = np.append(gene, node_chosen).flatten()

        for _ in range(2 * self._cable_num):
            random_i = self._random.sample(range(self._cable_num), 2)
            cable_chosen = np.array([self._cables[i] for i in random_i])
            gene = np.append(gene, cable_chosen).flatten()
            random_node_1 = self._random.randint(0, 1)
            random_node_2 = self._random.randint(0, 1)
            node_chosen = np.array([self._links[cable_chosen[0]][random_node_1],
                                    self._links[cable_chosen[1]][random_node_2]])
            gene = np.append(gene, node_chosen).flatten()
        return gene
