# ASSET2 - Airport Surface Simulator and Evaluation Tool 2

[![Build Status](https://travis-ci.org/heronyang/airport-simulation.svg?branch=master)](https://travis-ci.org/heronyang/airport-simulation)

## About

ASSET2 is built for Carnegie Mellon University MSIT Practicum Project, "NASA: Optimization of Airport Surface Planning and Scheduling" in 2017 Fall semester. The team is formed by CMU students and sponsored by NASA Ames Research Center. Please check out following materials for more information.

- [Video](https://www.youtube.com/watch?v=zpHWQc2RBQ0)
- [Slides](doc/practicum/report/slides.pdf)
- [One Pager](doc/practicum/report/one-pager.pdf), [Paper report](doc/practicum/report/report.pdf)

## Prepare airport data

Place airport related data under `data` folder like `data/sfo/build/` (use IATA
airport code).

## Install

    $ pip3 install -r requirements.txt

If you're using Linux system without X11, add `backend : Agg` into `~/.config/matplotlib/matplotlibrc` to avoid X11 error.

## Run

    $ python3 simulator.py -f plans/base.yaml

## Batch Run

    $ python3 simulator.py -f batch_plans/simple-uc.yaml

## Run Tests

    $ python3 -m unittest discover tests    # all tests
    $ python3 -m unittest tests/test_scheduler.py   # single test

## Check Style

    $ pycodestyle --show-pep8 --show-source .
    $ find . -iname "*.py" | xargs pylint    # haven't implemented

## Visiualization

    $ ./visualization/server.py

## Developer Guidelines

### Style

Please always follow [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) for readability and consistency.

### Logging

Default logging level is set in `simulation.py`, and please initialize logging
for each class in `__init__` like this way:

    self.logger = logging.getLogger(__name__)

### Debug

Put breakpoint in this way:

    import pdb; pdb.set_trace()

Also, please refer to our [Google Map](https://drive.google.com/open?id=1votbJbKKRUF5gDumno4GXOxVLAE&usp=sharing) for debugging the details.

### Units

For consistency, following units are used everywhere in the code:

    Time: second
    Length: ft

### Cache

Routing table calculated by the routing expert will be cached at `cache/` so
please make sure all the objects in routing table can be dumped into binary
file using `pickle`. Ex. logger can't be dumped.

Note that cache may cause errors or bugs in many cases because stale data is used.

### Clock

Simulation time (`sim_time`) indicates the time should be passed in each
`tick()` and it can be accessed globally in any place by using following
syntax:

    from clock import Clock
    self.logger.debug("sim time is %s", Clock.sim_time)
