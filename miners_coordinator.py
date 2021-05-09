def main(block_builder_queue, miners_queues):
    # while True:
    difficulty = 1
    last_hash = 0
    for i in range(0, 10):
        block_to_be_mined = block_builder_queue.get()
        block_to_be_mined.header['prev_hash'] = last_hash
        block_to_be_mined.header['difficulty'] = difficulty
        for miner_queue in miners_queues:
            miner_queue.put(block_to_be_mined)
