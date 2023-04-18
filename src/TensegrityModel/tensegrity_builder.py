import os.path as osp
from src.TensegrityModel.scene import create_scene
from gymnasium.envs.registration import register
import subprocess
import os
import numpy as np


class Tensegrity:
    """
    .. note::

        Geometry of tensegrity:
        :obj: Coordinates of nodes
        :obj: Pairs of bars
        :obj: Pairs of cables

    """

    def __init__(
            self, name, nodes, bars, cables, actuators,
            path,
            solver="Newoton",
            integrator="RK4",
            stiffness=100,
            damping=1,
            ctrl_range=30,
    ):
        """
        Args:
            name (string): name of the tensegrity
            nodes: coordinates of nodes, the list should be in N*3 shape
            bars: pairs of bars, each bar is a list of the two ends
            cables: pairs of cables
            actuators: no. of actuated cables
            path (string): Absolute path of folder for storing xml
            solver (string): Constraint solver algorithms (PGS / CG / Newton)
            integrator (string): Numerical integrator (Euler / RK4 / implicit)
            stiffness: stiffness of cables, default 100
            damping: damping of cables, default 1
            ctrl_range: range of motor control
        """
        self._name = name
        self._xml_filename = self._name + '.xml'
        self._xml_path = osp.join(path, self._xml_filename)

        self._nodes = nodes
        self._bars = bars
        self._cables = cables
        self._actuators = actuators

        self._solver = solver
        self._integrator = integrator
        self._stiffness = stiffness
        self._damping = damping
        self._ctrl_range = ctrl_range

    def create_xml(self):
        # Create xml model for tensegrity

        # create scenic settings
        scene_msg = create_scene()

        xml_file = open(self._xml_path, 'w')

        # file header
        header = f"""
<mujoco model="{self._name}">
        """
        header += scene_msg

        xml_file.write(header)

        default = f"""

    <option timestep="0.002" iterations="100" solver="{self._solver}" integrator="{self._integrator}" jacobian="dense" gravity = "0 0 -9.8" viscosity="0"/>

    <size njmax="5000" nconmax="500" nstack="5000000"/>

    <asset>
        <material name="rod" rgba=".7 .5 .3 1"/>
    </asset>
    
    <default>
        <motor ctrllimited="false" ctrlrange="-{self._ctrl_range} {self._ctrl_range}"/>
        <tendon stiffness="{self._stiffness}" damping="{self._damping}" frictionloss=".2"/>
        <geom size="0.02" mass=".1"/>
        <site size="0.04"/>
        <camera pos="0 -10 0"/>
    </default>
        """
        xml_file.write(default)

        # world body
        world_body_start = """
    <worldbody>
        """
        xml_file.write(world_body_start)

        for i in range(len(self._bars)):
            node1 = self._nodes[self._bars[i][0]]
            node2 = self._nodes[self._bars[i][1]]
            bar_xml = f"""
        <body name="bar{i + 1}">  
            <geom name="bar{i + 1}" type="capsule" fromto="{node1[0]} {node1[1]} {node1[2]} {node2[0]} {node2[1]} {node2[2]}" material="rod"/>
            <site name="b{self._bars[i][0]}" pos="{node1[0]} {node1[1]} {node1[2]}"/>
            <site name="b{self._bars[i][1]}" pos="{node2[0]} {node2[1]} {node2[2]}"/>
            <joint name="r{i + 1}" type="free" pos="0 0 0" limited="false" damping="0" armature="0" stiffness="0.2"/> 
        </body>
"""
            xml_file.write(bar_xml)

        world_body_end = """
    </worldbody>
        """
        xml_file.write(world_body_end)

        # tendon
        tendon_start = """
    <tendon>
        """
        xml_file.write(tendon_start)

        for i in range(len(self._cables)):
            node1 = self._cables[i][0]
            node2 = self._cables[i][1]
            length = np.linalg.norm(self._nodes[node1]-self._nodes[node2])
            tendon_xml = f"""
        <spatial name="S{i}" width="0.02" springlength="0 {length}">
            <site site="b{node1}"/>
            <site site="b{node2}"/>
        </spatial>
"""
            xml_file.write(tendon_xml)

        tendon_end = """
    </tendon>
        """
        xml_file.write(tendon_end)

        # actuator
        actuator_start = """
    <actuator>
        """
        xml_file.write(actuator_start)

        for i in range(len(self._actuators)):
            actuator_xml = f"""
        <motor tendon="S{self._actuators[i]}" gear="1"/>
"""
            xml_file.write(actuator_xml)

        actuator_end = """
    </actuator>
        """
        xml_file.write(actuator_end)

        # file end
        end = """
</mujoco>
        """
        xml_file.write(end)

        xml_file.close()

    def register_gym(self, des):
        """
        Register the tensegrity model in Gym
        Args:
            des: destination folder of 'asset' in Gymnasium package,
            usually `/home/$username$/anaconda3/envs/gym/lib/python3.8/site-packages/gymnasium/envs/mujoco/assets`
        """
        des_path = osp.join(des, self._xml_filename)
        subprocess.run(['cp', self._xml_path, des_path])

        register(
            id=self._name,
            entry_point="src.TensegrityModel.envs:TensegEnv",
            max_episode_steps=1000,
        )
        pass

    def clean(self, des):
        os.remove(osp.join(des, self._xml_filename))

    @property
    def get_name(self):
        return self._name

    @property
    def get_filename(self):
        return self._xml_filename
