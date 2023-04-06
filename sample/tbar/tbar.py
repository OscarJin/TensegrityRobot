from src.TensegrityModel.tensegrity_builder import Tensegrity
from src.TensegrityModel.envs import TensegEnv
import os.path as osp
import gymnasium as gym

nodes = [
    [-1, 0, 0],
    [1, 0, 0],
    [0, -1, 0],
    [0, 1, 0]
]

bars = [[0, 1], [2, 3]]

cables = [[0, 2], [0, 3], [1, 2], [1, 3]]

actuators = [0, 1, 2, 3]

dirname = osp.dirname(__file__)
des = '/home/oscar/anaconda3/envs/gym/lib/python3.8/site-packages/gymnasium/envs/mujoco/assets'
tbar = Tensegrity('tbar', nodes, bars, cables, actuators,
                  path=dirname, solver="Newton", integrator="RK4", stiffness=10, damping=.01)
tbar.create_xml()
tbar.register_gym(des)

env = gym.make(tbar.get_name, xml_file=tbar.get_filename, bar_num=2)
observation, info = env.reset()
print(observation)
