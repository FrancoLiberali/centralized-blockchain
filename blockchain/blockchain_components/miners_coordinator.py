import copy
import logging
import datetime

from business.block import DIFFICULTY_KEY, NONCE_KEY, PREV_HASH_KEY, TIMESTAMP_KEY, MAX_NONCE
from business.block_appender import INITIAL_DIFFICULTY, INITIAL_LAST_HASH

def main(block_builder_queue, miners_queues, block_appender_queue):
    logger = logging.getLogger(name="Miners coordinator")
    last_hash = INITIAL_LAST_HASH
    difficulty = INITIAL_DIFFICULTY
    nonce_range_per_miner = int(MAX_NONCE // len(miners_queues))
    while True:
        block_to_be_mined = block_builder_queue.get()
        block_to_be_mined.header[TIMESTAMP_KEY] = datetime.datetime.now()
        block_to_be_mined.header[PREV_HASH_KEY] = last_hash
        block_to_be_mined.header[DIFFICULTY_KEY] = difficulty
        logger.info(
            f"Sending block to all miners: {block_to_be_mined}"
        )
        send_block_to_miners(
            block_to_be_mined, miners_queues, nonce_range_per_miner)
        last_hash, difficulty = block_appender_queue.get()


def send_block_to_miners(block_to_be_mined, miners_queues, nonce_range_per_miner):
    for i, miner_queue in enumerate(miners_queues):
        # if i dont use deepcopy the nonce is the same for all miners,
        # probably because queue put is buffered and then the only existing
        # instance of block_to_be_mined is the last one
        block = copy.deepcopy(block_to_be_mined)
        block.header[NONCE_KEY] = nonce_range_per_miner * i
        miner_queue.put(block)
