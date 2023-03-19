

class Tensegrity():
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
    """

    def __init__(self, name, nodes, bars, cables):
        self.name = name
        self.nodes = nodes
        self.bars = bars
        self.cables = cables
        