import yaml

"""
Configuration parameters are lazy-loaded, and a baseline file is provided which
enables users to only provide configuration parameters that are different from
the baseline.
"""

class MetaConfig(type):

    BASE_LINE_EXPERIMENT_PLAN_FILEPATH = "./experiment_plans/base.yaml"

    @property
    def params(cls):
        if getattr(cls, "_params", None) is None:
            with open(MetaConfig.BASE_LINE_EXPERIMENT_PLAN_FILEPATH) as f:
                cls._params = yaml.load(f)
        return cls._params

    def load_experiment_plan(cls, config_filepath):
        with open(MetaConfig.BASE_LINE_EXPERIMENT_PLAN_FILEPATH) as f:
            baseline_params = yaml.load(f)
        with open(config_filepath) as f:
            cls._params = {**baseline_params, **yaml.load(f)}

class Config(metaclass = MetaConfig):

    LOG_FORMAT = "%(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    DATA_ROOT_DIR_PATH = "./data/%s/build/"
