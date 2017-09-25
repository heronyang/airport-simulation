# Airport Simulation

## Design Document

[here](https://github.com/heronyang/airport-simulation/wiki/Airport-Simulation)

## Prepare airport data

Place airport related data under `data` folder like `data/sfo` (use IATA
airport code).

## Installation

    $ pip3 install --user -r requirements.txt
    $ brew install pyqt # install python qt for mac users
    $ sudo apt-get install python-qt5 # for Ubuntu users

## Run Tests

    $ python3 -m unittest discover tests

## Run

    $ python3 run.py --airport sfo --schedule sep-11
