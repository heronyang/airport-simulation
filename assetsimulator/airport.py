"""This module maintains the list of current aircraft (asde-x) on the surface and
maintains a current 'state' of planned aircraft for scheduler purpose. It also provides functions to write the
*.asset file
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

import pandas as pd

import numpy as np

import scenario
import nodes


# Current airport vehicles
gps = {}  # id: x,y,z,psi,v  np.array(list(gps.values()))
# CAI state
state = {'sim_time': None, 'fix': {}, 'runway': {}, 'tugs': {}, 'aircraft': []}
cdr = False


def update_asdex(sim_time, plan_window):
    """Updates the airport asdex (gps values) of current vehicles. Also updates the CAI state for call to scheduler.

    :param sim_time: current simulation time
    :param plan_window: planning window for schduler
    """
    global state, gps
    state['sim_time'] = sim_time
    state['aircraft'] = []
    gps = {}
    plan_time = sim_time + plan_window
    for ac_key in scenario.aircraft:
        if scenario.aircraft[ac_key].active_time <= plan_time and scenario.aircraft[ac_key].state is not None:
            # Records all aircraft the are active or will become active in within the planning window.
            ac = scenario.aircraft[ac_key]
            if ac.operation.lower() == 'departure':
                start_loc, end_loc = ac.gate, ac.runway
            else:
                end_loc, start_loc = ac.gate, ac.runway
            aircraft = {'callsign': ac.callsign, 'uid': ac.uid, 'operation': ac.operation, 'model': ac.model,
                        'fix': ac.fix, 'activation': ac.active_time, 'etime': ac.rtas[0], 'status': ac.state,
                        'route': list(ac.route), 'start': start_loc, 'end': end_loc,
                        'location': [ac.x, ac.y, ac.z], 'wt_class': ac.wt_class}
            aircraft['start'] = ac.gate if ac.operation == 'departure' else ac.runway
            aircraft['end'] = ac.runway if ac.operation == 'departure' else ac.gate
            state['aircraft'].append(aircraft)
        if scenario.aircraft[ac_key].entry_time <= sim_time and scenario.aircraft[ac_key].state is not None:
            # Record all vehicles currently entered into simulation. This will enable showing aircraft at the gates
            ac = scenario.aircraft[ac_key]
            gps[ac_key] = [ac.callsign, ac.operation, 'GRD/DEP' if ac.operation == 'departure' else 'GRD', ac.state,
                           ac.model, ac.x, ac.y, ac.z, ac.psi, ac.v]
    if cdr and len(gps) > 2:
        conflict_detection_resolution(sim_time)


def update_runway_use(sim_time, rnwy, ops, model):
    """Update the runway use parameter. Called from Vehicle module when an aircraft uses the runway.

    :param sim_time: time of event
    :param rnwy: runway where the event happened
    :param ops: type of event (landing, takeoff, crossing)
    :param model: aircraft model.
    """
    if rnwy not in state['runway']:
        state['runway'][rnwy] = {}
    state['runway'][rnwy][ops] = {'model': model, 'time': sim_time}


def update_fix_use(sim_time, fix, ops, model):
    """Update the fix use parameter. Called from Vehicle module when an aircraft uses the runway.

    :param sim_time: time of event
    :param fix: Teh fix effected by the event
    :param ops: takeoff
    :param model: aircraft model
    """
    if fix not in state['fix']:
        state['fix'][fix] = {}
    state['fix'][fix][ops] = {'model': model, 'time': sim_time}


def write_tracks(fname):
    with open(fname, 'a') as fout:
        fout.write(
            '# sim_time\tUTC_time\tcall_sign\tac_type\tregistration\tstatus\tx(m)\ty(m)\tz(m)\tphi(deg)\tspeed(m/s)\n')
        for ac in gps:
            if gps[ac][1] == 'departure' and gps[ac][3] in ['PARK', 'GATE']:
                phi = 270 - np.degrees(gps[ac][8])
            else:
                phi = 90 - np.degrees(gps[ac][8])
            fout.write('{}\t{}\t{}\t{}\t{}\t{}\t{:7.4f}\t{:7.4f}\t{}\t{:7.4f}\t{:7.4f}\n'.format(state['sim_time'],
                                                                                                 state['sim_time'],
                                                                                                 gps[ac][0], gps[ac][4],
                                                                                                 ac,
                                                                                                 gps[ac][2], gps[ac][5],
                                                                                                 gps[ac][6], gps[ac][7],
                                                                                                 phi, gps[ac][9]))


def get_runway_use(rnwy):
    if rnwy in state['runway']:
        return state['runway'][rnwy]
    else:
        return None


def get_fix_use(fix):
    if fix in state['fix']:
        return state['fix'][fix]
    else:
        return None


def conflict_detection_resolution(sim_time):
    cdr_radius = 75
    agps = pd.DataFrame.from_dict(gps, orient='index')
    agps.columns = ['callsign', 'ops', 'mode', 'status', 'model', 'x', 'y', 'z', 'psi', 'v']
    for acid in agps.index:
        ac = agps.loc[acid]
        agps = agps.drop(acid)
        if ac.status in ['PARK', 'TAKEOFF']:  # or scenario.aircraft[acid].cdr_stop:  # @gate or already resolved
            continue
        conflict = ((agps['x'] - ac['x']) ** 2 + (agps['y'] - ac['y']) ** 2) < cdr_radius ** 2
        acid_x = conflict[conflict == True].index
        if acid_x.size > 0:
            xstop = []
            for xid in acid_x:
                if agps.loc[xid].status in ['PARK', 'TAKEOFF']:
                    continue
                if ac.ops == 'departure' and ac.status in ['RAMP', 'SPOT'] and agps.loc[xid].status == 'TAXI':
                    scenario.aircraft[acid].cdr_stop = True
                    print('[{}] {} cdr ramp stop for {}.'.format(sim_time, scenario.aircraft[acid].callsign,
                                                                 scenario.aircraft[xid].callsign))
                    break
                if agps.loc[xid, 'ops'] == 'departure' and agps.loc[xid, 'status'] in ['RAMP',
                                                                                       'SPOT'] and ac.status == 'TAXI':
                    xstop.append(xid)
                    print('[{}] {} added for ramp cdr with {}.'.format(sim_time, scenario.aircraft[xid].callsign,
                                                                       scenario.aircraft[acid].callsign))
                    continue
                ar = list(scenario.aircraft[acid].route)[:6]
                xr = list(scenario.aircraft[xid].route)[:6]
                common = next((r for r in ar if r in set(xr)), None)
                if common is not None:  # merging route
                    ar = ar[:ar.index(common) + 1]
                    xr = xr[:xr.index(common) + 1]
                    ta = -nodes.get_distance_to_node([ac.x, ac.y, ac.z], ar[0]) / 8.0 + \
                         sum([x / 8.0 for x in nodes.get_route_distance(ar)])
                    tx = -nodes.get_distance_to_node(list(agps.loc[xid, ['x', 'y', 'z']]), xr[0]) / 8.0 + \
                         sum([x / 8.0 for x in nodes.get_route_distance(xr)])
                    if ac.v < 0.01:
                        ta += 1
                    if agps.loc[xid, 'v'] < 0.01:
                        tx += 1
                    if ta > tx:
                        scenario.aircraft[acid].cdr_stop = True
                        print('[{}] {} cdr time stop for {}.'.format(sim_time, scenario.aircraft[acid].callsign,
                                                                     scenario.aircraft[xid].callsign))
                        break
                    else:
                        xstop.append(xid)
                        print('[{}] {} added for time cdr with {}.'.format(sim_time, scenario.aircraft[xid].callsign,
                                                                           scenario.aircraft[acid].callsign))
                else:  # disjoint route
                    if ac.v < agps.loc[xid, 'v']:
                        scenario.aircraft[acid].cdr_stop = True
                        print('[{}] {} cdr speed stop for {}.'.format(sim_time, scenario.aircraft[acid].callsign,
                                                                      scenario.aircraft[xid].callsign))
                        break
                    else:
                        xstop.append(xid)
                        print('[{}] {} added for speed cdr with {}.'.format(sim_time, scenario.aircraft[xid].callsign,
                                                                            scenario.aircraft[acid].callsign))
            # if not scenario.aircraft[acid].cdr_stop:
            for xid in xstop:
                scenario.aircraft[xid].cdr_stop = True
                print('[{}] _{} cdr stopped for {}.'.format(sim_time, scenario.aircraft[xid].callsign,
                                                            scenario.aircraft[acid].callsign))
