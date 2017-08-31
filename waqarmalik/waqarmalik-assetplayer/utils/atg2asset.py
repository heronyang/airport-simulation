#!/opt/local/bin/python -tt
import os
import sys
import re
from datetime import datetime

import numpy as np


# airport info (lon,lat) and elevation (m)
airportDB = {'KDFW': [[-97.040331, 32.896903], 185],
             'KCLT': [[-80.943139, 35.214], 228]}

airport = None
ft2m = 0.3048


def update_status(ramp_region=None, queue_region=None):
    """Update status to reflect whether the aircraft is in ramp and/or queue
    GRD/DEP --> converted to RAMP/DEP or GATE/DEP or QUEUE/DEP for departures
    GRD --> converted to RAMP or GATE for arrivals
    :param ramp_region: File having a single polygon for the ramp.
    :param queue_region: File having a single polygon for the queue.
    """
    status = None
    directory = os.path.dirname(ramp_region) if ramp_region else os.path.dirname(queue_region)
    node_file = os.path.join(directory, 'nodes.txt')
    if not os.path.isfile(node_file):
        print('(EEE) {} file does not exist.'.format(node_file))
        sys.exit(1)
    gate_checker = gate_status(node_file)
    gate_checker.send(None)
    if ramp_region:
        in_ramp = in_poly(ramp_region)
        in_ramp.send(None)
    if queue_region:
        in_queue = in_poly(queue_region)
        in_queue.send(None)
    while True:
        x, y, status, speed = yield (status)
        if ramp_region:
            if status == 'GRD/DEP' and in_ramp.send((x, y)):
                status = 'RAMP/DEP'
                status = gate_checker.send((x, y, status, speed))
            if status == 'GRD' and in_ramp.send((x, y)):
                status = 'RAMP'
                status = gate_checker.send((x, y, status, speed))
        if queue_region:
            if status == 'GRD/DEP' and in_queue.send((x, y)):
                status = 'QUEUE/DEP'


def in_poly(region_file):
    poly = []  # the  polygon.
    with open(region_file, 'r') as in_file:
        for line in in_file:
            line = line.strip().split()
            if len(line) == 2 and line[0][0] != '#':
                poly += [[float(line[0]), float(line[1])]]
    n = len(poly)
    inside = False
    while True:
        xt, yt = yield (inside)
        inside = False
        p1x, p1y = poly[0]
        for i in range(1, n + 1):
            p2x, p2y = poly[i % n]
            if p1x == p2x and p1y == p2y:
                continue
            if yt > min(p1y, p2y):
                if yt <= max(p1y, p2y):
                    if xt <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (yt - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or xt <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y


def gate_status(node_file):
    gates = []
    status = None
    with open(node_file, 'r') as in_file:
        for line in in_file:
            line = line.strip().split()
            if len(line) > 5 and line[0][0] != ' #' and line[4] == 'GATE_NODE':
                gates += [translate_sdss(float(line[0]), float(line[1]))]
    gates = np.array(gates)
    while True:
        x, y, status, speed = yield (status)
        if speed == 0:
            dist = np.min(np.sum(np.square(gates - np.array([x, y])), axis=1))
            if dist < 20 * 20:  # within 20m of any gate
                status = 'GATE/DEP' if status == 'RAMP/DEP' else 'GATE'


def read_atg(atg_file, asset_file, status_checker=None):
    """Convert given 4Hz ATG his file to 1Hz Asset format.

    :param atg_file: A <fn>.his file
    :param asset_file: The output file containing the 1Hz surface snapshots (<fn>.asset in ./)
    """
    do_header = True
    prev_instance = []
    # Fix for 2014 HITL6 ATG bug that puts GRD/DEP for arrivals.
    arrivals = []
    # DONE Fix
    with open(atg_file, 'r') as in_file, open(asset_file, 'a') as out_file:
        out = False
        for line in in_file:
            if do_header:
                match = re.match(r'\w+.region\w+', line)
                if match:
                    print(match.group())
                    do_header = False
                line = line.strip().split()
                if len(line) > 0 and line[0] == 'callsign':
                    ics = line.index('callsign')
                    imodel = line.index('actype')
                    istatus = line.index('flight')
                    itail = line.index('tail#')
                    ix = line.index('x-ffc')
                    iy = line.index('y-ffc')
                    iz = line.index('z-pos')
                    iphi = line.index('psi')
                    iv = line.index('ground')
            elif len(line.strip()) > 0:  # snapshots
                line = line.strip().split()
                if isnumber(line[0]):
                    line[0] = line[0].split('.')[0]
                    out = False if float(line[0]) == prev_instance else True
                    sim_time = float(line[0])
                    utc_time = int(float(line[3]))
                    if out:
                        out_file.write('\n')
                    prev_instance = float(line[0])
                else:
                    if airport == 'KDFW':  # 2012 simulation
                        x, y = transform(float(line[3]), float(line[4]))
                        z = float(line[7]) * ft2m
                        phi = float(line[12])
                        speed = float(line[10]) * ft2m
                    else:  # 2014 onwards
                        x, y = transform(float(line[ix]), float(line[iy]))
                        z = float(line[iz]) * ft2m
                        phi = float(line[iphi])
                        speed = float(line[iv]) * ft2m
                    if status_checker:
                        status = line[istatus]
                        # Fix for 2014 HITL6 ATG bug that puts GRD/DEP for arrivals.
                        if line[ics] in arrivals and status == 'GRD/DEP':
                            status = 'GRD'
                        elif line[ics] not in arrivals and status == 'CLA':
                            arrivals.append(line[ics])
                        # DONE Fix
                        status = status_checker.send((x, y, status, speed))
                    else:
                        status = line[istatus]
                    ac = '\t'.join([line[ics]] + [line[imodel]] + [line[itail]] + [status])
                    if out:
                        out_file.write('{0}\t{1}\t{2}\t{3:10.3f}\t{4:10.3f}\t{5:10.3f}  {6:8.3f}  {7:8.3f}\n'.
                                       format(sim_time, utc_time, ac, x, y, z, phi, speed))
                    print('Processing snapshot at time {}{}'.format(sim_time, ' ' * 40), end='\r')


def translate_sdss(x, y):
    if airport.upper() == 'KDFW':
        pass
    elif airport.upper() == 'KCLT':
        x -= 634.68
        y -= 1195.08
    else:
        pass
    return x, y


def transform(x, y):
    if airport == 'KDFW':
        x = (x + 35411395) * 0.2565527
        y = (y - 12004533) * 0.3038006
    elif airport == 'KCLT':
        x *= ft2m
        y *= ft2m
    else:
        pass
    return x, y
    # return x * ft2m + 634.68, y * ft2m + 1195.08 # offset between SDSS and ATG origin


def isnumber(word):
    try:
        float(word)
        return True
    except ValueError:
        return False


def main():
    """Given a 4Hz ATG his file, write a 1Hz ASSET file.
    Usage: atg2asset.py --track=<filename.his> --airport=<ICAO> --ramp_region=<txt> --queue_region=<txt>
    argument 'ramp_region' and 'queue_region' are optional.
    The new file is written in './' and is called <filename.asset>
    """
    global airport
    atg_file = None
    ramp_region_file = None
    queue_region_file = None
    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('--').split('=')
        if param[0].lower() == 'track':
            atg_file = os.path.expanduser(param[1])
        elif param[0].lower() == 'airport':
            airport = os.path.expanduser(param[1]).upper()
        elif param[0].lower() == 'help':
            print(main.__doc__)
            sys.exit(1)
        elif param[0].lower() == 'ramp_region':
            ramp_region_file = param[1]
            if not os.path.isfile(ramp_region_file):
                print('(EEE) File {} does not exist.'.format(ramp_region_file))
                sys.exit(1)
        elif param[0].lower() == 'queue_region':
            queue_region_file = param[1]
            if not os.path.isfile(queue_region_file):
                print('(EEE) File {} does not exist.'.format(queue_region_file))
                sys.exit(1)
        else:
            print('(EEE) ' + param[0] + ': Unknown parameter')
            print(main.__doc__)
            sys.exit(1)

    if not atg_file.endswith('.his') or not os.path.isfile(atg_file):
        print(main.__doc__)
        print('(EEE) Need a ATG history (*.his) file to work on.')
        sys.exit(1)

    asset_file = os.path.splitext(os.path.basename(atg_file))[0] + '.asset'

    if airport is None or airport not in airportDB:
        print('Airport {} does not match ICAO name in my database.'.format(airport))
        sys.exit(1)

    time = datetime.now().strftime('%X  %m/%d/%Y')
    with open(asset_file, 'w') as out_file:
        out_file.write('# ASSET\n')
        out_file.write('# {}\n'.format(airport))
        out_file.write('# <configuration>\n')
        out_file.write('# Airport origin (0,0) at ({0[0]:.6f},{0[1]:.6f})\n'.format(airportDB[airport][0]))
        out_file.write('# Airport elevation is {}\n'.format(airportDB[airport][1]))
        out_file.write('# File created at {}\n'.format(time))
        out_file.write('# {}\n'.format(atg_file))
        out_file.write('# sim_time\tUTC_time\t')
        out_file.write('call_sign\tac_type\tregistration\tstatus\tx(m)\ty(m)\tz(m)\tphi(deg)\tspeed(m/s)\n')

    if ramp_region_file or queue_region_file:
        status_checker = update_status(ramp_region_file, queue_region_file)
        status_checker.send(None)
        read_atg(atg_file, asset_file, status_checker)
    else:
        read_atg(atg_file, asset_file)
    print('Finished. You can now create the database now.{}'.format(' ' * 40))


if __name__ == '__main__':
    main()
