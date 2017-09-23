#!/opt/local/bin/python
import os
import sys
import sqlite3

import numpy as np
import pandas as pd
import pandas.io.sql as pdsql


pd.set_option("display.width", None)


def analyze(trackdb, week, run, scenario, condition, configuration):
    """Analyze the given asset database.
    The function looks at individual flight track information and determines the time of
    various events. These are recorded in the processed file and visualization tool can then be employed.
    :param trackdb:
    """
    conn = sqlite3.connect(trackdb)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='scenario'")
    if bool(cur.fetchone()[0]):
        out = pdsql.read_sql("SELECT * FROM scenario", conn)
        out[['real_out', 'real_off', 'real_on', 'real_in', 'real_spot_time']] = \
        out[['real_out', 'real_off', 'real_on', 'real_in', 'real_spot_time']].astype(float)
        out['real_ramp_time'] = out[['operation', 'real_spot_time', 'real_out', 'real_in']].apply(
            lambda x: x[1] - x[2] if x[0] == 'departure' else x[3] - x[1], axis=1)
        out['real_AMA_time'] = out[['operation', 'real_spot_time', 'real_off', 'real_on']].apply(
            lambda x: x[2] - x[1] if x[0] == 'departure' else x[1] - x[3], axis=1)
        out['real_taxi_time'] = out[['operation', 'real_out', 'real_off', 'real_on', 'real_in']].apply(
            lambda x: x[2] - x[1] if x[0] == 'departure' else x[4] - x[3], axis=1)
    else:
        out = initialize(conn, cur)
    out['week'], out['run'], out['scenario'] = week, run, scenario
    out['condition'], out['configuration'] = condition, configuration
    out.set_index('callsign', inplace=True)
    out['sim_out'], out['sim_off'], out['sim_on'], out['sim_in'], out['sim_spot_time'] = [np.nan] * 5
    out['sim_ramp_time'], out['sim_AMA_time'], out['sim_taxi_time'] = [np.nan] * 3
    out['ramp_dist'], out['AMA_dist'], out['dist'] = [np.nan] * 3
    out['real_ramp_speed'], out['real_AMA_speed'], out['real_speed'] = [np.nan] * 3
    out['sim_ramp_speed'], out['sim_AMA_speed'], out['sim_speed'] = [np.nan] * 3
    out['ramp_stops'], out['ramp_stop_time'], out['AMA_stops'], out['AMA_stop_time'] = [np.nan] * 4
    out['stops'], out['stop_time'] = [np.nan] * 2

    for ac in out.index:
        print('Processing aircraft {}'.format(ac), end='\r')
        query = """select status, min(sim_time) as start, max(sim_time) as end from tracks
                   where callsign='{}' group by status order by min(sim_time)""".format(ac)
        ac_brief = pdsql.read_sql(query, conn)
        ac_brief.set_index('status', inplace=True)
        if out.ix[ac, 'operation'] == 'arrival':
            if 'LANDING' in ac_brief.index:
                out.ix[ac, 'sim_on'] = ac_brief.ix['LANDING', 'start']
            if 'LANDING/ARR' in ac_brief.index:
                out.ix[ac, 'sim_on'] = ac_brief.ix['LANDING/ARR', 'start']
            if 'RAMP' in ac_brief.index:
                out.ix[ac, 'sim_spot_time'] = ac_brief.ix['RAMP', 'start']
            if 'RAMP/ARR' in ac_brief.index:
                out.ix[ac, 'sim_spot_time'] = ac_brief.ix['RAMP/ARR', 'start']
            if 'GATE' in ac_brief.index:
                out.ix[ac, 'sim_in'] = ac_brief.ix['GATE', 'start']
            if 'GATE/ARR' in ac_brief.index:
                out.ix[ac, 'sim_in'] = ac_brief.ix['GATE/ARR', 'start']
            if 'PARK/ARR' in ac_brief.index:
                out.ix[ac, 'sim_in'] = ac_brief.ix['PARK/ARR', 'start']
            out.ix[ac, 'sim_ramp_time'] = out.ix[ac, 'sim_in'] - out.ix[ac, 'sim_spot_time']
            out.ix[ac, 'sim_AMA_time'] = out.ix[ac, 'sim_spot_time'] - out.ix[ac, 'sim_on']
            out.ix[ac, 'sim_taxi_time'] = out.ix[ac, 'sim_in'] - out.ix[ac, 'sim_on']
            query = """SELECT status, x, y from tracks where callsign='{}' and
                            (status='GRD' or status='RAMP')""".format(ac)
            ac_track = pdsql.read_sql(query, conn)
            ac_track.set_index('status', inplace=True)
            if 'GRD' in ac_track.index and not np.isnan(out.ix[ac, 'sim_spot_time']):
                grd_dist = ac_track.ix['GRD'].diff().applymap(np.square).sum(axis=1).map(np.sqrt).sum()
                out.ix[ac, 'AMA_dist'] = grd_dist
                out.ix[ac, 'real_AMA_speed'] = grd_dist / out.real_AMA_time[ac]
                out.ix[ac, 'sim_AMA_speed'] = grd_dist / out.sim_AMA_time[ac]
            if 'RAMP' in ac_track.index and not np.isnan(out.ix[ac, 'sim_in']):
                ramp_dist = ac_track.ix['RAMP'].diff().applymap(np.square).sum(axis=1).map(np.sqrt).sum()
                out.ix[ac, 'ramp_dist'] = ramp_dist
                out.ix[ac, 'dist'] = grd_dist + ramp_dist
                out.ix[ac, 'real_ramp_speed'] = ramp_dist / out.real_ramp_time[ac]
                out.ix[ac, 'sim_ramp_speed'] = ramp_dist / out.sim_ramp_time[ac]
                out.ix[ac, 'real_speed'] = out.dist[ac] / out.real_taxi_time[ac]
                out.ix[ac, 'sim_speed'] = out.dist[ac] / out.sim_taxi_time[ac]
        elif out.ix[ac, 'operation'] == 'departure':  # departure
            if 'GATE/DEP' in ac_brief.index:
                out.ix[ac, 'sim_out'] = ac_brief.ix['GATE/DEP', 'end']
            if 'PARK/DEP' in ac_brief.index:
                out.ix[ac, 'sim_out'] = ac_brief.ix['PARK/DEP', 'end']
            if 'RAMP/DEP' in ac_brief.index:
                out.ix[ac, 'sim_spot_time'] = ac_brief.ix['RAMP/DEP', 'end']
            if 'DEP' in ac_brief.index:
                out.ix[ac, 'sim_off'] = ac_brief.ix['DEP', 'start']
            if 'TAKEOFF/DEP' in ac_brief.index:
                out.ix[ac, 'sim_off'] = ac_brief.ix['TAKEOFF/DEP', 'start']
            out.ix[ac, 'sim_ramp_time'] = out.ix[ac, 'sim_spot_time'] - out.ix[ac, 'sim_out']
            out.ix[ac, 'sim_AMA_time'] = out.ix[ac, 'sim_off'] - out.ix[ac, 'sim_spot_time']
            out.ix[ac, 'sim_taxi_time'] = out.ix[ac, 'sim_off'] - out.ix[ac, 'sim_out']
            query = """SELECT status, x, y from tracks where callsign='{}' and
                            (status='GRD/DEP' or status='QUEUE/DEP' or status='RAMP/DEP')""".format(ac)
            ac_track = pdsql.read_sql(query, conn)
            ac_track.set_index('status', inplace=True)
            if 'RAMP/DEP' in ac_track.index and not np.isnan(out.ix[ac, 'sim_spot_time']):
                ramp_dist = ac_track.ix['RAMP/DEP'].diff().applymap(np.square).sum(axis=1).map(np.sqrt).sum()
                out.ix[ac, 'ramp_dist'] = ramp_dist
                out.ix[ac, 'real_ramp_speed'] = ramp_dist / out.real_ramp_time[ac]
                out.ix[ac, 'sim_ramp_speed'] = ramp_dist / out.sim_ramp_time[ac]
            if ('GRD/DEP' in ac_track.index or 'QUEUE/DEP' in ac_track.index) and not np.isnan(out.ix[ac, 'sim_off']):
                grd_dist = 0
                if 'GRD/DEP' in ac_track.index:
                    grd_dist += ac_track.ix['GRD/DEP'].diff().applymap(np.square).sum(axis=1).map(np.sqrt).sum()
                if 'QUEUE/DEP' in ac_track.index:
                    grd_dist += ac_track.ix['QUEUE/DEP'].diff().applymap(np.square).sum(axis=1).map(np.sqrt).sum()
                out.ix[ac, 'AMA_dist'] = grd_dist
                out.ix[ac, 'dist'] = grd_dist + ramp_dist
                out.ix[ac, 'real_AMA_speed'] = grd_dist / out.real_AMA_time[ac]
                out.ix[ac, 'sim_AMA_speed'] = grd_dist / out.sim_AMA_time[ac]
                out.ix[ac, 'real_speed'] = out.dist[ac] / out.real_taxi_time[ac]
                out.ix[ac, 'sim_speed'] = out.dist[ac] / out.sim_taxi_time[ac]
    print(' ' * 100)

    out.reset_index()
    out.to_csv('myOut.out', sep='\t', na_rep='NA')
    # print(out)
    conn.close()


def initialize(conn, cur):
    """Construct a DataFrame for the case when the database does not contain a "scenario" table.
    The DataFrame contains empty entries for all aircraft that are present in the "tracks" table.
    It appropriately fills in whether the aircraft is an arrival/departure.

    :param cur: sqlite3 cursor to database with tracks
    """
    cur.execute("SELECT DISTINCT callsign FROM tracks order by callsign")
    ac = [x[0] for x in cur.fetchall()]
    out = pd.DataFrame()
    out['callsign'] = ac
    for ind in out.index:
        query = """select status, min(sim_time) as start, max(sim_time) as end from tracks
                   where callsign='{}' group by status order by min(sim_time)""".format(out.loc[ind,'callsign'])
        ac_brief = pdsql.read_sql(query, conn)
        if 'DEP' in list(ac_brief['status'])[0]:
            out.loc[ind, 'operation'] = 'departure'
        elif 'ARR' in list(ac_brief['status'])[0]:
            out.loc[ind, 'operation'] = 'arrival'
        else:
            out.loc[ind, 'operation'] = 'tug'
    out['real_out']=np.nan 
    out['real_off']=np.nan
    out['real_on']=np.nan
    out['real_in']=np.nan
    out['real_spot_time'] = np.nan
    out['real_ramp_time'],  out['real_AMA_time'], out['real_taxi_time'] =[np.nan]*3

    return out


def main():
    """Usage: ./analyze.py --trackdb=<filename.assetDB> --week=<week_num> --run=<sim_name> --scenario=<scenario_name> --condition=<advisory> --configutation=<controller position>

    trackdb (required) and others are optional
    trackdb : name of the ASSET database
    run: simulation identifier
    scenario: scenario identifier
    condition: advisory, baseline, paper strips, etc.
    configuration: controller position in cab
    """
    trackdb = None
    week = None
    run = None
    scenario = None
    condition = None
    configuration = None
    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('-').split('=')
        if param[0].lower() == 'help':
            print(main.__doc__)
            print(analyze.__doc__)
            sys.exit(1)
        elif param[0].lower() == 'trackdb':
            trackdb = os.path.expanduser(param[1])
        elif param[0].lower() == 'run':
            run = param[1]
        elif param[0].lower() == 'week':
            week = param[1]
        elif param[0].lower() == 'scenario':
            scenario = param[1]
        elif param[0].lower() == 'condition':
            condition = param[1]
        elif param[0].lower() == 'configuration':
            configuration = param[1]
        else:
            print('(EEE) ' + sys.argv[i] + ': Unknown parameter')
            print(main.__doc__)
            sys.exit(1)
    if not trackdb:
        print('(EEE) Need at least asset track database.')
        print(main.__doc__)
        sys.exit(1)
    if trackdb and not os.path.isfile(trackdb):
        print('(EEE) File {} does not exist.'.format(trackdb))
        sys.exit(1)

    analyze(trackdb, week, run, scenario, condition, configuration)


if __name__ == '__main__':
    main()
