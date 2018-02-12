import os

import numpy as np
import json
from utils import str2time
from config import Config

class Uncertainty:
    
    sigma = 0.1

    """
    A generic module to calculate uncertainty over multiple factors
    """
    def __init__(self, seed = Config.params["uncertainty"]["seed"]):

        self.seed = seed
        self.__initialize_distribution()

    @property
    def range(self):
        if self.__range is None:
            r = p_uc["range_threshold"] * np.random.random_sample((2, ))
            uc_min = max(0, seed - r[0])
            uc_max = min(1, seed + r[1])
            self.range = (uc_min, uc_max)
        return self.__range

    """
    Gets the uncertain value based on a normal distribution by default
    """
    def get_uncertain_value(self, original_value, on="SPEED"):
        return self.__get_default_uncertainty(original_value)
    
    def __get_default_uncertainty(self, original_value):
        return np.random.normal(original_value, Uncertainty.sigma)

    def __initialize_distribution(self):
        self.update(self.seed)

    def aircraft_can_move(self, aircraft):
        unc = min(self.seed * 1.5, 0.9) if is_terminal else self.seed
        return np.random.random() > unc
    
    def __initialize_distribution_with_file(self):
        sigma = 0
        filepath = self.factor_filepath
        
        # Check for valid factor file path
        if not os.path.exists(filepath):
            raise Exception("Factor data file is not provided")
            
        with open(filepath, "r") as f:
            factor_val = json.load(f)                
            for factor in factor_val:
                v = str(factor.get("relation"))
                if v == "DIRECT":
                    sigma = sigma + float(factor.get("value"))
                elif v == "INVERSE":
                    sigma = sigma + 1/float(factor.get("value"))
        self.update(sigma)
    
    @classmethod
    def update(self, value):
        self.sigma = value
