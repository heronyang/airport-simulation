# Waqarmalik

## Prerequisite (Mac, Homebrew)

### Install CMake

    $ brew install cmake
    $ cmake --help

### Install Qt5OpenGL:

    $ brew install qt5
    $ ls /usr/local/opt/qt5/lib/cmake/Qt5Widgets/Qt5WidgetsConfig.cmake
    $ export CMAKE_PREFIX_PATH=/usr/local/opt/qt5/

## Build

    $ cd assetplayer/build
    $ make

## Run Player

    $ ./assetplayer --airport=KDFW --track=out-20.asset

## Run Simulator

### Server

    $ pip3 install --user pandas
    $ python3 kdfw_scheduler.py

### Client

    $ python3 simulate.py --airport=kdfw --scenario=data/scen-dfw.scenario --cdr
