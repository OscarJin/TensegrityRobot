from src.TensegrityModel.tensegrity_builder import Tensegrity
import os.path as osp

nodes = [
    [-1, 0, 0],
    [1, 0, 0],
    [0, -1, 0],
    [0, 1, 0]
]

bars = [[0, 1], [2, 3]]

cables = [[0, 2], [0, 3], [1, 2], [1, 3]]

actuators = [0, 1, 2, 3]

tbar = Tensegrity('tbar', nodes, bars, cables, actuators)
dirname = osp.dirname(__file__)
tbar.create_xml(dirname, solver="Newton", integrator="RK4", stiffness=10, damping=.01)
# print(nodes[0])
