class Link:

    def __init__(self, index, name, nodes):
        if len(nodes) < 2:
            raise Exception("Less than two nodes were given")
        self.index = index
        self.name = name
        self.nodes = nodes

    def get_length(self):
        length = 0.0
        for i in range(1, len(self.nodes)):
            from_node = self.nodes[i - 1]
            to_node = self.nodes[i]
            length += from_node.get_distance_to(to_node)
        return length
