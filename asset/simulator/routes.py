""" Generate shortest path between start and end node.
    Generate shortest path between start and end node, and passing through the required via-nodes.
    all_route_pairs.txt file is required. The file is the predecessor matrix from Floyd-Warshall algorithm.
"""

# Copyright 2014  Waqar Malik <waqarmalik@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import numpy as np


def init(data_dir):
    global all_pairs
    all_pairs = np.loadtxt(os.path.join(data_dir, 'all_routes_pairs.txt')).astype('int')


def _get_path_(start, end, path):
    if start == end or all_pairs[start, end] == start or all_pairs[start, end] == end:
        return
    else:
        _get_path_(start, all_pairs[start, end], path)
        path.append(int(all_pairs[start, end]))
        _get_path_(all_pairs[start, end], end, path)


def shortest_path(start, end):
    """Provides the shortest path from nodes 'start' to 'end'

    :param start:
    :param end:
    :return: list of ordered nodes specifying each node along the path
    """
    path = []
    _get_path_(start, end, path)
    return path


def get_route(start, end, via_nodes):
    """Provides the shortest route between nodes 'start' and 'end' and passing through each node in the list 'via_nodes'.

    :param start:
    :param end:
    :param via_nodes: list of ordered_nodes the route has to pass through
    :return: list of ordered nodes specifying each node along the path
    """
    path = []
    via_nodes = [start] + via_nodes + [end]
    for from_node, to_node in zip(via_nodes, via_nodes[1:]):
        path.extend([from_node])
        path.extend(shortest_path(from_node, to_node))
    path.extend([end])
    return path
