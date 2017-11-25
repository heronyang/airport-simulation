class Config:

    DATA_ROOT_DIR_PATH = "./data/%s/build/"

    DEFAULT_TICK_PAUSE_TIME = 1
    DEFAULT_TICK_SIM_TIME = 5 * 60
    DEFAULT_SCHEDULE_SIM_TIME = 15 * 60

    CLOSE_NODE_THRESHOLD_FEET = 30

    INFINITE_DISTANCE = 9999999999  # Longer than any distance on earth surface

    PILOT_EXPECTED_VELOCITY = 5    # ft/sec, around 3.40909 mph
	
    MIN_TIGHTNESS = 10 * 60

    UNCERTAINTY_RANGE_THRESHOLD = 0.2