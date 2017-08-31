#!/opt/local/bin/python

import os
import sys
import socketserver
import json

import pandas as pd

import nodes


class SchedulerServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class SchedulerServerHandler(socketserver.BaseRequestHandler):
    output = {'sim_time': None, 'tugs': [], 'aircraft': []}
    # Separation Matrix for Same Runway Operations: separation[follower][leader]
    sep = pd.DataFrame(data=[[59, 88, 109, 110, 5],
                             [59, 61, 109, 91, 5],
                             [59, 61, 90, 91, 5],
                             [59, 61, 109, 91, 5],
                             [89, 89, 89, 89, 50]],
                       index=['SMALL', 'LARGE', 'HEAVY', 'B75', 'ARRIVAL'],
                       columns=['SMALL', 'LARGE', 'HEAVY', 'B75', 'ARRIVAL'], dtype=float)

    def handle(self):
        try:
            recv = self.request.recv(16777216).decode()
        except Exception as e:
            print("Exception while receiving message: {} \n {}", e.args, e)
        data = json.loads(recv.strip())
        with open('sch_input.txt', 'a') as fp:
            fp.write('#' * 50 + '\n')
            fp.write('"sim_time": {}\n'.format(data['sim_time']))
            fp.write('"runway":\n')
            fp.write(' {\n' + '\n'.join('  "{}": {}'.format(k, v) for k, v in data['runway'].items()) + '\n}\n')
            fp.write('"aircraft": \n')
            for ac in data['aircraft']:
                fp.write(' {\n' + '\n'.join('  "{}": {}'.format(k, v) for k, v in ac.items()) + '\n }\n')
            fp.write('\n')

        # process the data, i.e. print it:
        print("\nData recevied from {}:".format(self.client_address[0]))
        self.process_data(data)
        self.request.sendall(json.dumps(self.output).encode())

        with open('sch_output.txt', 'a') as fp:
            fp.write('#' * 50 + '\n')
            fp.write('"sim_time": {}\n'.format(self.output['sim_time']))
            fp.write('"aircraft": \n')
            for ac in self.output['aircraft']:
                fp.write(' {\n' + '\n'.join('  "{}": {}'.format(k, v) for k, v in ac.items()) + '\n}\n')

    def process_data(self, data):
        print('Simulation time: {}'.format(data['sim_time']))
        print(json.dumps(data['runway'], indent=2, sort_keys=True))
        self.output = {'sim_time': None, 'tugs': [], 'aircraft': []}
        self.output['sim_time'] = data['sim_time']
        for ac in data['aircraft']:
            self.get_rnwy_eta(ac)
        self.output['aircraft'] = sorted(self.output['aircraft'], key=lambda x: x['rnwy_eta'])
        self.rnwy_solver()
        for ac in self.output['aircraft']:
            print('{0[callsign]:<8s}{0[operation]:<10s}{0[wt_class]:<8s}{0[fix]:<6s}{0[status]:<12s}'
                  '{0[1eta]:>8.1f}{0[rnwy_eta]:>8.1f}{0[rnwy_rta]:>8.1f}'.format(ac))
        output = self.output
        self.output = {}
        self.output = {'sim_time': output['sim_time'], 'aircraft': []}
        for ac in output['aircraft']:
            self.output['aircraft'].append(
                {'callsign': ac['callsign'], 'uid': ac['uid'], 'operation': ac['operation'],
                 'trajectory': {'detail': ac['trajectory']}})

        with open('sch_debug.txt', 'a') as fp:
            fp.write('#' * 50 + '\n')
            fp.write('"sim_time": {}\n'.format(self.output['sim_time']))
            fp.write('"runway":\n')
            fp.write(' {\n' + '\n'.join('  "{}": {}'.format(k, v) for k, v in data['runway'].items()) + '\n}\n')
            fp.write('"aircraft": \n')
            for ac in output['aircraft']:
                fp.write(' {\n' + '\n'.join('  "{}": {}'.format(k, v) for k, v in ac.items()) + '\n}\n')

    def get_rnwy_eta(self, ac):
        if ac['status'] == 'TAKEOFF':
            return
        if ac['operation'].lower() == 'arrival' and ac['status'] in ['PARK', 'TAXI', 'GATE', 'RAMP']:
            return
        taxi_time = 0
        route = ac['route']
        taxi_distances = nodes.get_route_distance(route)
        for ii in range(len(route) - 1):
            taxi_time += taxi_distances[ii] / nodes.get_link_speed(route[ii], route[ii + 1])
        ac['etime'] = -1
        if ac['etime'] == -1:
            if ac['status'] in ['ARRIVAL', 'PARK', 'GATE']:
                ac['etime'] = ac['activation']
            else:
                eta1 = nodes.get_distance_to_node(ac['location'], route[0]) / nodes.get_link_speed(route[0], route[1])
                ac['etime'] = self.output['sim_time'] - eta1

        rnwy_eta = ac['etime'] + taxi_time if ac['operation'].lower() == 'departure' else ac['etime']
        # No xing considered

        wt_class = ac['wt_class'] if ac['operation'].lower() == 'departure' else 'ARRIVAL'
        out_ac = {'callsign': ac['callsign'], 'uid': ac['uid'], 'operation': ac['operation'],
                  'activation': ac['activation'], '1eta': ac['etime'], 'fix': ac['fix'],
                  'rnwy_eta': rnwy_eta, 'route': ac['route'], 'wt_class': wt_class,
                  'xing': ii, 'status': ac['status']}
        self.output['aircraft'].append(out_ac)

    def rnwy_solver(self):
        arrivals = []
        departures = []
        for ac in self.output['aircraft']:
            if ac['status'] == 'ARRIVAL':
                arrivals.append(ac['rnwy_eta'])
            elif ac['operation'].lower() == 'departure':
                departures.append(ac)
        self.output['aircraft'] = departures
        p_time = -1000
        p_wc = 'LARGE'
        print('RTAs:', end=' ')
        for i in range(len(self.output['aircraft'])):
            ac = self.output['aircraft'][i]
            c_time = ac['rnwy_eta']
            c_wc = ac['wt_class']
            rnwy_rta = max(c_time, p_time + self.sep.loc[c_wc, p_wc])
            while len(arrivals)>0 and rnwy_rta>arrivals[0]-self.sep.loc['ARRIVAL','LARGE']:
                print(arrivals[0], end=' ')
                rnwy_rta = max(rnwy_rta, arrivals.pop(0) + self.sep.loc[c_wc, 'ARRIVAL'])
            print('{:.1f}x{:.1f}'.format(c_time, rnwy_rta), end=' ')
            self.output['aircraft'][i]['rnwy_rta'] = rnwy_rta
            p_time, p_wc = self.output['aircraft'][i]['rnwy_rta'], c_wc

            self.output['aircraft'][i]['trajectory'] = [[r, -1] for r in ac['route']]
            if ac['operation'].lower() == 'departure':
                ac['trajectory'][-1][-1] = ac['rnwy_rta']
                if nodes.get_type(ac['route'][0]) == 'GATE_NODE':
                    ac['trajectory'][0][-1] = max(ac['activation'],
                                                  ac['rnwy_rta'] - 1.1 * (ac['rnwy_eta'] - ac['1eta']))
                    if not gate_hold:
                        ac['trajectory'][0][-1] = ac['activation']
                route = ac['route']
                for ii in [2, 3, 4, 5, 6]:
                    if len(route) > ii:
                        ac['trajectory'][-ii][-1] = ac['trajectory'][-ii + 1][-1] - 1.03 * nodes.get_distance(
                            route[-ii], route[-ii + 1]) / nodes.get_link_speed(route[-ii], route[-ii + 1])
        print()



if __name__ == '__main__':
    gate_hold = False
    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('--').split('=')
        if param[0].lower() == 'gate_hold':
            gate_hold = True
        elif param[0].lower() == 'help':
            print('Usage: {} --gate_hold'.format(sys.argv[0]))
            sys.exit(1)
        else:
            print('(EEE) ' + param[0] + ': Unknown parameter')
            sys.exit(1)
    try:
        os.remove('sch_input.txt')
    except OSError:
        pass
    try:
        os.remove('sch_output.txt')
    except OSError:
        pass
    try:
        os.remove('sch_debug.txt')
    except OSError:
        pass
    host, port = '127.0.0.1', 13373
    nodes.init('data/KRDR/')
    server = SchedulerServer((host, port), SchedulerServerHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
