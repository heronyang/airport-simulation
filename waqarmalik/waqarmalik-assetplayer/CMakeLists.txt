cmake_minimum_required(VERSION 2.8.8)
set(TARGET assetplayer)
project(${TARGET})

#set(CMAKE_PREFIX_PATH "/Users/wmalik/Qt/5.2.1/clang_64/")
set(CMAKE_PREFIX_PATH "/usr/local/opt/qt5/")
set(CMAKE_CXX_FLAGS "-std=c++11 -stdlib=libc++")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -stdlib=libc++")
set(CMAKE_AUTOMOC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON) 

set(SOURCES ./src/Main.C 
		./src/GLWindow.C
		./src/States.C
		./src/AssetPlayer.C)

add_executable(${TARGET} ${SOURCES})

find_package(OpenGL REQUIRED)
find_package(Qt5Gui)
find_package(Qt5Core)
find_package(Qt5OpenGL REQUIRED)

qt5_use_modules(${TARGET} Core Gui Opengl)
target_link_libraries(${TARGET} ${OPENGL_LIBRARIES})
ADD_CUSTOM_COMMAND( TARGET ${TARGET} POST_BUILD COMMAND rm -rf data )
ADD_CUSTOM_COMMAND( TARGET ${TARGET} POST_BUILD COMMAND ln -s ${CMAKE_SOURCE_DIR}/data ${CMAKE_CURRENT_BINARY_DIR}/data )

ADD_CUSTOM_TARGET(debug
  COMMAND ${CMAKE_COMMAND} -DCMAKE_BUILD_TYPE=Debug ${CMAKE_SOURCE_DIR}
  COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target all
  COMMENT "Switch CMAKE_BUILD_TYPE to Debug"
  )

ADD_CUSTOM_TARGET(release
  COMMAND ${CMAKE_COMMAND} -DCMAKE_BUILD_TYPE=Release ${CMAKE_SOURCE_DIR}
  COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target all
  COMMENT "Switch CMAKE_BUILD_TYPE to Release"
  )
