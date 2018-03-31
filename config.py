import yaml
from utils import update_dict


class MetaConfig(type):

    BASE_LINE_EXPERIMENT_PLAN_FILEPATH = "./plans/base.yaml"

    @property
    def params(self):
        # Lazy initialization with base-line configurations
        if getattr(self, "_params", None) is None:
            with open(MetaConfig.BASE_LINE_EXPERIMENT_PLAN_FILEPATH) as f:
                    self._params = yaml.load(f)
        return self._params

    def load_plan(self, config_filepath):
        with open(config_filepath) as f:
            new_params = yaml.load(f)
            update_dict(self.params, new_params)


class Config(metaclass=MetaConfig):

    LOG_FORMAT = "[%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    DATA_ROOT_DIR_PATH = "./data/%s/build/"
    OUTPUT_DIR = "./output/"
    BATCH_OUTPUT_DIR = "./batch_output/"

    SCHEDULER_DIR_NAME = "scheduler"
