import src.TensegrityModel.tensegrity_ga as ga
from src.TensegrityModel.tensegrity_builder import Tensegrity
import os.path as osp

dirname = osp.dirname(__file__)
des = '/home/oscar/anaconda3/envs/gym/lib/python3.8/site-packages/gymnasium/envs/mujoco/assets'
test_ga = ga.TensegrityGA(6, gym_des=des, dirname=dirname, verbose=True)

test_ga.run(n_workers=1)
print(test_ga.best_individual[0])
nodes, bars, cables, actuators = test_ga.decode(test_ga.best_individual[1])
print(ga.tensegrity_ga.bounding_box(nodes))


best = Tensegrity('best', nodes, bars, cables, actuators,
                  path=dirname, solver="Newton", integrator="RK4", stiffness=1, damping=.05)
best.create_xml()

