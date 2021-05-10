from threading import Thread, Lock
import datetime

from common import isCryptographicPuzzleSolved, MAX_NONCE

class BlockMinedMessage:
    def __init__(self, miner_id, block):
        self.miner_id = miner_id
        self.block = block

class Miner():
    def __init__(self, id):
        self.id = id
        self.lock = Lock()
        self.block_to_be_mined = None

    def mine(self, block_appender_queue):
        while True:
            # time.sleep(1)  # TODO borrar, solo para debugging
            with self.lock:
                if self.block_to_be_mined != None:
                    self.block_to_be_mined.header['timestamp'] = datetime.datetime.now()
                    if isCryptographicPuzzleSolved(self.block_to_be_mined, self.block_to_be_mined.header['difficulty']):
                        block_appender_queue.put(
                            BlockMinedMessage(self.id, self.block_to_be_mined)
                        )
                        break
                    if self.block_to_be_mined.header['nonce'] == MAX_NONCE:
                        break
                    self.block_to_be_mined.header['nonce'] += 1


def main(id, coordinator_queue, block_appender_queue):
    miner = Miner(id)

    t = Thread(target=miner.mine, args=((block_appender_queue),))
    t.start()

    while True:
        new_block = coordinator_queue.get()
        with miner.lock:
            miner.block_to_be_mined = new_block
            if not t.is_alive(): # sended a block to the block appender an finished
                t = Thread(target=miner.mine, args=((block_appender_queue),))
                t.start()
