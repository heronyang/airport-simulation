#!/opt/local/bin/python
"""Generates Opengl quads from ATG DXF files

    Usage:  ./regionEditor --prefix=xxx  --airport=xxx
    :param prefix (optional): used for specifying root folder for airport adaptation (default: ../data)
    :param airport (reqd.): used to specify airport. Files are in prefix/airport

    The airport folder should contain a dxf folder with the files. An additional file 'drawings.txt'
    specifies the order of drawing the quads and their color.
"""

# Copyright 2014  Waqar Malik <waqarmalik@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os.path


airport = None
prefix = '../data'
ft2m = 0.3048


def read_dxf(filename):
    """ Reads a given dxf file and extracts the 3DFACE (quads) data.
    The quad data is output as list of polygon
    Each polygon is a list of vertices.
    (Output is a list of list)
    """
    with open(filename, 'r') as file_dxf:
        line = file_dxf.readline()
        while line.strip() != 'ENTITIES':
            line = file_dxf.readline()
        polys = []
        in_poly = False
        for line in file_dxf:
            line = line.strip()
            if line == 'ENDSEC':
                break
            elif in_poly:
                v_map = dict.fromkeys(['10', '20', '30', '11', '21', '31',
                                       '12', '22', '32', '13', '23', '23'], 0.0)
                while line != '0':
                    if line in v_map:
                        v_map[line] = float(next(file_dxf).strip()) * ft2m
                    line = next(file_dxf).strip()
                x = [v_map['10'], v_map['11'], v_map['12'], v_map['13']]
                y = [v_map['20'], v_map['21'], v_map['22'], v_map['23']]
                x, y = transform(x, y)
                polys.append(list(zip(x, y)))
            elif line == '3DFACE':
                in_poly = True
    return polys


def transform(x, y):
    if airport.upper() == 'KDFW':
        x = [(x0 / ft2m + 35411395) * 0.2565527 for x0 in x]
        y = [(y0 / ft2m - 12004533) * 0.3038006 for y0 in y]
    elif airport.upper() == 'KCLT':
        pass
    else:
        pass
    return x, y


def write_quads(polys, color):
    """Writes .dxf data as a plain .quad file
    Each line:  x y color
    Block of 4 lines define a polygon with vertex colors.
    """
    filename = os.path.join(prefix, airport.upper(), airport.lower() + '.quad')
    with open(filename, 'a') as fout:
        for poly in polys:
            for vertex in poly:
                c = color.lstrip('#')
                c = [c[:2], c[2:4], c[-2:]]
                rgb = [round(int(x, 16) / 255, 3) for x in c]
                fout.write('{0[0]:10.2f}\t{0[1]:10.2f}\t{1[0]}\t{1[1]}\t{1[2]}\n'.format(vertex, rgb))


def convert_dxf():
    filename = os.path.join(prefix, airport.upper(), 'dxf/drawings.txt')
    if not os.path.isfile(filename):
        print('(EEE) ' + filename + ' missing.')
        sys.exit(1)

    with open(filename, 'r') as map_file:
        for line in map_file:
            if line.strip() == '' or line[0] == '#':
                continue
            dxf_file, color, order = line.strip().split()
            dxf_file = os.path.join(prefix, airport.upper(), 'dxf', dxf_file)
            if not os.path.isfile(dxf_file):
                print('(EEE) File ' + dxf_file + ' missing.')
                sys.exit(1)
            else:
                polys = read_dxf(dxf_file)
                write_quads(polys, color)


def doc():
    print('\tUsage:  ./regionEditor --prefix=xxx  --airport=xxx')
    print('\t\tprefix (optional): used for specifying root folder for airport adaptation (default: ../data)')
    print('\t\tairport (required): used to specify airport. Files are in prefix/airport')
    sys.exit(1)


def main():
    global airport
    global prefix

    for i in range(1, len(sys.argv)):
        param = sys.argv[i].strip('--').split('=')
        if param[0].lower() == 'prefix':
            prefix = os.path.expanduser(param[1])
        elif param[0].lower() == 'airport':
            airport = param[1]
        elif param[0].lower() == 'help':
            doc()
        else:
            print('(EEE) ' + param[0] + ': Unknown parameter')
            sys.exit(1)

    if airport is None:
        print('(EEE) Need at least airport information')
        doc()

    if not os.path.exists(os.path.join(prefix, airport.upper())):
        print('(EEE)', os.path.join(prefix, airport.upper()), 'does not exist.')
        print('(EEE) Incorrect prefix/airport information provided')
        sys.exit(1)

    fn = os.path.join(prefix, airport.upper(), airport.lower() + '.quad')
    if os.path.isfile(fn):
        print('(WWW) File', fn, 'exists - will be overwritten.')
        f = open(fn, 'w')
        f.close()

    convert_dxf()


if __name__ == '__main__':
    main()