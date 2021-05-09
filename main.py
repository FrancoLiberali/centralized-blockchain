from multiprocessing import Process, Queue
import time
import sys

import block_builder
import miners_coordinator
import miner

MAX_BLOCKS_ENQUEUED = 2048
CANT_MINERS = 2

def main():
    pqueue = Queue(maxsize=MAX_BLOCKS_ENQUEUED)

    block_builder_p = Process(target=block_builder.main, args=((pqueue),))
    block_builder_p.daemon = True
    # Launch block_builder_p() as a separate python process
    block_builder_p.start()

    miners_queues = []
    for miner_id in range(0, CANT_MINERS):
        miner_queue = Queue()
        miner_p = Process(
            target=miner.main, args=((miner_id), (miner_queue), )
        )
        miner_p.daemon = True
        # Launch miner_p() as a separate python process
        miner_p.start()
        miners_queues.append(miner_queue)

    miners_coordinator_p = Process(
        target=miners_coordinator.main, args=((pqueue), (miners_queues),)
    )
    miners_coordinator_p.daemon = True
    # Launch miners_coordinator_p() as a separate python process
    miners_coordinator_p.start()

    # Wait for miners_coordinator_p to finish
    miners_coordinator_p.join()
    # Wait for block_builder_p to finish
    block_builder_p.join()

if __name__ == '__main__':
    main()
