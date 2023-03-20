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

actuators = [0, 2]

tbar = Tensegrity('Tbar', nodes, bars, cables, actuators)
dirname = osp.dirname(__file__)
tbar.create_xml(dirname)
# print(nodes[0])
