import src.TensegrityModel.tensegrity_ga as ga
from src.TensegrityModel.tensegrity_builder import Tensegrity
import os.path as osp

test_ga = ga.TensegrityGA(6)

test_ga.run(n_workers=2)
print(test_ga.best_individual[0])
nodes, bars, cables, actuators = test_ga.decode(test_ga.best_individual[1])
print(ga.tensegrity_ga.bounding_box(nodes))

dirname = osp.dirname(__file__)
best = Tensegrity('best', nodes, bars, cables, actuators,
                  path=dirname, solver="Newton", integrator="RK4", stiffness=10, damping=.01)
best.create_xml()

