import logging

from config.envvars import MINERS_AMOUNT_KEY, get_config_param

MINERS_AMOUNT = get_config_param(
    MINERS_AMOUNT_KEY, logging.getLogger("Blockchain main")
)
MINERS_IDS = range(1, MINERS_AMOUNT + 1)
