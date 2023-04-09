import src.TensegrityModel.tensegrity_ga as GA
from src.TensegrityModel.tensegrity_builder import Tensegrity
import os.path as osp

ga = GA.TensegGA(strut_num=6)
p1 = ga.create_individual()
# print(p1)

nodes, bars, cables, actuators = ga.decode(p1)
nodes *= 2

dirname = osp.dirname(__file__)

P1 = Tensegrity('tbar', nodes, bars, cables, actuators,
                path=dirname, solver="Newton", integrator="RK4", stiffness=10, damping=.01)
P1.create_xml()
