import logging

from business.block_appender import BlockAppender
from communications.block_interface import send_block_with_hash
from communications.constants import ADD_SUCCESSFUL_MINING_OP, ADD_WRONG_MINING_OP
from communications.safe_tcp_socket import SafeTCPSocket
from config.envvars import STORAGE_MANAGER_HOST_KEY, STORAGE_MANAGER_WRITE_PORT_KEY, get_config_params

def main(miners_queue, miners_coordinator_queue, mined_counter_queue):
    logger = logging.getLogger(name="Block appender")
    config_params = get_config_params(
        [STORAGE_MANAGER_HOST_KEY, STORAGE_MANAGER_WRITE_PORT_KEY],
        logger
    )

    block_appender = BlockAppender()
    socket_to_storage_manager = SafeTCPSocket.newClient(
        config_params[STORAGE_MANAGER_HOST_KEY],
        config_params[STORAGE_MANAGER_WRITE_PORT_KEY]
    )
    while True:
        message = miners_queue.get()
        block_hash_hex = hex(message.block.hash())
        logger.info(
            f"Received from Miner {message.miner_id} block to be added: {block_hash_hex}"
        )
        block = message.block
        if block_appender.addBlock(block):
            send_block_with_hash(socket_to_storage_manager, block)
            logger.info(
                f"Block received from Miner {message.miner_id} added to blockchain sucessfully: {block}"
            )
            send_add_successful_mining(mined_counter_queue, message.miner_id)
            miners_coordinator_queue.put(
                (block_appender.last_block_hash,
                 block_appender.difficulty)
            )
        else:
            logger.info(
                f"Block {block_hash_hex} received from Miner {message.miner_id} couldn't be added to blockchain"
            )
            send_add_wrong_mining(mined_counter_queue, message.miner_id)


class NewMinedMessage:
    def __init__(self, miner_id, block):
        self.miner_id = miner_id
        self.operation = block

def send_add_successful_mining(mined_counter_queue, miner_id):
    mined_counter_queue.put(
        NewMinedMessage(miner_id, ADD_SUCCESSFUL_MINING_OP)
    )

def send_add_wrong_mining(mined_counter_queue, miner_id):
    mined_counter_queue.put(
        NewMinedMessage(miner_id, ADD_WRONG_MINING_OP)
    )
