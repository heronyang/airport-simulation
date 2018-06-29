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

/**
 *  RouteGen.cpp
 *
 *
 *  Created by Waqar Malik on 9/29/10.
 *  Updated 05/20/11
 *  Copyright 2010 NASA Ames. All rights reserved.
 *
 */
// Make sure "xxx/AllPairsRoutes" is removed if nodes.txt and links.txt are updated.

#include "routeGen.hpp"

routeGen::routeGen(std::shared_ptr<network> nodelink, std::string dir) :
INF((std::numeric_limits<int>::max)() / 3) {
	net.swap(nodelink);
    
	unsigned int numNodes = net->nodes.size();
	std::vector<std::vector<double> > graph1(numNodes, std::vector<double>(numNodes, (double) INF));
    
	for (std::vector<edge>::const_iterator it = net->links.begin(); it != net->links.end(); ++it) {
		graph1[it->getFrom()][it->getTo()] = it->getLength();
        
		if (it->getUndirected()) graph1[it->getTo()][it->getFrom()] = it->getLength();
	}
    
	std::vector<std::vector<short> > pred1(numNodes);
	for (unsigned short i = 0; i < numNodes; ++i)
		pred1[i] = std::vector<short>(numNodes, i);
    
	graph.swap(graph1);
	pred.swap(pred1);
    
	std::ifstream inFile((dir + "AllPairsRoutes").c_str()); // previously calculated shortest path
	if (inFile) {
		for (unsigned int i = 0; i < pred.size(); ++i) {
			for (unsigned int j = 0; j < pred[i].size(); ++j)
				inFile >> pred[i][j];
		}
	}
	else { // No previous runs
		FloydWarshall(); // This completes most of the computation and creates the pred/dist table.
		std::ofstream outFile((dir + "AllPairsRoutes").c_str());
		for (unsigned int i = 0; i < pred.size(); ++i) {
			for (unsigned int j = 0; j < pred[i].size(); ++j)
				outFile << pred[i][j] << " ";
      outFile << std::endl;
		}
		outFile.close();
	}
	inFile.close();
    
}

void routeGen::FloydWarshall() {
	std::vector<std::vector<double> > distance = graph; // d[i][j] = shortest distance from i to j
	for (unsigned int kk = 0; kk < graph.size(); ++kk) {
		std::cout << ".";
		std::flush(std::cout);
		for (unsigned int ii = 0; ii < graph.size(); ++ii) {
			for (unsigned int jj = 0; jj < graph.size(); ++jj)
				if (distance[ii][jj] > (distance[ii][kk] + distance[kk][jj])) {
					distance[ii][jj] = distance[ii][kk] + distance[kk][jj];
					pred[ii][jj] = short(kk);
				}
		}
	}
	// Output msg about missing path if if any d[i][j] is INF
}

void routeGen::getPath(int from, int to, std::vector<int>& path) {
	if (from == to) // no nodes in between
		return;
	else if ((pred[from][to] == from) || (pred[from][to] == to)) // no nodes in between
		return;
	else {
		//recursive: GetPath(i,intermediate) + intermediate + GetPath(intermediate,j)
		getPath(from, pred[from][to], path);
		path.push_back(pred[from][to]);
		getPath(pred[from][to], to, path);
	}
}

bool routeGen::getShortestPath(int from, int to, std::vector<int>& path) {
	// Assumption: a path exists from-->to. Keeping and checking distance matrix for INF was memory intensive.
	if (path.empty()) 
    path.push_back(from); // add first node
	getPath(from, to, path);
	path.push_back(to); // add last node
	return true;
}

std::vector<int> routeGen::getRoute(int from, int to, std::list<int> viaNodes) {
	viaNodes.push_front(from);
	viaNodes.push_back(to);
    
	std::vector<int> route;
	std::list<int>::const_iterator listItPrev = viaNodes.begin();
	std::list<int>::const_iterator listIt = viaNodes.begin();
	++listIt;
	for (; listIt != viaNodes.end(); ++listIt) {
		getShortestPath(*listItPrev, *listIt, route);
		++listItPrev;
	}
	std::vector<int>(route).swap(route);
    
	return route;
}

