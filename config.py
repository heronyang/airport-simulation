"""`Config` extends `MetaConfig` and it reads configurations from a given yaml
file. A default yaml is also provided so the user only has to specify the
parameters that are different from the default one.
"""
import yaml
from utils import update_dict
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_LINE_EXPERIMENT_PLAN_FILEPATH = BASE_DIR + "/plans/base.yaml"


class MetaConfig(type):
    """`MetaConfig` is a generic configuration class that offers `params`
    dictionary of all configurations and `load_plan` for loading configurations
    from a yaml file.
    """

    @property
    def params(cls):
        """Returns a dictionary of the configuration parameters."""
        # Lazy initialization with base-line configurations
        if getattr(cls, "_params", None) is None:
            with open(BASE_LINE_EXPERIMENT_PLAN_FILEPATH) as fout:
                cls._params = yaml.load(fout)
        return cls._params

    def load_plan(cls, config_filepath):
        """Loads a plan from file."""
        with open(config_filepath) as fout:
            new_params = yaml.load(fout)
            update_dict(cls.params, new_params)


class Config(metaclass=MetaConfig):
    """`Config` extends `MetaConfig` by adding constant variables that used by
    the simulation.
    """

    LOG_FORMAT = "[%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    DATA_ROOT_DIR_PATH = BASE_DIR + "/data/%s/build/"
    DATA_GENERATION_DIR_PATH = BASE_DIR + "/data/%s/"
    OUTPUT_DIR = BASE_DIR + "/output/"
    PLANS_DIR = BASE_DIR + "/plans/"
    BATCH_OUTPUT_DIR = BASE_DIR + "/batch_output/"

    SCHEDULER_DIR_NAME = "scheduler"
    OUTPUT_FIG_DPI = 150
    OUTPUT_FIG_SIZE = (20, 10)
    OUTPUT_FIG_X_ROT = 90

    DECIMAL_ROUND = 7
