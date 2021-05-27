import logging

from config.envvars import MINERS_AMOUNT_KEY, get_config_param

MINERS_AMOUNT = get_config_param(
    MINERS_AMOUNT_KEY, logging.getLogger("Blockchain main")
)
MINERS_IDS = range(1, MINERS_AMOUNT + 1)

INITIAL_LAST_HASH = 0
INITIAL_DIFFICULTY = 1
MAX_NONCE = 2**(32*8) - 1  # max number posible in 32 bytes


def isCryptographicPuzzleSolved(block, difficulty):
    return block.hash() < (2**256) / difficulty - 1
