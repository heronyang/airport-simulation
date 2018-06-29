//============================================================================
// Name        : sdssRouteGen.cpp
// Author      : Waqar Malik
// Version     :
// Copyright   : UARC - NASA Ames
// Description : Sample file to test routeGen
//============================================================================

#include <memory>
#include <string>
#include "network.hpp"
#include "routeGen.hpp"

int main(int argc, char *argv[]) {
  if (argc<2){
    std::cout << "Usage: ./sdssRouteGen ./airport_dir/ <from> <to> <via_nodes>" << std::endl;
    return 0;
  }
  std::string dir = argv[1];  
  int from = (argc > 2) ? atoi(argv[2]) : 0;
  int to = (argc > 3) ? atoi(argv[3]) : 1;
  
  std::list<int> viaNodes;
  if (argc > 4){
    for (int i=4; i<argc; ++i)
      viaNodes.push_back(atoi(argv[i]));
  }

	std::cout << "\n\nReading airport model......";
	std::flush(std::cout);
	std::shared_ptr<network> net(new network(dir));

	std::cout << "[OK]\nSynthesizing all-pairs shortest path......";
	std::flush(std::cout);
	routeGen allRoutes(net, dir);
	std::cout << " [OK]" << std::endl;

	std::vector<int> path;
	allRoutes.getShortestPath(from, to, path);
  std::cout << "\r\nShortest Path "<< from << " --> " << to << std::endl;
	for(unsigned int i=0; i<path.size(); ++i)
	  std::cout << path[i] << " ";
	std::cout<< "\r\n" << std::endl;

	if (!viaNodes.empty()){
    path = allRoutes.getRoute(from,to, viaNodes);
    std::cout << "Path "<< from << " --> " << to;
      std::cout << " via nodes ";
      for ( auto& via : viaNodes)
        std::cout << via << " ";
  
    std::cout << std::endl;
	  for(unsigned int i=0; i<path.size(); ++i)
	    std::cout << path[i] << " ";
	  std::cout<< "\r\n" << std::endl;
  }
	
  return 0;
}
