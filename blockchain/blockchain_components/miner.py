from threading import Thread, Lock

from common.common import isCryptographicPuzzleSolved, MAX_NONCE
from common.logger import Logger

class BlockMinedMessage:
    def __init__(self, miner_id, block):
        self.miner_id = miner_id
        self.block = block

class Miner():
    def __init__(self, id):
        self.id = id
        self.logger = Logger(f"Miner {id}")
        self.lock = Lock()
        self.block_to_be_mined = None

    def mine(self, block_appender_queue):
        while True:
            with self.lock:
                if self.block_to_be_mined != None:
                    if isCryptographicPuzzleSolved(self.block_to_be_mined, self.block_to_be_mined.header['difficulty']):
                        self.logger.info(
                            f"Cryptografic puzzle solver with nonce: {self.block_to_be_mined.header['nonce']}"
                        )
                        block_appender_queue.put(
                            BlockMinedMessage(self.id, self.block_to_be_mined)
                        )
                        break
                    if self.block_to_be_mined.header['nonce'] == MAX_NONCE:
                        break
                    self.block_to_be_mined.header['nonce'] += 1

def main(id, coordinator_queue, block_appender_queue):
    logger = Logger(f"Miner {id} master")
    miner = Miner(id)
    t = None

    while True:
        new_block = coordinator_queue.get()
        logger.info(
            f"Starting to mine block with nonce: {new_block.header['nonce']}"
        )
        with miner.lock:
            miner.block_to_be_mined = new_block
            # not t: first block received
            # not t.is_alive(): sended a block to the block appender and finished
            if not t or not t.is_alive(): 
                t = Thread(target=miner.mine, args=((block_appender_queue),))
                t.start()
