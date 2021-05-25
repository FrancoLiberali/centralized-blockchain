from common.responses import respond_ok
import datetime
import json
from multiprocessing import Lock, Process, Manager
from concurrent.futures import ProcessPoolExecutor
from common.common import isCryptographicPuzzleSolved, \
    INITIAL_DIFFICULTY, \
    INITIAL_LAST_HASH, \
    STORAGE_MANAGER_HOST, \
    STORAGE_MANAGER_WRITE_PORT, \
    TARGET_TIME_IN_SECONDS, \
    SUCESSFULL_INDEX, \
    WRONG_INDEX, \
    MINERS_AMOUNT, \
    BLOCK_APPENDER_PORT, \
    MINED_PER_MINER_SIZE_LEN_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket
from common.block_interface import send_block_with_hash
from common.logger import Logger

BLOCKS_ADDED_TO_ADJUST_DIFFICULTY = 256

class BlockAppender:
    def __init__(self):
        self.difficulty = INITIAL_DIFFICULTY
        self.last_block_hash = INITIAL_LAST_HASH
        self.start_time = datetime.datetime.now()
        self.blocks_added = 0
        self.socket = SafeTCPSocket.newClient(
            STORAGE_MANAGER_HOST, STORAGE_MANAGER_WRITE_PORT)

    def addBlock(self, block):
        if (self.isBlockValid(block)):
            send_block_with_hash(self.socket, block)
            self.blocks_added += 1
            self.last_block_hash = block.hash()
            self.adjustDifficulty()
            return True
        return False

    def adjustDifficulty(self):
        if self.blocks_added == BLOCKS_ADDED_TO_ADJUST_DIFFICULTY:
            now = datetime.datetime.now()
            elapsed_time = (now -
                            self.start_time).total_seconds()

            self.difficulty = self.difficulty * \
                (TARGET_TIME_IN_SECONDS / elapsed_time) * \
                BLOCKS_ADDED_TO_ADJUST_DIFFICULTY

            self.start_time = now
            self.blocks_added = 0

    def isBlockValid(self, block):
        return block.header['prev_hash'] == self.last_block_hash and isCryptographicPuzzleSolved(block, self.difficulty)

def main(miners_queue, miners_coordinator_queue):
    # TODO desde que saque lo de deamon los procesos ya no me muestran las excepciones
    logger = Logger(f"Block appender")
    for miner_id in range(0, MINERS_AMOUNT):
        mined_per_miner[miner_id] = [0, 0]
    mined_per_miner_server_p = Process(
        target=mined_per_miner_server,
    )
    mined_per_miner_server_p.start()
    
    block_appender = BlockAppender()
    while True:
        message = miners_queue.get()
        block_hash_hex = hex(message.block.hash())
        logger.info(
            f"Received from Miner {message.miner_id} block to be added: {block_hash_hex}"
        )
        if block_appender.addBlock(message.block):
            logger.info(
                f"Block received from Miner {message.miner_id} added to blockchain sucessfully: {message.block}"
            )
            add_successfull_mining(message.miner_id)
            miners_coordinator_queue.put(
                (block_appender.last_block_hash,
                 block_appender.difficulty)
            )
        else:
            logger.info(
                f"Block {block_hash_hex} received from Miner {message.miner_id} couldn't be added to blockchain"
            )
            add_wrong_mining(message.miner_id)


manager = Manager()
mined_per_miner = manager.dict()
mined_per_miner_lock = Lock() # TODO no es lo mas eficiente, lectores-escritores

def add_successfull_mining(miner_id):
    add_mining(miner_id, SUCESSFULL_INDEX)

def add_wrong_mining(miner_id):
    add_mining(miner_id, WRONG_INDEX)

def add_mining(miner_id, mining_type):
    mined = mined_per_miner.get(miner_id, {})
    with mined_per_miner_lock:
        mined[mining_type] = mined[mining_type] + 1
        mined_per_miner[miner_id] = mined

GET_MINED_PER_MINER_PROCESS_AMOUNT = 2 # TODO envvar
# TODO modularizar

def mined_per_miner_server():
    server_socket = SafeTCPSocket.newServer(BLOCK_APPENDER_PORT)
    process_pool = ProcessPoolExecutor(GET_MINED_PER_MINER_PROCESS_AMOUNT)
    while True:
        client_socket,_ = server_socket.accept()
        # TODO
        # enqueued = process_pool._work_queue.qsize()
        # if enqueued > MAX_ENQUEUED_READS:
            # respond_service_unavaliable(client_socket)
            # continue
        process_pool.submit(get_mined_per_miner, client_socket)


def get_mined_per_miner(client_socket):
    with mined_per_miner_lock:
        mined_per_miner_copy = mined_per_miner.copy()
    mined_per_miner_json = json.dumps(
        mined_per_miner_copy,
        indent=4,
        sort_keys=False
    )
    respond_ok(client_socket, close_socket=False)
    client_socket.send_string_with_len_prepended(
        mined_per_miner_json,
        MINED_PER_MINER_SIZE_LEN_IN_BYTES
    )
    client_socket.close()
