from multiprocessing import Process, Queue
import time
import sys

import block_builder
import miners_coordinator

MAX_BLOCKS_ENQUEUED = 2048

def main():
    pqueue = Queue(maxsize=MAX_BLOCKS_ENQUEUED)

    block_builder_p = Process(target=block_builder.main, args=((pqueue),))
    block_builder_p.daemon = True
    # Launch block_builder_p() as a separate python process
    block_builder_p.start()
    
    miners_coordinator_p = Process(
        target=miners_coordinator.main, args=((pqueue),)
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
