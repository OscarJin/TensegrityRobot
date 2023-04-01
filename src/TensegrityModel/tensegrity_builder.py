import os.path as osp
from src.TensegrityModel.scene import create_scene


class Tensegrity:
    """
    .. note::

        Geometry of tensegrity:
        :obj: Coordinates of nodes
        :obj: Pairs of bars
        :obj: Pairs of cables
    
    Args:
        name (string): name of the tensegrity
        nodes (list): coordinates of nodes, the list should be in N*3 shape
        bars (list): pairs of bars, each bar is a list of the two ends
        cables (list); pairs of cables
        actuators (list): no. of actuated cables
    """

    def __init__(self, name, nodes, bars, cables, actuators):
        self.name = name
        self.nodes = nodes
        self.bars = bars
        self.cables = cables
        self.actuators = actuators

    def create_xml(self, path, stiffness=100, damping=1):
        """
        Create xml model for tensegrity
        Args:
            path: Absolute path of folder for storing xml
            stiffness: stiffness of cables, default 100
            damping: damping of cables, default 1

        Returns: a xml file

        """
        # create scene.xml
        create_scene(path)

        xml_path = self.name + '.xml'
        xml_path = osp.join(path, xml_path)
        xml_file = open(xml_path, 'w')

        # file header
        header = f"""
<mujoco model="{self.name}">

    <include file="scene.xml"/>

    <option timestep="0.002" iterations="100" solver="PGS" jacobian="dense" gravity = "0 0 -9.8" viscosity="0"/>

    <size njmax="5000" nconmax="500" nstack="5000000"/>

    <asset>
        <material name="rod" rgba=".7 .5 .3 1"/>
    </asset>
    
    <default>
        <motor ctrllimited="false" ctrlrange="-100 100"/>
        <tendon stiffness="{stiffness}" damping="{damping}" springlength=".5" frictionloss=".2"/>
        <geom size="0.02" mass=".1"/>
        <site size="0.04"/>
        <camera pos="0 -10 0"/>
    </default>
        """
        xml_file.write(header)

        # world body
        world_body_start = """
    <worldbody>
        """
        xml_file.write(world_body_start)

        for i in range(len(self.bars)):
            node1 = self.nodes[self.bars[i][0]]
            node2 = self.nodes[self.bars[i][1]]
            bar_xml = f"""
        <body>  
            <geom name="bar{i + 1}" type="capsule" fromto="{node1[0]} {node1[1]} {node1[2]} {node2[0]} {node2[1]} {node2[2]}" material="rod"/>
            <site name="b{self.bars[i][0]}" pos="{node1[0]} {node1[1]} {node1[2]}"/>
            <site name="b{self.bars[i][1]}" pos="{node2[0]} {node2[1]} {node2[2]}"/>
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

        for i in range(len(self.cables)):
            node1 = self.cables[i][0]
            node2 = self.cables[i][1]
            tendon_xml = f"""
        <spatial name="S{i}" width="0.02">
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

        for i in range(len(self.actuators)):
            actuator_xml = f"""
        <motor tendon="S{self.actuators[i]}" gear="1"/>
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
