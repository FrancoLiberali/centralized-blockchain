from multiprocessing import Process

from blockchain_components.block_appender.block_appender import block_appender_server
from blockchain_components.block_appender.mined_per_miner import mined_per_miner_server, initialize_mined_per_miner


def initialize(miners_queue, miners_coordinator_queue):
    initialize_mined_per_miner()
    mined_per_miner_server_p = Process(
        target=mined_per_miner_server,
    )
    mined_per_miner_server_p.start()
    block_appender_server(miners_queue, miners_coordinator_queue)
