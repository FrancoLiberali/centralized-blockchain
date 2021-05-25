from concurrent.futures import ProcessPoolExecutor
import json
from multiprocessing import Lock, Manager

from common.common import MINERS_AMOUNT, \
    SUCESSFULL_INDEX, \
    WRONG_INDEX, \
    BLOCK_APPENDER_PORT, \
    MINED_PER_MINER_SIZE_LEN_IN_BYTES
from common.responses import respond_ok
from common.safe_tcp_socket import SafeTCPSocket

manager = Manager()
mined_per_miner = manager.dict()
mined_per_miner_lock = Lock()  # TODO no es lo mas eficiente, lectores-escritores


def initialize_mined_per_miner():
    for miner_id in range(0, MINERS_AMOUNT):
        mined_per_miner[miner_id] = [0, 0]


def add_successfull_mining(miner_id):
    add_mining(miner_id, SUCESSFULL_INDEX)


def add_wrong_mining(miner_id):
    add_mining(miner_id, WRONG_INDEX)


def add_mining(miner_id, mining_type):
    with mined_per_miner_lock:
        mined = mined_per_miner[miner_id]
        mined[mining_type] = mined[mining_type] + 1
        mined_per_miner[miner_id] = mined


GET_MINED_PER_MINER_PROCESS_AMOUNT = 2  # TODO envvar

def mined_per_miner_server():
    server_socket = SafeTCPSocket.newServer(BLOCK_APPENDER_PORT)
    process_pool = ProcessPoolExecutor(GET_MINED_PER_MINER_PROCESS_AMOUNT)
    while True:
        client_socket, _ = server_socket.accept()
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
