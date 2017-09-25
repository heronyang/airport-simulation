from node import Node

class Gate(Node):

    def __init__(self, index, name, geo_pos):
        self.name = name
        Node.__init__(self, index, geo_pos)

    def __repr__(self):
        return "<GATE: %s>" % self.name
