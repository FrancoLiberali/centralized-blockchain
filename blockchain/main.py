from multiprocessing import Process, Queue
import sys
sys.path.append(".")

from blockchain_components import block_builder, miners_coordinator, miner, block_appender
from common.common import MINERS_AMOUNT

MAX_BLOCKS_ENQUEUED = 2048 # TODO envvar

def main():
    block_builder_to_miners_coordinator_queue = Queue(
        maxsize=MAX_BLOCKS_ENQUEUED
    )

    block_builder_p = Process(
        target=block_builder.main,
        args=(
            (block_builder_to_miners_coordinator_queue),
        )
    )
    block_builder_p.start()

    miners_to_block_appender_queue = Queue()
    block_appender_to_miners_coordinator_queue = Queue()
    block_appender_p = Process(
        target=block_appender.main, args=(
            (miners_to_block_appender_queue),
            (block_appender_to_miners_coordinator_queue)
        )
    )
    block_appender_p.start()

    miners_queues = []
    for miner_id in range(0, MINERS_AMOUNT):
        miner_queue = Queue()
        miner_p = Process(
            target=miner.main, args=(
                (miner_id), (miner_queue), (miners_to_block_appender_queue))
        )
        miner_p.start()
        miners_queues.append(miner_queue)

    miners_coordinator_p = Process(
        target=miners_coordinator.main, args=(
            (block_builder_to_miners_coordinator_queue),
            (miners_queues),
            (block_appender_to_miners_coordinator_queue)
        )
    )
    miners_coordinator_p.start()

    miners_coordinator_p.join()
    # TODO join miners
    block_appender_p.join()
    block_builder_p.join()

if __name__ == '__main__':
    main()
