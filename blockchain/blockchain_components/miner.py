from common.block import DIFFICULTY_KEY, NONCE_KEY
import logging
from threading import Thread, Lock

from blockchain_components.common import isCryptographicPuzzleSolved, MAX_NONCE

class BlockMinedMessage:
    def __init__(self, miner_id, block):
        self.miner_id = miner_id
        self.block = block

class Miner():
    def __init__(self, id):
        self.id = id
        self.logger = logging.getLogger(name=f"Miner {id}")
        self.lock = Lock()
        self.block_to_be_mined = None

    def mine(self, block_appender_queue):
        while True:
            with self.lock:
                if self.block_to_be_mined != None:
                    if isCryptographicPuzzleSolved(self.block_to_be_mined, self.block_to_be_mined.header[DIFFICULTY_KEY]):
                        self.logger.info(
                            f"Cryptografic puzzle solved with nonce: {self.block_to_be_mined.header[NONCE_KEY]}"
                        )
                        block_appender_queue.put(
                            BlockMinedMessage(self.id, self.block_to_be_mined)
                        )
                        break
                    if self.block_to_be_mined.header[NONCE_KEY] == MAX_NONCE:
                        break
                    self.block_to_be_mined.header[NONCE_KEY] += 1

def main(id, coordinator_queue, block_appender_queue):
    logger = logging.getLogger(name=f"Miner {id} master")
    miner = Miner(id)
    t = None

    while True:
        new_block = coordinator_queue.get()
        logger.info(
            f"Starting to mine block with nonce: {new_block.header[NONCE_KEY]}"
        )
        with miner.lock:
            miner.block_to_be_mined = new_block
            # not t: first block received
            # not t.is_alive(): sended a block to the block appender and finished
            if not t or not t.is_alive(): 
                t = Thread(target=miner.mine, args=((block_appender_queue),))
                t.start()
