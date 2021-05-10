from threading import Thread, Lock
import datetime
import time

from common import isCryptographicPuzzleSolved

class Miner():
    def __init__(self):
        self.lock = Lock()
        self.block_to_be_mined = None
        self.nonce = 0

    def mine(self, block_appender_queue):
        while True:
            # time.sleep(1)  # TODO borrar, solo para debugging
            with self.lock:
                if self.block_to_be_mined != None:
                    # print(f"minando con dificultad {block_to_be_mined.header['difficulty']}")
                    self.block_to_be_mined.header['timestamp'] = datetime.datetime.now()
                    self.block_to_be_mined.header['nonce'] = self.nonce
                    # print(f"block_to_be_mined: {block_to_be_mined}")
                    if isCryptographicPuzzleSolved(self.block_to_be_mined, self.block_to_be_mined.header['difficulty']):
                        # print("block minado bien piola")
                        block_appender_queue.put(self.block_to_be_mined)
                        break
                    self.nonce += 1


def main(id, coordinator_queue, block_appender_queue):
    miner = Miner()

    t = Thread(target=miner.mine, args=((block_appender_queue),))
    t.start()

    while True:
        new_block = coordinator_queue.get()
        print(f"nuevo bloque recibido: {new_block}")
        with miner.lock:
            print("actualizando valores")
            miner.nonce = 0  # TODO recibir el nonce para que no todos los miners hagan lo mismo
            miner.block_to_be_mined = new_block
            if not t.is_alive(): # sended a block to the block appender an finished
                t = Thread(target=miner.mine, args=((block_appender_queue),))
                t.start()
