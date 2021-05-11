from common.common import INITIAL_DIFFICULTY, INITIAL_LAST_HASH, MAX_NONCE
import copy

def main(block_builder_queue, miners_queues, block_appender_queue):
    last_hash = INITIAL_LAST_HASH
    difficulty = INITIAL_DIFFICULTY
    nonce_range_per_miner = int(MAX_NONCE // len(miners_queues))
    while True:
        block_to_be_mined = block_builder_queue.get()
        block_to_be_mined.header['prev_hash'] = last_hash
        block_to_be_mined.header['difficulty'] = difficulty
        for i, miner_queue in enumerate(miners_queues):
            # if i dont use deepcopy the nonce is the same for all miners,
            # probably because queue put is buffered and then the only existing
            # instance of block_to_be_mined is the last one
            block = copy.deepcopy(block_to_be_mined)
            block.header['nonce'] = nonce_range_per_miner * i
            miner_queue.put(block)
        last_hash, difficulty = block_appender_queue.get()