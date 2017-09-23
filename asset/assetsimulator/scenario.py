"""This module reads the given scenario file, sets up the aircraft dictionary,
finds all possible routes for each vehicle, sets vehicle dynamics, etc.

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
import json
from copy import deepcopy

import nodes
import routes
from Vehicle import Vehicle


aircraft = {}  # {uid: aircraft}


def read_scenario(fname):
    global aircraft
    with open(fname) as fin:
        for line in fin:
            line = line.strip()
            if not line or line[0] == '#':
                continue
            line = line.split()
            line = [None if item == 'NA' else item for item in line]
            operation, callsign, uid, model, registration, airport, gate, spot, runway, fix = line[:10]
            start_loc, entry_time, active_time, turnaround = line[10:]
            aircraft[line[2]] = Vehicle(operation, callsign, uid, model, registration, airport, gate, spot,
                                        runway, fix, start_loc, entry_time, active_time, turnaround)

    _set_aircraft_dynamics_()
    _set_aircraft_route_()


def _set_aircraft_dynamics_():
    global aircraft
    wt_class = {}
    ac_dynamics = {}
    kt2ms = 0.514444
    ft2m = 0.3048
    with open('data/aircraft_types_database.txt') as fin:
        for line in fin:
            if not line.strip() or line[0] == '#':
                continue
            line = line.strip().split()
            if len(line) >= 20:
                line = line[:20]
                line += fin.readline().strip().split()
            wt_class[line[0]] = line[1]
            ac_dynamics[line[0]] = {'ARRIVAL': float(line[20]) * kt2ms, 'GATE': float(line[25]) * kt2ms,
                                    'RAMP': float(line[23]) * kt2ms, 'SPOT': float(line[23]) * kt2ms,
                                    'TAXI': float(line[21]) * kt2ms, 'QUEUE': float(line[22]) * kt2ms,
                                    'DEFAULT': float(line[21]) * kt2ms, 'AMAX': float(line[26]) * ft2m,
                                    'AMIN': float(line[27]) * ft2m}
    for ac in aircraft:
        model = aircraft[ac].model
        if model not in ac_dynamics:
            model = 'DEFAULT'
        aircraft[ac].dynamics = deepcopy(ac_dynamics[model])  # deepcopy required as each aircraft could update dynamics
        # Can also introduce uncertainty between aircraft of same type.
        aircraft[ac].wt_class = wt_class[model]


def _set_aircraft_route_():
    global aircraft
    with open(os.path.join(nodes.data_dir, 'route_groups_arr_decision_tree.json')) as fin:
        group_arr_decision = json.load(fin)
    with open(os.path.join(nodes.data_dir, 'route_arr_decision_tree.json')) as fin:
        route_arr_decision = json.load(fin)
    with open(os.path.join(nodes.data_dir, 'route_groups_dep_decision_tree.json')) as fin:
        group_dep_decision = json.load(fin)
    with open(os.path.join(nodes.data_dir, 'route_dep_decision_tree.json')) as fin:
        route_dep_decision = json.load(fin)
    for ac_key in aircraft:
        if aircraft[ac_key].operation == 'arrival':
            aircraft[ac_key].all_routes = _ac_routes_(aircraft[ac_key], group_arr_decision, route_arr_decision)
        elif aircraft[ac_key].operation == 'departure':
            aircraft[ac_key].all_routes = _ac_routes_(aircraft[ac_key], group_dep_decision, route_dep_decision)


def _ac_routes_(ac, group_decision, route_decision):
    via_gate_spot = {"default": []}
    via_spot_rnwy = {"default": []}
    if ac.spot in route_decision:
        gate_grp = 'default'
        if ac.spot in group_decision:
            for grp in group_decision[ac.spot]:
                if ac.gate in group_decision[ac.spot][grp]:
                    gate_grp = grp
                    break
        via_gate_spot = route_decision[ac.spot][gate_grp]
    if ac.runway in route_decision:
        spot_grp = 'default'
        if ac.runway in group_decision:
            for grp in group_decision[ac.runway]:
                if ac.spot in group_decision[ac.runway][grp]:
                    spot_grp = grp
                    break
        via_spot_rnwy = route_decision[ac.runway][spot_grp]

    ac_route = {}
    for gs in via_gate_spot:
        for sr in via_spot_rnwy:
            if ac.operation == 'departure':
                path = routes.get_route(nodes.gate_map[ac.gate], nodes.spot_map[ac.spot], via_gate_spot[gs])
                path.pop()
                path.extend(routes.get_route(nodes.spot_map[ac.spot], via_spot_rnwy[sr][-1], via_spot_rnwy[sr][:-1]))
                ac_route[gs + '_' + sr] = path
            elif ac.operation == 'arrival':
                path = routes.get_route(via_spot_rnwy[sr][0], nodes.spot_map[ac.spot], via_spot_rnwy[sr][1:])
                path.pop()
                path.extend(routes.get_route(nodes.spot_map[ac.spot], nodes.gate_map[ac.gate], via_gate_spot[gs]))
                ac_route[sr + '_' + gs] = path
            else:
                print('Error in path: vehicle in unknown operation')
    return ac_route