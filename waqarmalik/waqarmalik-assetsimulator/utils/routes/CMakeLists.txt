CMAKE_MINIMUM_REQUIRED( VERSION 2.6 FATAL_ERROR )
PROJECT(sdssRouteGen)

set(CMAKE_CXX_FLAGS "-g -m64 -std=c++11 -stdlib=libc++")
set(CMAKE_BUILD_TYPE Release)

SET(SOURCES sdssRouteGen.cpp network.cpp routeGen.cpp)

ADD_EXECUTABLE( sdssRouteGen ${SOURCES})
ADD_CUSTOM_COMMAND( TARGET sdssRouteGen POST_BUILD 
 		COMMAND rm -rf  ${CMAKE_CURRENT_BINARY_DIR}/data
		COMMAND ln -s ${CMAKE_SOURCE_DIR}/data ${CMAKE_CURRENT_BINARY_DIR}/data )

# cmake .. -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
