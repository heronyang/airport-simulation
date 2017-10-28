class Link:

    def __init__(self, index, name, nodes):
        if len(nodes) < 2:
            raise Exception("Less than two nodes were given")
        self.index = index
        self.name = name
        self.nodes = nodes
        self.hash = hash("%s#%s#%s" % (self.name, self.index, self.nodes))

    @property
    def length(self):
        length = 0.0
        for i in range(1, len(self.nodes)):
            from_node = self.nodes[i - 1]
            to_node = self.nodes[i]
            length += from_node.get_distance_to(to_node)
        return length

    @property
    def start(self):
        return self.nodes[0]

    @property
    def end(self):
        return self.nodes[len(self.nodes) - 1]

    @property
    def reverse(self):
        """
        Reverses the node orders, which means the start and end are switched.
        """
        return Link(self.index, self.name, self.nodes[::-1])

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)


    def __repr__(self):
        return "<Link: " + self.name + ">"
