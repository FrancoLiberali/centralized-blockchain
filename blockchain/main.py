import logging
from multiprocessing import Process, Queue

from blockchain_components import block_builder, miners_coordinator, miner, block_appender
import blockchain_components.mined_counter.initializer
from blockchain_components.common import MINERS_IDS
from common.envvars import MAX_BLOCKS_ENQUEUED_KEY, get_config_param
from common.logger import configure_log, join_logger

def main():
    log_queue, log_listener = configure_log()
    max_blocks_enqueued = get_config_param(MAX_BLOCKS_ENQUEUED_KEY, logging.getLogger("Blockchain main"))

    block_builder_to_miners_coordinator_queue = Queue(
        maxsize=max_blocks_enqueued
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
    block_appender_to_mined_counter_queue = Queue()
    block_appender_p = Process(
        target=block_appender.main, args=(
            (miners_to_block_appender_queue),
            (block_appender_to_miners_coordinator_queue),
            (block_appender_to_mined_counter_queue),
        )
    )
    block_appender_p.start()

    mined_counter_p = Process(
        target=blockchain_components.mined_counter.initializer.initialize, args=(
            (block_appender_to_mined_counter_queue),
        )
    )
    mined_counter_p.start()

    miners_queues = []
    miners = []
    for miner_id in MINERS_IDS:
        miner_queue = Queue()
        miner_p = Process(
            target=miner.main, args=(
                (miner_id), (miner_queue), (miners_to_block_appender_queue))
        )
        miners_queues.append(miner_queue)
        miners.append(miner_p)
        miner_p.start()

    miners_coordinator_p = Process(
        target=miners_coordinator.main, args=(
            (block_builder_to_miners_coordinator_queue),
            (miners_queues),
            (block_appender_to_miners_coordinator_queue)
        )
    )
    miners_coordinator_p.start()

    miners_coordinator_p.join()
    for miner_p in miners:
        miner_p.join()
    block_appender_p.join()
    block_builder_p.join()

    join_logger(log_queue, log_listener)

if __name__ == '__main__':
    main()
