#!/opt/local/bin/python

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

from collections import deque
import os
import sys
import random
import socket
import json

import nodes
import routes
import scenario
import airport


def simulate(data_dir, sim_scenario, scheduler_call_freq=100, scheduler_call_window=15):
    print(5 * '*' + ' Started ' + 5 * '*')
    print('--- Initialize airport node-link ---')
    nodes.init(data_dir)
    print('--- Initialize all possible routes --- ')
    routes.init(data_dir)
    print('--- Initialize scenario --- \n')
    scenario.read_scenario(sim_scenario)

    fout = 'out.asset'
    try:
        os.remove(fout)
    except OSError:
        pass

    # TMP route scheduler:
    for ac in scenario.aircraft:
        route_name = random.choice(list(scenario.aircraft[ac].all_routes.keys()))
        scenario.aircraft[ac].setup(route_name)
    # TMP route scheduler:

    scheduler_call_time_elapsed = scheduler_call_freq
    for sim_time in range(max([int(ac.active_time) + 1000 for ac in scenario.aircraft.values()])):
        print('\tSim time: {}'.format(sim_time), end='\r')
        airport.update_asdex(sim_time, scheduler_call_window * 60)
        airport.write_tracks(fout)

        # call scheduler
        if scheduler_call_time_elapsed >= scheduler_call_freq:
            scheduler()
            scheduler_call_time_elapsed = 1
        else:
            scheduler_call_time_elapsed += 1

        # call controller agents
        remove_aircraft = []
        for ac in scenario.aircraft:
            scenario.aircraft[ac].move(sim_time)
            if scenario.aircraft[ac].state == 'REMOVE':
                remove_aircraft.extend([ac])
        for ac in remove_aircraft:
            scenario.aircraft.pop(ac)
    print('\n\n' + 5 * '*' + ' Completed ' + 5 * '*')


def scheduler():
    data = airport.state
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 13373))
    # sock.send(json.dumps(data, indent=2, separators=(',', ': ')).encode())
    sock.send(json.dumps(data).encode())
    result = json.loads(sock.recv(16777216).decode())
    for ac in result['aircraft']:
        scenario.aircraft[ac['uid']].rtas = deque([t for n, t in ac['trajectory']['detail']])
    sock.close()


def main():
    """Usage: ./simulate.py --prefix=<data_dir> --airport=<ICAO> --scenario=<file> --cdr
    prefix: (optional) Location of "data" directory
    airport: (required) airport being simulated
    scenario: (required) scenario file
    cdr: (optional) enable conflict detection and resolution
    """
    prefix = "./data/"
    sim_airport = None
    sim_scenario = None

    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('--').split('=')
        if param[0].lower() == 'prefix':
            prefix = os.path.expanduser(param[1])
        elif param[0].lower() == 'airport':
            sim_airport = param[1]
        elif param[0].lower() == 'scenario':
            sim_scenario = param[1]
        elif param[0].lower() == 'cdr':
            airport.cdr = True
        elif param[0].lower() == 'help':
            print(main.__doc__)
            sys.exit(1)
        else:
            print('(EEE) ' + param[0] + ': Unknown parameter')
            sys.exit(1)

    if sim_airport is None or sim_scenario is None:
        print(main.__doc__)
        sys.exit(1)

    data_dir = os.path.join(prefix, sim_airport.upper())
    if not os.path.exists(data_dir):
        print('(EEE)', data_dir, 'does not exist.')
        print('(EEE) Incorrect prefix/airport information provided')
        sys.exit(1)

    if not os.path.exists(sim_scenario):
        print('(EEE)', sim_scenario, 'does not exist.')
        print('(EEE) Incorrect scenario-file information provided')
        sys.exit(1)

    simulate(data_dir, sim_scenario)


if __name__ == '__main__':
    main()