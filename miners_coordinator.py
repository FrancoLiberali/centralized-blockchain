from common import isCryptographicPuzzleSolved, INITIAL_DIFFICULTY, INITIAL_LAST_HASH

def main(block_builder_queue, miners_queues, block_appender_queue):
    last_hash = INITIAL_LAST_HASH
    difficulty = INITIAL_DIFFICULTY
    while True:
        block_to_be_mined = block_builder_queue.get()
        block_to_be_mined.header['prev_hash'] = last_hash
        block_to_be_mined.header['difficulty'] = difficulty
        for miner_queue in miners_queues:
            miner_queue.put(block_to_be_mined)
        last_hash, difficulty = block_appender_queue.get()
