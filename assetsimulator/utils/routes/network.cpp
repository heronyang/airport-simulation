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

#include "network.hpp"

vertex::vertex(double x_i, double y_i, int sossIndex_i, std::string SMSID_i, std::string type_i, int out_i, int in_i) {
    x = x_i;
    y = y_i;
    sossIndex = sossIndex_i;
    SMSID = SMSID_i;
    type = type_i;
    out = out_i;
    in = in_i;

    if (out != in)
        std::cout << "Node " << sossIndex << " has unidirectional links" << std::endl;
}

edge::edge(int from_i, int to_i, std::string label_i, std::string type_i, int direction_i, double length_i, bool undirected_i) {
    from = from_i;
    to = to_i;
    label = label_i;
    type = type_i;
    undirected = undirected_i;
    direction = direction_i;
    length =length_i;
}

network::network(std::string dir) {
    std::ifstream nodeFile( (dir+"nodes.txt").c_str());
    assert(nodeFile);
    double x, y;
    int sossIndex, out, in;
    std::string SMSID, type, spot;
    std::string line, tmp;
    char c;
    std::stringstream ss;
    while (getline(nodeFile, line)) {
        ss << line;
        c = ss.peek();
        if (c != '#' && ss.get(c)) {
            ss.unget();
            ss >> x >> y >> sossIndex >> SMSID >> type >> out >> in;
            //std::cout << x << "\t" << y << "\t" << sossIndex << "\t" << SMSID << "\t" << type << "\t" << out << "\t" << in << std::endl;
            nodes.push_back(vertex(x, y, sossIndex, SMSID, type, out, in));
            if (type=="SPOT_NODE"){ // **BUG** DFW specific
                //spot = "S"+SMSID.substr(4);
                size_t start = SMSID.find("-")+1;
                spot = SMSID.substr( start, SMSID.rfind("-")-start);
                size_t spotNum;
                spotNum=spot.find_first_not_of("0");
                if (spotNum!=std::string::npos)
                    spot = "S"+spot.substr(spotNum);
                else {
                    std::cout << "(WWW) Incorrect SMS spot name for " << sossIndex << " " << SMSID << std::endl;
                    spot = "S1000";
                }
                mapSpot.insert(std::make_pair(spot, sossIndex));
            }
            else if (type=="GATE_NODE"){ // **BUG** DFW specific
                //mapGate.insert(std::make_pair(SMSID.substr(4), sossIndex));
                mapGate.insert(std::make_pair(SMSID, sossIndex));
            }
        }
        while (ss >> tmp) {
        };
        ss.str("");
        ss.clear();
    }
    std::vector<vertex>(nodes).swap(nodes); // Truncate off the excess capacity...

    // check that nodes index is actually sossIndex
    for (unsigned int i = 0; i < nodes.size(); ++i) {
        if (i != (unsigned int) nodes[i].getSOSSIndex()) {
            std::cout << "sossIndex not in order" << std::endl; //can be made better
            assert(false);
        }
    }
    nodeFile.close();

    std::ifstream linkFile((dir+"links.txt").c_str());
    assert(linkFile);
    int num, from, to, direction;
    double length;
    std::string label, linktype;
    line="";
    while (getline(linkFile, line)) {
        ss << line;
        c = ss.peek();
        if (c != '#' && ss.get(c)) {
            ss.unget();
            ss >> num >> from >> to >> tmp >> tmp >> label >> linktype;

            direction = int(atan2( nodes[from].getY() - nodes[to].getY(), nodes[from].getX() - nodes[to].getX() ) * 180 / PI);
            direction = (direction<0)? direction+360 : direction;
            length = sqrt(pow((nodes[from].getY() - nodes[to].getY()), 2) + pow((nodes[from].getX() - nodes[to].getX()), 2));
            //std::cout << num << "\t" << from << "\t" << to << "\t" << tmp << "\t" << tmp << "\t" << label << "\t" << type << std::endl;
            links.push_back(edge(from, to, label, linktype, direction, length, true));
        }
        while (ss >> tmp) {
        };
        ss.str("");
        ss.clear();
    }
    std::vector<edge>(links).swap(links);
    linkFile.close();
    
    
    std::ifstream fixFile((dir+"fixes.txt").c_str());
    assert(fixFile);
    std::string fix, fixType;
    int fixIndex;
    while (getline(fixFile, line)) {
        ss << line;
        c = ss.peek();
        if (c != '#' && ss.get(c)) {
            ss.unget();
            ss >> fix >> fixIndex >> fixType;
            if (fixType=="ARRIVAL_FIX") 
                mapAFix.insert(std::make_pair(fix, fixIndex));
            else if (fixType=="DEPARTURE_FIX")
                mapDFix.insert(std::make_pair(fix, fixIndex));
        }
        while (ss >> tmp) {
        };
        ss.str("");
        ss.clear();
        line="";
    }
    fixFile.close();
    
    std::ifstream rampFile((dir+"ramp.txt").c_str());
    if(rampFile){
        double x, y;
        std::string tmpStr;
        std::vector<std::pair<double, double> > poly;
        while (getline(rampFile, line)) {
            ss << line;
            c = ss.peek();
            if (c != '#' && ss.get(c) && line.length()>2) {
                ss.unget();
                ss >> x >> y;
                poly.push_back(std::make_pair(x, y));
            }
            else if (c != '#'){
                rampPoly.push_back(poly);
                poly.clear();
            }
            while (ss >> tmp) {};
            ss.str("");
            line="";
            ss.clear();
        }
        if(!poly.empty())
            rampPoly.push_back(poly);
    }
    rampFile.close();
    
    std::ifstream rnwyFile((dir+"runways.txt").c_str());
    assert(rnwyFile);
    std::string rnwy, tmpStr;
    int tmpNode;
    int ind=0;
    std::vector<std::pair<double, double> > poly;
    while (getline(rnwyFile, line)) {
        ss << line;
        c = ss.peek();
        if (c != '#' && ss.get(c) && line.length()>2) {
            ss.unget();
            ss >> rnwy >> tmpStr;
            if(tmpStr=="ARRIVAL_NODE" || tmpStr=="RUNWAY_XING_NODE" || tmpStr =="DEPARTURE_NODE"){
                ss >> tmpNode;
                mapRunway.insert(std::make_pair(tmpNode, rnwy));
                if(tmpStr=="RUNWAY_XING_NODE"){
                    ss >> tmpNode;
                    mapRunway.insert(std::make_pair(tmpNode, rnwy));
                }
                std::unordered_map<std::string, int>::const_iterator it = mapRunwayIndex.find(rnwy);
                if (it==mapRunwayIndex.end()){
                    mapRunwayIndex.insert(std::make_pair(rnwy, ind));
                    mapIndexRunway.insert(std::make_pair(ind, rnwy));
                    ind++;
                }
            }
            else if (isdigit(tmpStr[1])){
                if(isdigit(rnwy[2])){
                    poly.push_back(std::make_pair(atof(rnwy.c_str()), atof(tmpStr.c_str())));
                }
                else {
                    runwayPoly.push_back(poly);
                    poly.clear();
                    double tmpD;
                    ss >> tmpD;
                    poly.push_back(std::make_pair(atof(tmpStr.c_str()), tmpD));
                }
            }
            else {
                std::cout << "(EEE) Error in runways.txt -- unknown entry" << std::endl;
            }
        }
        if(!poly.empty())
           runwayPoly.push_back(poly); 
        while (ss >> tmpStr) {
        };
        ss.str("");
        line="";
        ss.clear();
    }
    rnwyFile.close();

}

int network::gateToSOSSNode(std::string str) {
    std::unordered_map<std::string, int>::const_iterator it = mapGate.find(str);
    if (it!=mapGate.end())
        return it->second;
    else{
        std::cout << "ERROR: No node found for gate " << str << std::endl;
        return -1;
    }
}

int network::spotToSOSSNode(std::string str) {
    std::unordered_map<std::string, int>::const_iterator it = mapSpot.find(str);
    if (it!=mapSpot.end())
        return it->second;
    else{
        std::cout << "ERROR: No node found for spot " << str << std::endl;
        return -1;
    }
}
int network::numOfFixes(){
    return mapDFix.size();
}
int network::fixToIndex(std::string str) {
    std::unordered_map<std::string, int>::const_iterator it = mapAFix.find(str);
    if (it!=mapAFix.end())
        return it->second;
    else{
        std::unordered_map<std::string, int>::const_iterator it = mapDFix.find(str);
        if (it!=mapDFix.end())
            return it->second;
        else {
            std::cout << "ERROR: No index found for fix " << str << std::endl;
            return -1;
        }
    }
}

int network::numOfRunways(){
    return mapRunwayIndex.size();
}

int network::runwayToIndex(std::string str) {
    std::unordered_map<std::string, int>::const_iterator it = mapRunwayIndex.find(str);
    if (it!=mapRunwayIndex.end())
        return it->second;
    else{
        std::cout << "ERROR: No index found for runway" << str << std::endl;
        return -1;
    }
}
std::string network::indexToRunway(int ii){
    std::unordered_map<int, std::string>::const_iterator it = mapIndexRunway.find(ii);
    if (it!=mapIndexRunway.end())
        return it->second;
    else{
        std::cout << "ERROR: No runway found for index " << ii << std::endl;
        return "";
    }

}
std::string network::nodeToRunway(int node){
    std::unordered_map<int, std::string>::const_iterator it=mapRunway.find(node);
    if(it!=mapRunway.end())
        return it->second;
    else{
        std::cout << "ERROR: " << node << " is not associated with any runway." << std::endl;
        return("");
    }
}

void network::writeGNUPlotNodes() {
    std::ofstream outFile("plotNodes");
    assert(outFile);
    outFile << "# DFW Node Model for visualization in GNUPlot" << std::endl << std::endl;

    std::string color;
    for (unsigned int i = 0; i < nodes.size(); ++i) {
        if (nodes[i].getType() == "SPOT_NODE")
            color = "0xb20000";
        else if (nodes[i].getType() == "QUEUE_NODE")
            color = "0x32c896";
        else if (nodes[i].getType() == "RAMP_NODE")
            color = "0xff6400";
        else if (nodes[i].getType() == "GATE_NODE")
            color = "0xff0000";
        else if (nodes[i].getType() == "DEPARTURE_NODE")
            color = "0x00ff00";
        else if (nodes[i].getType() == "ARRIVAL_NODE")
            color = "0xff00ff";
        else
            color = "0x000000";

        outFile << std::setw(10) << nodes[i].getX() << std::setw(10) << nodes[i].getY()
                << std::setw(6) << nodes[i].getSOSSIndex() << std::setw(10) << color << std::endl;
    }
    outFile.close();
}

void network::writeGNUPlotLinks() {
    std::ofstream outFile("plotLinks");
    assert(outFile);
    outFile << "# DFW Node-Link Model for visualization in GNUPlot" << std::endl << std::endl;

    std::string color;
    for (unsigned int i = 0; i < links.size(); ++i) {
        if (links[i].getType() == "SPOT_LINK")
            color = "0xb20000";
        else if (links[i].getType() == "QUEUE_LINK")
            color = "0x32c896";
        else if (links[i].getType() == "RAMP_LINK")
            color = "0xff6400";
        else if (links[i].getType() == "RUNWAY_XING_LINK")
            color = "0xff0000";
        else if (links[i].getType() == "DEPARTURE_LINK")
            color = "0x00ff00";
        else if (links[i].getType() == "ARRIVAL_LINK")
            color = "0xff00ff";
        else
            color = "0x000000";

        outFile << std::setw(10) << nodes[links[i].getFrom()].getX() << std::setw(10) << nodes[links[i].getFrom()].getY() << std::setw(6)
                << links[i].getFrom() << std::setw(10) << color << "\t" << links[i].getLength() << std::endl;
        outFile << std::setw(10) << nodes[links[i].getTo()].getX()   << std::setw(10) << nodes[links[i].getTo()].getY()   << std::setw(6)
                << links[i].getTo()   << std::setw(10) << color << "\t" << links[i].getLength() << std::endl << std::endl;
    }
    outFile.close();
}

