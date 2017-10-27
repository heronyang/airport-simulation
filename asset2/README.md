# Airport Simulation

## Design Document

[here](https://github.com/heronyang/airport-simulation/wiki/Airport-Simulation)

## Prepare airport data

Place airport related data under `data` folder like `data/sfo/build/` (use IATA
airport code).

## Installation

    $ pip3 install --user -r requirements.txt
    $ brew install pyqt # install python qt for mac users
    $ sudo apt-get install python-qt5 # for Ubuntu users

## Run

    $ python3 simulator.py --airport sfo # without graphical minotor
    $ python3 simulator.py --airport sfo -g # with graphical minotor
    $ python3 simulator.py --help

## Run Tests

    $ python3 -m unittest discover tests

## Developer Guidelines

### Logging

Default logging level is set in `simulation.py`, and please initialize logging
for each class in `__init__` like this way:

    self.logger = logging.getLogger(__name__)

### Debug

Put breakpoint in this way (make sure IPython is installed):

    from IPython.core.debugger import Tracer; Tracer()()

### Units

For consistency, following units are used everywhere in the code:

    Time: second
    Length: ft
