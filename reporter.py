import json
from config import Config as cfg

def save_batch_result(name, expr_var_range):
    batch_output_dir = cfg.BATCH_OUTPUT_DIR
    metrics = []
    for expr_var in expr_var_range:
        filename = cfg.OUTPUT_DIR + name + "-batch-" + str(expr_var) +\
                "/metrics.json"
        with open(filename) as f:
            d = json.load(f)
            metrics.append([expr_var, d])
    print(metrics)

import numpy
save_batch_result("simple-continuous-uc", numpy.arange(0.0, 0.8, 0.2))
