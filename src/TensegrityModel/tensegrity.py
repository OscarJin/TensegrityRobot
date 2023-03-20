import os.path as osp


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

    def create_xml(self, path):
        """
        Create xml model for tensegrity
        Args:
            path: Absolute path for storing xml

        Returns: a xml file

        """
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
            <tendon stiffness="100" damping="1" range=".5 2" springlength=".5" frictionloss=".2"/>
            <geom size="0.02" mass=".1"/>
            <site size="0.04"/>
            <camera pos="0 -10 0"/>
        </default>
        """
        xml_file.write(header)

        # file end
        end = '</mujoco>'
        xml_file.write(end)

        xml_file.close()
        pass
