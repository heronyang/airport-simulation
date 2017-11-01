#!/opt/local/bin/python
""" Coverts a given .asset file to .sqlite database.

This database is used for analysis.
"""
import os
import sys
import sqlite3


def main(scenario_file, track_file):

    summary = {}
    with open(scenario_file, 'r') as traffic_scenario:
        traffic_scenario.readline()  # read header
        for line in traffic_scenario:
            line = line.strip().split()
            # line = [None if x == 'NA' else x for x in line]
            if len(line) > 0 and line[0][0] != '#':
                summary[line[1]] = {'operation':line[0], 'entry':int(line[11]), 'expected_active':int(line[12])}



    with open(track_file, 'r') as history:
        history.readline()  # read the header
        for line in history:
            line = line.strip().split()
            if len(line) > 0 and line[0][0] != '#':
                call_sign = line[2]
                if call_sign in summary:
                    summary[call_sign]['actual_active'] = int(line[0])
                    delay = int(line[0]) - summary[call_sign]['expected_active']
                    summary[call_sign]['delay'] = delay
    

    for call_sign in summary:
        with open('summary.out', 'w') as outfile:
            outfile.write("callsign\t\texpected_active\t\tactual_active\t\tdelay\n")
            for call_sign in summary:
                outfile.write(call_sign+"\t\t"+str(summary[call_sign]['expected_active'])+"\t\t"
                    +str(summary[call_sign]['actual_active'])+"\t\t"+str(summary[call_sign]['expected_active'])+"\n")
        
        print (call_sign, summary[call_sign])                




def doc():
    print('\tUsage: python3 summary.py --scenario=<scenario.scenario> --track=<filename.asset> ')
    print('\t\tscenario (required): used for specifying the scenario corresponding to the track file')
    print('\t\ttrack (required): track information in asset format')
    sys.exit(1)


if __name__ == '__main__':
    scenario = None
    track = None

    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('--').split('=')
        if param[0].lower() == 'scenario':
            scenario = os.path.expanduser(param[1])
        elif param[0].lower() == 'track':
            track = os.path.expanduser(param[1])
        elif param[0].lower() == 'help':
            doc()
        else:
            print('(EEE) ' + param[0] + ': Unknown parameter')
            sys.exit(1)

    if track is None or not track.endswith('.asset') or scenario is None or not scenario.endswith('.scenario'):
        print('(EEE) Need asset history information and scenario information')
        doc()

    if not os.path.isfile(track):
        print('(EEE) File {} does not exist.'.format(track))
        sys.exit(1)

    if not os.path.isfile(scenario):
        print('(EEE) File {} does not exist.'.format(scenario))
        sys.exit(1)

    main(scenario, track)
    print('Finished.')
