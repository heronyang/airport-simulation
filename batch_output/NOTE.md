## S/L Experiment: Times: 15

S/L Experiments are used for testing and debugging.

- `sfo-terminal-2-rt-s/`
- `sfo-terminal-2-rt/`
- `sfo-terminal-2-uc-l/`
- `sfo-terminal-2-uc/`
- `simple-rt-s/`
- `simple-uc-s/`

## XL Experiment: Times: 15

XL Experiments run the plots we planned to put into the paper. However, we found:

- `sfo-terminal-2-rt-xl/`: Uncertainty amount is too small so there's not much different in the result graph. Also, the value range for the experimental variable is too small to create an intense scheduling problem.
- `sfo-terminal-2-uc-xl/`: Rescheduling time is too small that it's hard to create an intense scheduling problem.

## XXL Experiment: Times: 30

- `sfo-terminal-2-rt-xl/`
- `sfo-terminal-2-uc-xl/`

## Refined Experiment: Times: 20

Scenario: 00:00 - 09:00, mean 180 sec, deviation 30 sec

- `sfo-terminal-2-uc`: 0, 0.01, 0.02, ..., 0.15 (rt = 120)
# - `sfo-terminal-2-rt`: 120, 180, ... 900
