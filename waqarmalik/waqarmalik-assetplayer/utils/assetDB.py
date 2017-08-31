#!/opt/local/bin/python
""" Coverts a given .asset file to .sqlite database.

This database is used for analysis.
"""
import os
import sys
import sqlite3


def main(scenario_file, track_file):
    """Build a database containing the scenario and track data.
    The database will be build in the same folder as the track data (<name>.asset) and will be called <name>.sqlite
    """
    asset_db = os.path.splitext(track_file)[0] + '.assetDB'
    print(asset_db)

    with open(track_file, 'r') as history, sqlite3.connect(asset_db) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS tracks")
        cur.execute("""CREATE TABLE tracks(sim_time NUM, utc_time INT, callsign TEXT, ac_type TEXT,
                        registration TEXT, status TEXT, x NUM, y NUM, z NUM, phi NUM, speed NUM)
                    """)
        cur.execute("CREATE INDEX time_idx ON tracks(sim_time)")
        cur.execute("CREATE INDEX ac_idx ON tracks(callsign)")
        history.readline()  # read the header
        for line in history:
            line = line.strip().split()
            if len(line) > 0 and line[0][0] != '#':
                status = line[5]
                if status == 'SPOT/DEP':
                    line[5] = 'RAMP/DEP'
                elif '/DEP' in status and status not in ['RAMP/DEP', 'PARK/DEP', 'TAKEOFF/DEP']:
                    line[5] = 'TAXI/DEP'
                elif status == 'SPOT/ARR':
                    line[5] = 'RAMP/ARR'
                elif '/ARR' in status and status not in ['LANDING/ARR', 'RAMP/DEP', 'PARK/ARR']:
                    line[5] = 'TAXI/ARR'
                cur.execute("INSERT INTO tracks VALUES (?,?,?,?,?,?,?,?,?,?,?)", tuple(line))
                print('Processing snapshot at time {}{}'.format(line[0], ' ' * 20), end='\r')
    if scenario_file:
        # will add table containing scenario
        with open(scenario_file, 'r') as traffic_scenario, sqlite3.connect(asset_db) as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS scenario")
            cur.execute("""CREATE TABLE scenario(operation, callsign, registration, acType, airport, gate, spot,
                            runway, fix, real_out NUM, real_off NUM, real_on NUM, real_in NUM, real_spot_time NUM)
                        """)
            cur.execute("CREATE INDEX scen_ac_idx ON scenario(callsign)")
            traffic_scenario.readline()  # read header
            for line in traffic_scenario:
                line = line.strip().split()
                line = [None if x == 'NA' else x for x in line]
                if len(line) > 0 and line[0][0] != '#':
                    status = line[5]
                    if status == 'SPOT/DEP':
                        line[5] = 'RAMP/DEP'
                    elif '/DEP' in status and status not in ['RAMP/DEP', 'PARK/DEP', 'TAKEOFF/DEP']:
                        line[5] = 'TAXI/DEP'
                    elif status == 'SPOT/ARR':
                        line[5] = 'RAMP/ARR'
                    elif '/ARR' in status and status not in ['LANDING/ARR', 'RAMP/DEP', 'PARK/ARR']:
                        line[5] = 'TAXI/ARR'
                    cur.execute("INSERT INTO scenario VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(line))

            # Check that flights in "tracks" table are present in "scenario" table
            conn.commit()
            cur.execute('SELECT DISTINCT callsign FROM scenario')
            scenario_ac = {x[0] for x in cur.fetchall()}
            cur.execute('SELECT DISTINCT callsign FROM tracks')
            track_ac = {x[0] for x in cur.fetchall()}
            if track_ac.issubset(scenario_ac):
                print('GOOD. All flight objects with tracks have an entry in "scenario" table in database.')
            else:
                print('BAD. Flights {} have no corresponding entries in "scenario" table in database.')


def doc():
    print('\tUsage: assetDB.py --scenario=<scenario.scenario> --track=<filename.asset> ')
    print('\t\tscenario (optional): used for specifying the scenario corresponding to the track file')
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

    if track is None or not track.endswith('.asset'):
        print('(EEE) Need at least asset history information')
        doc()

    if not os.path.isfile(track):
        print('(EEE) File {} does not exist.'.format(track))
        sys.exit(1)

    main(scenario, track)
    print('Finished. You can now run the analysis.{}'.format(' ' * 40))
