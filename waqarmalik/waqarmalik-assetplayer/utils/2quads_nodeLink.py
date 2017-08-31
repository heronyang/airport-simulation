#! /opt/local/bin/python
""" This program takes SDSS nodes.txt and links.txt and converts them to colored 'quads' suitable for opengl use.

    Usage: ./nodeLink.py --prefix=xxx --airport=xxxx
    :param prefix (optional): default ../data')
    :param airport (required): look for files in prefix/airport
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

nodesize = 2.5  # nodesize

color = {'GATE': '#6c71c4',
         'SPOT': '#b58900',
         'RAMP': '#268bd2',
         'TAXI': '#859900',
         'QUEUE': '#2aa198',
         'DEPARTURE': '#dc322f',
         'ARRIVAL': '#dc322f',
         'BRIDGE': '#cb4b16',
         'EXIT': '#d33682',
         'RUNWAY': '#cb4b16'}

airport = None
nodes = []


def transform(x, y):
    if airport.upper() == 'KDFW':
        pass
    elif airport.upper() == 'KCLT':
        x -= 634.68
        y -= 1195.08
    else:
        pass
    return x, y
# 626.9468, 1204.979


def node_quads(in_file, out_file):
    global nodes
    if not os.path.isfile(in_file):
        print(in_file, 'does not exist')
        sys.exit(1)
    if os.path.isfile(out_file):
        print('(WWW) File', out_file, 'exists - will be overwritten.')
    with open(in_file, 'r') as fin, open(out_file, 'w') as fout:
        for line in fin:
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                line = line.split()
                x, y = transform(float(line[0]), float(line[1]))
                name = line[3]
                node_type = line[4].split('_')[0]
                nodes += [(x, y)]
                if node_type in color:
                    c = color[node_type].lstrip('#')
                    c = [c[:2], c[2:4], c[-2:]]
                    rgb = [round(int(x, 16) / 255, 3) for x in c]
                else:
                    print('(EEE) Unknown node type')
                    rgb = [0, 1, 1]
                fout.write('{0}\t{1:10.3f}\t{2:10.3f}\t{3[0]}\t{3[1]}\t{3[2]}\n'.
                           format(name, x - nodesize, y - nodesize, rgb))
                fout.write('{0}\t{1:10.3f}\t{2:10.3f}\t{3[0]}\t{3[1]}\t{3[2]}\n'.
                           format(name, x - nodesize, y + nodesize, rgb))
                fout.write('{0}\t{1:10.3f}\t{2:10.3f}\t{3[0]}\t{3[1]}\t{3[2]}\n'.
                           format(name, x + nodesize, y + nodesize, rgb))
                fout.write('{0}\t{1:10.3f}\t{2:10.3f}\t{3[0]}\t{3[1]}\t{3[2]}\n'.
                           format(name, x + nodesize, y - nodesize, rgb))


def link_quads(in_file, out_file):
    if not os.path.isfile(in_file):
        print(in_file, 'does not exist')
        sys.exit(1)
    if os.path.isfile(out_file):
        print('(WWW) File', out_file, 'exists - will be overwritten.')
    with open(in_file, 'r') as fin, open(out_file, 'w') as fout:
        for line in fin:
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                line = line.split()
                link_type = line[6].split('_')[0]
                if link_type in color:
                    c = color[link_type].lstrip('#')
                    c = [c[:2], c[2:4], c[-2:]]
                    rgb = [round(int(x, 16) / 510, 3) for x in c]
                else:
                    print('(EEE) Unknown node type')
                    rgb = [0, 1, 0]
                fout.write('{0[0]:10.3f}\t{0[1]:10.3f}\t{1[0]}\t{1[1]}\t{1[2]}\n'.
                           format(nodes[int(line[1])], rgb))
                fout.write('{0[0]:10.3f}\t{0[1]:10.3f}\t{1[0]}\t{1[1]}\t{1[2]}\n'.
                           format(nodes[int(line[2])], rgb))


def doc():
    print('\tUsage: ./nodeLink.py --prefix=xxx --airport=xxx')
    print('\t\t prefix (optional): default ../data')
    print('\t\t airport (required): look for files in prefix/airport')
    sys.exit(1)


def main():
    global airport
    prefix = '../data'
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

    in_node = os.path.join(prefix, airport.upper(), 'nodes.txt')
    out_node = os.path.join(prefix, airport.upper(), 'nodes.quad')
    in_link = os.path.join(prefix, airport.upper(), 'links.txt')
    out_link = os.path.join(prefix, airport.upper(), 'links.quad')

    node_quads(in_node, out_node)
    link_quads(in_link, out_link)


if __name__ == '__main__':
    main()