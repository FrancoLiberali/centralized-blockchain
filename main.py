from multiprocessing import Process, Queue
import time
import sys

import block_builder
import miners_coordinator
import miner
import block_appender
import storage_manager

MAX_BLOCKS_ENQUEUED = 2048 # TODO envvar
CANT_MINERS = 4 # TODO envvar

def main():
    # TODO sacar de aca tiene que ir en otro nodo
    storage_manager_p = Process(target=storage_manager.main)
    storage_manager_p.daemon = True
    # Launch storage_manager_p() as a separate python process
    storage_manager_p.start()
    # fin TODO

    block_builder_to_miners_coordinator_queue = Queue(
        maxsize=MAX_BLOCKS_ENQUEUED
    )

    block_builder_p = Process(
        target=block_builder.main,
        args=(
            (block_builder_to_miners_coordinator_queue),
        )
    )
    block_builder_p.daemon = True
    # Launch block_builder_p() as a separate python process
    block_builder_p.start()

    miners_to_block_appender_queue = Queue()
    block_appender_to_miners_coordinator_queue = Queue()
    block_appender_p = Process(
        target=block_appender.main, args=(
            (miners_to_block_appender_queue),
            (block_appender_to_miners_coordinator_queue)
        )
    )
    block_appender_p.daemon = True
    # Launch block_appender_p() as a separate python process
    block_appender_p.start()

    miners_queues = []
    for miner_id in range(0, CANT_MINERS):
        miner_queue = Queue()
        miner_p = Process(
            target=miner.main, args=(
                (miner_id), (miner_queue), (miners_to_block_appender_queue))
        )
        miner_p.daemon = True
        # Launch miner_p() as a separate python process
        miner_p.start() # TODO investigar que es esto
        miners_queues.append(miner_queue)

    miners_coordinator_p = Process(
        target=miners_coordinator.main, args=(
            (block_builder_to_miners_coordinator_queue),
            (miners_queues),
            (block_appender_to_miners_coordinator_queue)
        )
    )
    miners_coordinator_p.daemon = True
    # Launch miners_coordinator_p() as a separate python process
    miners_coordinator_p.start()

    miners_coordinator_p.join()
    # TODO join miners
    block_appender_p.join()
    block_builder_p.join()

if __name__ == '__main__':
    main()
