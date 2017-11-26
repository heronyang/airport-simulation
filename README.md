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
    $ python3 simulator.py -a sfo -tp 0 # without pause

## Run Tests

    $ python3 -m unittest discover tests

## Developer Guidelines

### Style

**[IMPORTANT] Please always follow [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) for readability and consistency.**

### Logging

Default logging level is set in `simulation.py`, and please initialize logging
for each class in `__init__` like this way:

    self.logger = logging.getLogger(__name__)

### Debug

**[IMPORTANT]** Put breakpoint in this way (make sure IPython is installed):

    from IPython.core.debugger import Tracer; Tracer()()

Also, please refer to our [Google Map](https://drive.google.com/open?id=1votbJbKKRUF5gDumno4GXOxVLAE&usp=sharing) for debugging the details.

### Units

For consistency, following units are used everywhere in the code:

    Time: second
    Length: ft

### Cache

Routing table calculated by the routing expert will be cached at `cache/` so
please make sure all the objects in routing table can be dumped into binary
file using `pickle`. Ex. logger can't be dumped.

### Clock

Simulation time (`sim_time`) indicates the time should be passed in each
`tick()` and it can be accessed globally in any place by using following
syntax:

    from clock import Clock
    self.logger.debug("sim time is %s", Clock.sim_time)
