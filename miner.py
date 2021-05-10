from threading import Thread, Lock
import datetime
import time

from common import isCryptographicPuzzleSolved

lock = Lock()
block_to_be_mined = None
nonce = 0

def mine(block_appender_queue):
    global block_to_be_mined
    global nonce
    while True:
        time.sleep(1) # TODO borrar, solo para debugging
        with lock:
            if block_to_be_mined != None:
                print("minando")
                block_to_be_mined.header['timestamp'] = datetime.datetime.now()
                block_to_be_mined.header['nonce'] = nonce
                if isCryptographicPuzzleSolved(block_to_be_mined, block_to_be_mined.header['difficulty']):
                    print("block minado bien piola")
                    block_appender_queue.put(block_to_be_mined)
                nonce += 1


def main(id, coordinator_queue, block_appender_queue):
    global block_to_be_mined
    global nonce

    t = Thread(target=mine, args=((block_appender_queue),))
    t.start()

    while True:
        new_block = coordinator_queue.get()
        print("nuevo bloque recibido")
        with lock:
            nonce = 0 # TODO recibir el nonce para que no todos los miners hagan lo mismo
            block_to_be_mined = new_block
