/**
 *  Copyright 2011 Waqar Malik <waqarmalik@gmail.com>
 *  Copyright 2011 SESO Group at NASA Ames
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 */

#ifndef __NETWORK_HPP__
#define __NETWORK_HPP__

#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <cassert>
#include <cmath>
#include <unordered_map>

const double PI = 3.14159265;

class vertex {
public:
    vertex(double x_i, double y_i, int sossIndex_i, std::string SMSID_i, std::string type_i, int out_i, int in_i);
    double getX() { return x; }
    double getY() { return y; }
    int getSOSSIndex() { return sossIndex; }
    std::string getSMSID() { return SMSID; }
    std::string getType() { return type; }
    int getOut() { return out; } 
    int getIn() { return in; } 
private:
    double x, y;
    int sossIndex;
    std::string SMSID;
    std::string type;
    int out;
    int in;
};

class edge {
public:
    edge(int from_i, int to_i, std::string label_i, std::string type_i, int direction_i, double length_i, bool undirected_i);
    void setLength(double length_i) { length = length_i; }
    int getFrom() const  { return from; }
    int getTo() const { return to; }
    std::string getLabel() const { return label; }
    std::string getType() const { return type; }
    int getDirection() { return direction; }
    double getLength() const { return length; }
    bool getUndirected() const { return undirected; }

private:
    int from, to, direction;
    double length;
    std::string label;
    std::string type;
    bool undirected;
};

class network {
public:
    network(std::string);
    int gateToSOSSNode(std::string); // A9, B24, etc... (-1 ERROR)
    int spotToSOSSNode(std::string); // S5, S14, S113, etc...(-1 ERROR)
    int numOfFixes();
    int fixToIndex(std::string);
    int numOfRunways();
    int runwayToIndex(std::string);
    std::string indexToRunway(int);
    std::string nodeToRunway(int node);
    void writeGNUPlotNodes();
    void writeGNUPlotLinks();

    std::vector<vertex> nodes;
    std::vector<edge> links;
    
    std::vector< std::vector< std::pair<double, double> > > runwayPoly;
    std::vector< std::vector< std::pair<double, double> > > rampPoly;
    
private:
    std::unordered_map<std::string, int> mapGate;
    std::unordered_map<std::string, int> mapSpot;
    std::unordered_map<std::string, int> mapDFix;
    std::unordered_map<std::string, int> mapAFix;
    std::unordered_map<int, std::string> mapRunway;
    std::unordered_map<std::string, int> mapRunwayIndex;
    std::unordered_map<int, std::string> mapIndexRunway;
};


#endif
