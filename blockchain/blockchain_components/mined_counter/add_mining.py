from blockchain_components.mined_counter.common import read_list_from_miner_file, \
    write_list_to_miner_file, \
    mined_per_miner_locks
from common.common import ADD_SUCCESSFUL_MINING_OP, \
    ADD_WRONG_MINING_OP, \
    SUCCESSFUL_INDEX, \
    WRONG_INDEX
from common.logger import Logger

logger = Logger("Mined counter - Add mining")

def add_successful_mining(miner_id):
    add_mining(miner_id, SUCCESSFUL_INDEX)

def add_wrong_mining(miner_id):
    add_mining(miner_id, WRONG_INDEX)

def add_mining(miner_id, mining_type):
    with mined_per_miner_locks[miner_id]:
        mined_by_miner = read_list_from_miner_file(miner_id)
        mined_by_miner[mining_type] = mined_by_miner[mining_type] + 1
        write_list_to_miner_file(miner_id, mined_by_miner)
    logger.info(f"New count of mined by Miner {miner_id} is {mined_by_miner}")

def add_mining_server(block_appender_queue):
    while True:
        message = block_appender_queue.get()
        miner_id = message.miner_id
        if message.operation == ADD_SUCCESSFUL_MINING_OP:
            logger.info(f"Received request to add sucessful mining of Miner {miner_id}")
            add_successful_mining(miner_id)
        elif message.operation == ADD_WRONG_MINING_OP:
            logger.info(f"Received request to add wrong mining of Miner {miner_id}")
            add_wrong_mining(miner_id)