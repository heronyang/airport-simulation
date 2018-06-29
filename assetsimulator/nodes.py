"""
This module defines the node model of the airport and provides several getter method.
This is a core module required for the ASSET simulator.
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

import pandas as pd
import numpy as np


data_dir = None
vertices = pd.DataFrame()  # {node index : x,y,type,name}
spot_map = {}  # {spot_string : node_index} used for reverse lookup
gate_map = {}  # {gate_string : node_index} used for reverse lookup
runway_map = {}  # {runway_string : orientation } used for modeling approach and take-off


def init(in_dir):
    """
    This function should be called once in the central program.
    This initiates all the module variables, and makes it available to other modules calling the Nodes module.
    Reduces memory usage as there is a single copy of the variables across different modules.

    :param in_dir: string pointing to directory where nodes.txt exists
    """
    global data_dir, vertices, spot_map, gate_map, runway_map
    data_dir = in_dir
    vert = {}
    with open(os.path.join(data_dir, 'nodes.txt')) as fin:
        for line in fin:
            if not line.strip() or line[0] == '#':
                continue
            line = line.strip().split()
            x, y = _transform_(float(line[0]), float(line[1]))
            vert[int(line[2])] = (x, y, line[4], line[3])
            if line[4] == 'GATE_NODE':
                gate_map[line[3]] = int(line[2])
            if line[4] == 'SPOT_NODE':
                # The spot name format is different at various airport adaptation.
                # The following logic makes it uniform: S# ('S' followed by spot number)
                spot = line[3].split('-')
                if len(spot) > 1:  # DFW format
                    spot = 'S' + spot[1].lstrip('0')
                else:
                    spot = 'S' + spot[0][4:]
                spot_map[spot] = int(line[2])
                vert[int(line[2])] = (x, y, line[4], spot)
    vertices = pd.DataFrame.from_dict(vert, orient='index')
    vertices.columns = ['x', 'y', 'type', 'name']

    with open(os.path.join(data_dir, 'runways.txt')) as fin:
        for line in fin:
            if not line.strip() or line[0] == '#':
                continue
            line = line.strip().split()
            if line[1] == 'ARRIVAL_NODE':
                vertices.loc[int(line[2]), 'name'] = line[0]
            elif line[1] == 'DEPARTURE_NODE':
                vertices.loc[int(line[2]), 'name'] = line[0]
            elif line[1] == 'RUNWAY_XING_NODE':
                vertices.loc[int(line[2]), 'name'] = line[0]
                vertices.loc[int(line[3]), 'name'] = line[0]
            elif line[1] == 'HEADING':
                runway_map[line[0]] = np.pi / 2 - np.radians(float(line[2]))  # convert from heading to orientation


def _transform_(x, y):
    """ Transform the input co-ordinate. SDSS produced nodes.txt model may have a different origin

    :param x: x-coordinate
    :param y: y-coordinate
    :return: transformed coordinate
    """
    airport = os.path.basename(data_dir)
    if airport.upper() == 'KDFW':
        pass
    elif airport.upper() == 'KCLT':
        x -= 634.68
        y -= 1195.08
    else:
        pass
    return x, y


def get_location(index):
    return vertices.loc[index, ['x', 'y']].tolist()


def get_type(index):
    return vertices.loc[index, 'type']


def get_name(index):
    return vertices.loc[index, 'name']


def get_distance(index1, index2):
    x1, y1 = vertices.loc[index1, ['x', 'y']]
    x2, y2 = vertices.loc[index2, ['x', 'y']]
    return np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def get_route_distance(route):
    """Returns list of length of each individual link in route
    :param route: list of indices
    :return: list of link lengths
    """
    return list(np.sqrt(np.sum(np.square(np.diff(vertices.loc[route, ['x', 'y']].values, axis=0)), axis=1)))


def get_distance_to_node(loc, index2):
    x1, y1, z1 = loc
    x2, y2 = vertices.loc[index2, ['x', 'y']]
    return np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)


def get_orientation(index1, index2):
    x1, y1 = vertices.loc[index1, ['x', 'y']]
    x2, y2 = vertices.loc[index2, ['x', 'y']]
    return np.arctan2(y2 - y1, x2 - x1)


def get_link_type(index1, index2):
    """Return the link_type given two node indices.

    The link_type is used to determine the nominal speed an aircraft should move with on the given link

    :param index1:
    :param index2:
    :return:
    """
    node1 = vertices.loc[index1, 'type'][:-5]
    node2 = vertices.loc[index2, 'type'][:-5]

    if node1 == node2:
        return node1
    if {'GATE'} & {node1, node2}:
        return 'GATE'
    if {'SPOT'} & {node1, node2}:
        return 'SPOT'
    if {'RAMP'} & {node1, node2}:
        return 'RAMP'
    if {'DEPARTURE'} & {node1, node2}:
        return 'TIPH'
    if {'QUEUE'} & {node1, node2}:
        return 'QUEUE'
    if {'ARRIVAL', 'EXIT'} & {node1, node2}:
        return 'LAND'
    if {'TAXI'} & {node1, node2} and node1 != node2:
        return list({node1, node2} - {'TAXI'})[0]
    print('(WWW) {} - {} case not handled'.format(node1, node2))  # Ideally this should not happen.
    return node1


def get_link_speed(index1, index2):
    link_type = get_link_type(index1, index2)
    speed = 8
    if link_type == 'GATE':
        speed = 2
    elif link_type == 'RAMP':
        speed = 5
    elif link_type == 'LAND':
        speed = 20
    return speed


def get_nearest_node(x, y):
    """returns index of nearest node to location x, y
    """
    dist = vertices.loc[:, ['x', 'y']].apply(lambda loc: (loc[1] - y) ** 2 + (loc[0] - x) ** 2, axis=1)
    return dist.idxmin()


def get_spot_index(spot):
    return spot_map[spot]


def get_gate_index(gate):
    return gate_map[gate]


def get_runway_orientation(runway):
    return runway_map[runway]
