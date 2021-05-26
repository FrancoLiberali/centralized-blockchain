import os

MAX_BLOCKS_ENQUEUED_KEY = "MAX_BLOCKS_ENQUEUED"
MINERS_AMOUNT_KEY = "MINERS_AMOUNT"

STORAGE_MANAGER_HOST_KEY = "STORAGE_MANAGER_HOST"
STORAGE_MANAGER_WRITE_PORT_KEY = "STORAGE_MANAGER_WRITE_PORT"
STORAGE_MANAGER_READ_PORT_KEY = "STORAGE_MANAGER_READ_PORT"
STORAGE_MANAGER_READ_PROCESS_AMOUNT_KEY = "READ_PROCESS_AMOUNT"
STORAGE_MANAGER_MINED_PER_MINUTE_PORT_KEY = "STORAGE_MANAGER_MINED_PER_MINUTE_PORT"
STORAGE_MANAGER_MINED_PER_MINUTE_PROCESS_AMOUNT_KEY = "MINED_PER_MINUTE_PROCESS_AMOUNT"

BLOCK_BUILDER_HOST_KEY = "BLOCK_BUILDER_HOST"
BLOCK_BUILDER_PORT_KEY = "BLOCK_BUILDER_PORT"

BLOCK_APPENDER_HOST_KEY = "BLOCK_APPENDER_HOST"
MINED_COUNTER_PORT_KEY = "MINED_COUNTER_PORT"

INT_ENVVARS_KEYS = [
    MAX_BLOCKS_ENQUEUED_KEY,
    MINERS_AMOUNT_KEY,
    STORAGE_MANAGER_WRITE_PORT_KEY,
    STORAGE_MANAGER_READ_PORT_KEY,
    STORAGE_MANAGER_READ_PROCESS_AMOUNT_KEY,
    STORAGE_MANAGER_MINED_PER_MINUTE_PORT_KEY,
    STORAGE_MANAGER_MINED_PER_MINUTE_PROCESS_AMOUNT_KEY,
    BLOCK_BUILDER_PORT_KEY,
    MINED_COUNTER_PORT_KEY,
]

def get_config_param(key, logger):
    try:
        envvar = os.environ[key]
        if key in INT_ENVVARS_KEYS:
            return int(envvar)
        return envvar
    except KeyError as e:
        logger.critical(
            f"Key was not found in EnvVars. Error: {e}. Aborting")
        raise e
    except ValueError as e:
        logger.critical(
            f"Key could not be parsed. Error: {e}. Aborting")
        raise e

def get_config_params(keys, logger):
    config = {}
    for key in keys:
        config[key] = get_config_param(key, logger)
    return config
