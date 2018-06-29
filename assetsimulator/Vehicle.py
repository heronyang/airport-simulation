""" This module defines the attributes of a single vehicle (aircraft or tug). It also incorporates the logic
for moving the aircraft. At each requested update, the pilot agent checks for conflicts, determines its action,
and executes its movement. Before returning back to the calling function, it updates its internal position.
"""

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

import numpy as np

import nodes
import airport


class Vehicle:
    def __init__(self, operation, callsign, uid, model, registration, arprt, gate, spot, runway, fix, start_loc,
                 entry_time, active_time, turnaround):
        self.operation = operation.lower()  # arrival/departure/tug
        self.callsign = callsign
        self.uid = uid  # Unique id for each operation
        self.model = model  # Vehicle model code
        self.registration = registration  # Vehicle registration. Will be same for turn-around flights
        self.airport = arprt  # Destination airport for departure, Origin airport for arrival
        self.gate = gate
        self.spot = spot
        self.runway = runway
        self.fix = fix  # Aircraft fix usage. There can be additional constraints on aircraft going to same fix
        self.start = start_loc  # Tug depot / Departure gate / Arrival exit
        self.entry_time = float(entry_time)  # Time aircraft enters the simulation
        self.active_time = float(active_time)  # Departure pushback time / Arrival touchdown time
        self.turnaround = turnaround  # If departure is a turnaround, indicate the uid of corresponding arrival
        self.wt_class = None  # Super / Heavy / B757 / Large / Small / tug
        self.dynamics = {}  # {name : speed or acceleration }

        # Current information variables of the aircraft
        self.cdr_stop = False
        self.state = None
        self.target_speed = None
        self.x = None
        self.y = None
        self.z = None
        self.psi = None
        self.s = 0.0  # distance moved along the current link
        self.v = 0.0
        self.a = 0.0
        self.timer = 0.0  # how far has timer proceeded
        self.timer_expiry = None  # When does the timer expire? If timer >= timer_expiry then timer has expired.

        # Trajectory information
        self.route = deque()  #
        self.all_routes = {}  # All routes the aircraft/vehicle can take
        self.link_distance = 0  # link-length for first link in route
        self.rtas = deque()  # Same size as route. Specifies rtas to each node. -1 implies move on pilot logic.

    def setup(self, route_name='default_default'):
        """Initializes route and associated variables for aircraft.

        The route could be set by the scheduler (centralized location), controller agent, or
        by assigning simple rule-based routing

        :param route_name: key name for route. If the key is not present in all_routes, the default value is used.
        """
        if route_name not in self.all_routes.keys():
            route_name = 'default_default'
        self.route = deque(self.all_routes[route_name])
        self.rtas = deque([-1] * len(self.route))
        self.link_distance = nodes.get_distance(self.route[0], self.route[1])
        link_type = nodes.get_link_type(self.route[0], self.route[1])
        self.target_speed = self.dynamics[link_type if link_type in self.dynamics else 'DEFAULT']

    def move(self, sim_time, dt=1.0):
        """ Move the vehicle.

        For all active aircraft first update_kinematics() based on vehicle factors such as dynamics, rtas, conflicts,
        and then update_route() if aircraft has traversed the link, and
        then finally use the updated kinematics to update the vehicle position.

        For aircraft between event_time and active_time model aircraft landing or parked at gate.
        :param sim_time:
        :param dt:
        :raise:
        """

        def update_position():
            if len(self.route) > 1:
                if self.route[1] == -1:  # for modeling departure aircraft takeoff.
                    # A dummy node (-1) is added to the route to model aircraft take-off
                    self.psi = nodes.get_runway_orientation(self.runway)
                    self.z = 100
                else:
                    self.psi = nodes.get_orientation(self.route[0], self.route[1])
                    self.z = 0
                self.x, self.y = nodes.get_location(self.route[0]) + self.s * np.array(
                    [np.cos(self.psi), np.sin(self.psi)])

        def update_kinematics():
            if self.cdr_stop:
                self.a = 0
                self.v = 0
                self.cdr_stop = False
            elif self.rtas[0] != -1 and self.rtas[0] > sim_time:
                # If speed is positive and vehicle was not supposed to leave previous node, slow down and stop
                self.a = -self.dynamics['AMIN'] if self.v > 0 else 0
                v_next = self.v + self.a * 1.0
                if v_next < 0:  # stop aircraft
                    self.v, self.a = 0.0, 0.0
            elif self.rtas[1] == -1:
                # No restraint on reaching next node --> move at target speed
                if self.v < self.target_speed - self.dynamics['AMAX'] * 0.5:
                    self.a = self.dynamics['AMAX']
                elif self.v > self.target_speed + self.dynamics['AMAX'] * 0.5:
                    self.a = -self.dynamics['AMIN']
                else:
                    self.a = 0
            else:
                # try to reach next node at specified time
                time_left = self.rtas[1] - sim_time
                if time_left < 0:  # just move at maximum target speed
                    if self.v < self.target_speed - self.dynamics['AMAX'] * 0.5:
                        self.a = self.dynamics['AMAX']
                    elif self.v > self.target_speed + self.dynamics['AMAX'] * 0.5:
                        self.a = -self.dynamics['AMIN']
                    else:
                        self.a = 0
                else:
                    dist_left = self.link_distance - self.s
                    if self.v * time_left < dist_left - self.v * 0.5:
                        self.a = self.dynamics['AMAX']
                    elif self.v * time_left > dist_left + self.v * 0.5:
                        self.a = -self.dynamics['AMIN']
                    else:
                        self.a = 0
                    if self.a > 0 and self.target_speed < self.v < self.target_speed + self.dynamics['AMAX'] * 0.5:
                        self.a = 0
                        self.v = self.target_speed
                    elif self.v > self.target_speed + self.dynamics['AMAX'] * 0.5:  # vehicle speed > link speed
                        self.a = -self.dynamics['AMIN']
            self.s += self.v * dt + 0.5 * self.a * dt * dt
            self.v += self.a * dt
            if self.v < 0:
                self.v = 0.0
            if self.v > self.target_speed:
                self.v = self.target_speed

        def update_route():
            while self.s >= self.link_distance:
                self.s -= self.link_distance
                if self.rtas[1] != -1:
                    print('{:<8s} {:<12s} {:>5d} {:>5d}r [{}]'.format(self.callsign, nodes.get_type(self.route[1])[:-5],
                                                                      sim_time, int(self.rtas[1]), self.route[1]))
                self.route.popleft()
                self.rtas.popleft()
                if len(self.route) == 1:
                    # Model take-off or park at gate
                    if self.operation == 'arrival':
                        if self.timer_expiry is None:
                            self.timer_expiry = 900
                            self.timer = 0
                        self.state = 'PARK'
                    elif self.operation == 'departure':  # Model takeoff
                        if self.route[0] == -1:
                            self.state = 'REMOVE'
                        else:
                            airport.update_runway_use(sim_time, self.runway, 'takeoff', self.model)
                            airport.update_fix_use(sim_time, self.fix, 'takeoff', self.model)
                            self.state = 'TAKEOFF'
                            self.link_distance = 10000  # Model terminal space up to 10km
                            self.target_speed = 100  # Cruising speed
                            self.dynamics['AMAX'] *= 2
                            self.route.append(-1)
                            self.rtas.append(-1)
                    return
                self.link_distance = nodes.get_distance(self.route[0], self.route[1])
                link_type = nodes.get_link_type(self.route[0], self.route[1])
                self.target_speed = self.dynamics[link_type if link_type in self.dynamics else 'DEFAULT']
                self.state = link_type
                if nodes.get_type(self.route[0]) == nodes.get_type(self.route[1]) == 'RUNWAY_XING_NODE' and self.v > 0:
                    airport.update_runway_use(sim_time, nodes.get_name(self.route[0]), 'crossing', self.model)

        def check_timer():
            self.timer += 1
            # right now used only for removing aircraft.
            # TODO extend to handle other cases... spool-up, tug-connect, etc.
            if self.timer > self.timer_expiry:
                self.state = 'REMOVE'

        if self.entry_time <= sim_time <= self.active_time:
            if self.operation == 'departure':
                self.state = 'PARK'
                self.s, self.v, self.a = 0, 0, 0
                update_position()
            else:  # Model aircraft landing
                self.state = 'ARRIVAL'
                t = self.active_time - sim_time
                v_cruise, dec_land = 100, 2 * self.dynamics['AMIN']
                dec_time = (v_cruise - self.dynamics['ARRIVAL']) / dec_land
                if t < dec_time:
                    self.s = -self.dynamics['ARRIVAL'] * t - 0.5 * dec_land * t * t
                    self.v = self.dynamics['ARRIVAL'] + dec_land * t
                else:
                    self.s = -(v_cruise ** 2 - self.dynamics['ARRIVAL'] ** 2) / 2 / dec_land - (t - dec_time) * v_cruise
                    self.v = self.dynamics['ARRIVAL'] + dec_land * dec_time
                self.psi = nodes.get_runway_orientation(self.runway)
                self.x, self.y = nodes.get_location(self.route[0]) + self.s * np.array([np.cos(self.psi),
                                                                                        np.sin(self.psi)])
                self.z = 10 * t
                self.s = 0  # if not reset, it can report next link as traveled when out if this loop
                if sim_time - dt < self.active_time < sim_time + dt:
                    airport.update_runway_use(sim_time, self.runway, 'landing', self.model)

        if self.active_time <= sim_time:
            try:
                if len(self.route) > 1:
                    update_kinematics()
                    update_route()
                    update_position()
                else:
                    check_timer()
            except:
                print(self.uid, self.callsign, self.operation, self.route)
                raise
