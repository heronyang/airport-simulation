#!/opt/local/bin/python
from ggplot import *
import sys
import os
import pandas as pd
import numpy as np

def scenario(list_data, ta_data, scenario_list):
    """Convert atg scenario file to asset .scenario format
    It is also used as a combined scenario list in 'scenario' table in the assetDB

    list_data and ta_data are the atg files and were created from data in scenario_list.
    If there are small discrepancies in data (gate, spot, call-sign, activation time),
    then this program tries to correct them automatically. It outputs entries that cannot be auto-resolved.
    The user should first run this program and then manually try to correct the entries that cannot be auto-resolved.
    The ASSET sqlite database should be build only after the manual corrections have been done.

    :param list_data: ATG scenario file
    :param ta_data: ATG turn-around file
    :param scenario_list: Possible scenario file containing real field data. ATG scenarios were based on this file.
    """
    asset_scenario_file = os.path.splitext(list_data)[0] + '.scenario'
    demand_png = os.path.splitext(list_data)[0] + '.png'

    # Read ATG Scenario into dataFrame.
    atg_list = pd.read_table(list_data, comment='#', na_values=['NOT_SET', 'None'])
    atg_list = atg_list[atg_list.callsign.notnull()]
    atg_list.rename(columns={'tailNumber': 'registration'}, inplace=True)
    atg_list['operation'] = atg_list.flStatus.map(lambda x: 'arrival' if x == 'RTE' else 'departure')
    atg_list['airport'] = np.where(atg_list.flStatus == 'RTE', atg_list.depAirport, atg_list.destAirport)
    atg_list['runway'] = np.where(atg_list.flStatus == 'RTE', atg_list.destRunway, atg_list.depRunway)
    atg_list['fix'] = atg_list[['operation','nasFlightPath']].apply(find_fix, axis=1)
    atg_list.rename(columns={'pbTime': 'real_out'}, inplace=True)
    atg_list.real_out.astype(float)
    atg_list['real_off'] = np.nan
    atg_list.rename(columns={'fpSta': 'real_on'}, inplace=True)
    atg_list.real_on.astype(float)
    #    atg_list['real_on'] = atg_list[['flStatus', 'entryTime']].apply(
    #        lambda x: float(x[1][1:]) if x[0] == 'RTE' else np.nan, axis=1)
    atg_list['real_in'] = np.nan
    atg_list['real_spot_time'] = np.nan
    cols = ['operation', 'callsign', 'registration', 'acType', 'airport', 'gate', 'spot', 'runway', 'fix',
            'real_out', 'real_off', 'real_on', 'real_in', 'real_spot_time']
    atg_list = atg_list[cols]

    # Read turnaround
    if ta_data:
        ta_list = pd.read_table(ta_data, comment='#', na_values=['NOT_SET', 'None'])
        ta_list = ta_list[ta_list.callsign.notnull()]
        ta_list.rename(columns={'tailNumber': 'registration'}, inplace=True)
        ta_list.rename(columns={'destAirport': 'airport'}, inplace=True)
        ta_list.rename(columns={'depRunway': 'runway'}, inplace=True)
        ta_list.rename(columns={'pbTime': 'real_out'}, inplace=True)
        ta_list.real_out.astype(float)
        ta_list['real_off'] = np.nan
        ta_list['real_on'] = np.nan
        ta_list['real_in'] = np.nan
        ta_list['real_spot_time'] = np.nan
        ta_list['operation'] = 'departure'
        ta_list['gate'] = ta_list.registration.map(pd.Series(atg_list.gate.values, index=atg_list.registration))
        ta_list['acType'] = ta_list.registration.map(pd.Series(atg_list.acType.values, index=atg_list.registration))
        ta_list['fix'] = ta_list[['operation','nasFlightPath']].apply(find_fix, axis=1)
        ta_list = ta_list[cols]
    else:
        ta_list = None

    if scenario_list:
        scenario_list = pd.read_table(scenario_list, comment='#', na_values=['NOT_SET', 'None'])
        scenario_list = scenario_list[scenario_list.callsign.notnull()]
    else:
        scenario_list = pd.DataFrame()

    demand(atg_list, ta_list, scenario_list, png_file=demand_png)
    if not scenario_list.empty:
        scenario_check(atg_list, ta_list, scenario_list)

    # Combine list_data and ta_data to now get final file
    final_scenario = atg_list.append(ta_list)
    final_scenario.sort(['operation', 'real_on', 'real_out'], inplace=True)
    print('Writing {}'.format(asset_scenario_file))
    final_scenario.to_csv(asset_scenario_file, sep='\t', na_rep='NA', index=False)

def find_fix(x):
    fix = 'UNKWN'
    route = x[1].split('.')
    if x[0] == 'arrival':
        if len(route[-2]) == 6:
            fix = route[-2][:-1]
    if x[0] == 'departure':
        if len(route[1]) == 6:
            fix = route[1][:-1]
        elif len(route[2]) == 6:
            fix = route[2][:-1]
        else:
            fix = 'WAQAR'
    return fix



def scenario_check(atg_list, ta_list, scenario_list):
    """Check that the ATG flight has a corresponding entry in field-scenario file, and update ATG flight with
    paramters from the field-scenario

    :param atg_list: ATG scenario
    :param ta_list: ATG turnaround
    :param scenario_list: Scenario from field data
    """
    for ii in atg_list.index:
        atg = atg_list.ix[ii]
        match = scenario_list[(scenario_list.callsign == atg.callsign) & (scenario_list.operation == atg.operation)]
        if match.shape[0] == 1:  # match found in real scenario
            if atg.operation == 'departure':
                atg_list.ix[ii, 'real_off'] = atg_list.ix[ii, 'real_out'] + float(match.real_off - match.real_out)
                atg_list.ix[ii, 'real_spot_time'] = atg_list.ix[ii, 'real_out'] + \
                                                    float(match.real_spot_time - match.real_out)
                if not (atg_list.ix[ii, 'real_out'] < atg_list.ix[ii, 'real_spot_time'] < atg_list.ix[ii, 'real_off']):
                    atg_list.ix[ii, 'real_spot_time'] = np.nan
            else:
                atg_list.ix[ii, 'real_in'] = atg_list.ix[ii, 'real_on'] + float(match.real_in - match.real_on)
                atg_list.ix[ii, 'real_spot_time'] = atg_list.ix[ii, 'real_on'] + \
                                                    float(match.real_spot_time - match.real_on)
                if not (atg_list.ix[ii, 'real_on'] < atg_list.ix[ii, 'real_spot_time'] < atg_list.ix[ii, 'real_in']):
                    atg_list.ix[ii, 'real_spot_time'] = np.nan

        else:
            print('No field match found for {} ({}) from atg.list_data.'.format(atg.callsign, atg.operation))
            print(scenario_list[scenario_list.callsign == atg.callsign][['operation', 'callsign', 'registration']])
            print(scenario_list[scenario_list.registration == atg.registration][
                ['operation', 'callsign', 'registration']])
            print()

    for ii in ta_list.index:
        ta = ta_list.ix[ii]
        match = scenario_list[(scenario_list.callsign == ta.callsign) & (scenario_list.operation == ta.operation)]
        if match.shape[0] == 1:  # match found in real scenario
            ta_list.ix[ii, 'real_off'] = ta_list.ix[ii, 'real_out'] + float(match.real_off - match.real_out)
            ta_list.ix[ii, 'real_spot_time'] = ta_list.ix[ii, 'real_out'] + \
                                               float(match.real_spot_time - match.real_out)
            if not (atg_list.ix[ii, 'real_out'] < atg_list.ix[ii, 'real_spot_time'] < atg_list.ix[ii, 'real_off']):
                    atg_list.ix[ii, 'real_spot_time'] = np.nan
        else:
            cs = ta.callsign
            new_cs = cs[:3] + str(int(cs[3:]) - 1)
            match = scenario_list[(scenario_list.callsign == new_cs) & (scenario_list.operation == ta.operation)]
            if match.shape[0] == 1:  # match found in real scenario
                #ta_list.ix[ii, 'callsign'] = new_cs
                ta_list.ix[ii, 'real_off'] = ta_list.ix[ii, 'real_out'] + float(match.real_off - match.real_out)
                ta_list.ix[ii, 'real_spot_time'] = ta_list.ix[ii, 'real_out'] + \
                                                   float(match.real_spot_time - match.real_out)
                if not (atg_list.ix[ii, 'real_out'] < atg_list.ix[ii, 'real_spot_time'] < atg_list.ix[ii, 'real_off']):
                    atg_list.ix[ii, 'real_spot_time'] = np.nan
            else:
                print('No field match found for {} ({}) from atg.ta_data.'.format(ta.callsign, ta.registration))
                tmp = scenario_list[(scenario_list.registration == ta.registration) &
                                    (scenario_list.operation == ta.operation)]
                print(tmp[['operation', 'callsign', 'registration']])
                print()


def demand(atg_list, ta_list, scenario_list, delta=60.0, window=600.0, png_file='demand.png'):
    """Generate and plot the demand profile in ATG and real scenario

    :param atg_list:
    :param ta_list:
    :param scenario_list:
    :param delta: (seconds) Generate 'demand' count every delta seconds.
    :param window: (seconds) Calculate number of operation in [t-window, t+window] as demand
    """
    op_demands = pd.DataFrame()
    tmp = atg_list.append(ta_list)
    n_arrivals = (tmp.operation == 'arrival').sum()
    n_departures = (tmp.operation == 'departure').sum()
    trange = pd.Series(np.arange(np.min([0, tmp.real_on.min()]), np.max([tmp.real_out.max(), tmp.real_on.max()]) + delta, delta))
    op_demands['time'] = trange / 60
    op_demands['atg_arr'] = operation_count(np.sort(tmp[tmp.operation == 'arrival'].real_on), trange, window)
    op_demands['atg_dep'] = operation_count(np.sort(tmp[tmp.operation == 'departure'].real_out), trange, window)
    if scenario_list.empty:
        op_demands['field_arr'] = np.nan
        op_demands['field_dep'] = np.nan
    else:
        op_demands['field_arr'] = operation_count(np.sort(scenario_list[scenario_list.operation == 'arrival'].real_on),
                                                 trange, window)
        op_demands['field_dep'] = operation_count(
            np.sort(scenario_list[scenario_list.operation == 'departure'].real_out), trange, window)

    #p = ggplot(op_demands, aes(x='time', alpha=0.7)) + geom_line(aes(y='atg_arr'), color='firebrick', size=3) + \
    #    geom_line(aes(y='atg_dep'), color='coral', size=3) + \
    #    ylab('Number of operations') + xlab('time (minutes)') + ggtitle('Demand Plots')
    #print(p)

    op_demands2 = pd.melt(op_demands, id_vars=['time'], var_name='Type')
    demand_vis = ggplot(op_demands2, aes(x='time', y='value', colour='Type', group='Type')) + \
                 geom_line(size=3, alpha=1.0) + ylab('Demand: number of operations in [t-10, t+10]') + \
                 xlab('time (minutes)') + ggtitle('#D={}, #A={}'.format(n_departures, n_arrivals))
    ggsave(png_file, demand_vis)
    rout = os.path.splitext(png_file)[0] + '.r_out'
    op_demands2.to_csv(rout, sep='\t', na_rep='NA', index=False)

def operation_count(event_time, trange, window):
    return trange.map(lambda x: ((event_time > x - window) & (event_time < x + window)).sum())


def main():
    """Usage ./scenario.py <scenario.list_data> <scenario.ta_data> <scenario.list>

    Required: scenario.list_data
    Optional: scenario.ta_data, scenario.list>
    """
    list_data = None
    ta_data = None
    scenario_list = None
    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('-').strip('.').split('.')
        if param[0].lower() == 'help':
            print(main.__doc__)
            print(scenario.__doc__)
            sys.exit(1)
        elif param[1].lower() == 'list_data':
            list_data = os.path.expanduser(sys.argv[i])
        elif param[1].lower() == 'ta_data':
            ta_data = os.path.expanduser(sys.argv[i])
        elif param[1].lower() == 'list':
            scenario_list = os.path.expanduser(sys.argv[i])
        else:
            print('(EEE) ' + sys.argv[i] + ': Unknown parameter')
            print(main.__doc__)
            sys.exit(1)
    if not list_data:
        print('(EEE) Need at least atg list_data file.')
        print(main.__doc__)
        sys.exit(1)
    if list_data and not os.path.isfile(list_data):
        print('(EEE) File {} does not exist.'.format(list_data))
        sys.exit(1)
    if ta_data and not os.path.isfile(ta_data):
        print('(EEE) File {} does not exist.'.format(ta_data))
        sys.exit(1)
    if scenario_list and not os.path.isfile(scenario_list):
        print('(EEE) File {} does not exist.'.format(scenario_list))
        sys.exit(1)

    scenario(list_data, ta_data, scenario_list)


if __name__ == '__main__':
    main()
