from src.TensegrityModel.tensegrity_builder import Tensegrity
from src.TensegrityModel.envs import TensegEnv
import os.path as osp
import gymnasium as gym
import numpy as np

nodes = np.array([
    [-1, 0, 0],
    [1, 0, 0],
    [0, -1, 0],
    [0, 1, 0]
])

bars = np.array([[0, 1], [2, 3]])

cables = np.array([[0, 2], [0, 3], [1, 2], [1, 3]])

actuators = np.array([0, 1, 2, 3])

dirname = osp.dirname(__file__)
des = '/home/oscar/anaconda3/envs/gym/lib/python3.8/site-packages/gymnasium/envs/mujoco/assets'
tbar = Tensegrity('tbar', nodes, bars, cables, actuators,
                  path=dirname, solver="Newton", integrator="RK4", stiffness=.1, damping=.05, ctrl_range=1)
tbar.create_xml()
tbar.register_gym(des)

env = gym.make(tbar.get_name, xml_file=tbar.get_filename, bar_num=2)
observation, info = env.reset()

for _ in range(1000):
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

print(info)
env.close()

tbar.clean(des)
