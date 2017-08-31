#!/usr/local/bin/python3

import socketserver
import json
import random
import routes
import os
import numpy as np
import nodes
import re

class SchedulerServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class SchedulerServerHandler(socketserver.BaseRequestHandler):
    def handle(self):

        def choose_tugDistance(time, data,dep):
            tugNum = 0
            depots = data["tugs"]
            sumMin = 0
            d = []
            t = []
            tugs = {"scenario_time": time,"tugs":[]}
            routes.init('/Users/rmorrisk/Downloads/assetsimulator/data/KDFW')
            nodes.init('/Users/rmorrisk/Downloads/assetsimulator/data/KDFW')
            dkeys = [x for x in list(depots.keys())]
            for depot in dkeys:
                if depots[depot] != []:
                    tugNum = tugNum + len(depots[depot])
                    t.append(depot)
                    d.append(nodes.depot_map[depot])
            print("t = ", t)
            print("d = ", d)
            dep = sorted(dep,key = lambda k:k['time'] - time)
            print("________________________")
            for ac in dep:
                print("resources = ", t)
                if t == []:
                    break
                paths = [nodes.get_distance(x, nodes.get_nearest_node(ac['location'][0],ac['location'][1])) for x in d]
                ind = paths.index(min(paths))
                sumMin += min(paths)
                print("depot =",t[ind], depots[t[ind]])
                tugs["tugs"].append({"callsign": depots[t[ind]][0],"operation":"tug", "trajectory":{"target":ac['callsign']}})
                depots[t[ind]].pop(0)
                if depots[t[ind]] == []:
                    t.remove(t[ind])
                    d.remove(d[ind])
                print("__________________")
            d_len = [len(depots[x]) for x in ["DPT-1","DPT-2"]]
            print(d_len)
            for b in depots["DPT-Q"]:
                    o = list(depots.keys())[d_len.index(min(d_len))]
                    tugs["tugs"].append({"callsign": b, "operation":"tug", "trajectory":{"target": o}})
                    d_len[d_len.index(min(d_len))]+=1
            return np.array([tugs,sumMin,tugNum])

        def choose_tugRandom(dep,used):
            while True:
                if all(x == [] for x in list(dep.values())):
                    tug = ""
                    break
                depots = list(dep.keys())
                random.shuffle(depots)
                depot = depots[0]
                if not dep[depot]:
                    depots.remove(depot)
                    continue
                random.shuffle(list(depot))
                if dep[depot][0] not in used:
                    tug = dep[depot][0]
                    break
                else:
                    dep[depot].remove(dep[depot][0])
                    continue
            return tug

        try:
            data = json.loads(self.request.recv(4096).decode().strip())
            print("Recevied from {}:".format(self.client_address[0]))
            time = data['sim_time']
            depots = data['tugs']
            #det = depots["DPT-Q"] #holds the tugs at the detachment point
            dep = [] # holds the departure aircraft ready to be towed.
            setup = 5
            for ac in data['aircraft']:
                #if time >= ac['activation'] - setup and ac['operation'] == 'tug' and ac['status'] == 'detached':
                #    det.append(ac)
                #else:
                if time >= ac['activation'] and  ac['operation'] == 'departure' and "tug" not in ac.keys():
                    dep.append(ac)
            out = choose_tugDistance(time,data,dep)
            print(out)
            self.request.sendall(json.dumps({'return': 'ok'}).encode())
        except Exception as e:
            print("Exception while receiving message: {} \n {}", e.args, e)


if __name__ == '__main__':
    host, port = '127.0.0.1', 13374
    server = SchedulerServer((host, port), SchedulerServerHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
