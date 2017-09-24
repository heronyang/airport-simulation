class Line:

    def __init__(self, index, nodes):
        if len(nodes) < 2:
            raise Exception("Less than two nodes were given")
        self.__index = index
        self.__nodes = nodes

    def get_length(self):
        length = 0.0
        for i in range(1, len(self.__nodes)):
            from_node = self.__nodes[i - 1]
            to_node = self.__nodes[i]
            length += from_node.get_distance_to(to_node)
        return length

    def get_nodes(self):
        return self.__nodes
