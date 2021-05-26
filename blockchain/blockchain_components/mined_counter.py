from common.logger import Logger
from concurrent.futures import ProcessPoolExecutor
import json
from multiprocessing import Lock, Process
from pathlib import Path

from common.common import ADD_SUCCESSFUL_MINING_OP, \
    ADD_WRONG_MINING_OP, \
    ALL_MINERS, \
    BLOCK_APPENDER_PORT, \
    MINED_PER_MINER_SIZE_LEN_IN_BYTES, \
    MINERS_IDS, \
    MINER_ID_LEN_IN_BYTES, \
    SUCESSFULL_INDEX, \
    WRONG_INDEX
from common.responses import respond_ok
from common.safe_tcp_socket import SafeTCPSocket

GET_MINED_PER_MINER_PROCESS_AMOUNT = 2  # TODO envvar
MINED_PER_MINER_PATH = "/blockchain/blockchain_components/mined_counter/mined_per_miner_files"

mined_per_miner_locks = {} # TODO que no pida sudo el docker down
# TODO no es lo mas eficiente, lectores-escritores
logger = Logger("Mined counter - Add mining")

def main(block_appender_queue):
    initialize_mined_per_miner_files_and_locks()
    get_mined_per_miner_server_p = Process(
        target=get_mined_per_miner_server
    )
    get_mined_per_miner_server_p.start()
    add_mining_server(block_appender_queue)


def get_mined_by_miner_path(miner_id):
    return f"{MINED_PER_MINER_PATH}/{miner_id}.json"

def write_list_to_miner_file(miner_id, list):
    with open(get_mined_by_miner_path(miner_id), "w+") as miner_file:
        json.dump(list, miner_file)

def read_list_from_miner_file(miner_id):
    with open(get_mined_by_miner_path(miner_id), "r") as miner_file:
        return json.load(miner_file)


def initialize_mined_per_miner_files_and_locks():
    Path(MINED_PER_MINER_PATH).mkdir(parents=True, exist_ok=True)
    for miner_id in MINERS_IDS:
        mined_per_miner_locks[miner_id] = Lock()
        write_list_to_miner_file(miner_id, [0, 0])

def add_successful_mining(miner_id):
    add_mining(miner_id, SUCESSFULL_INDEX) # TODO fix typo

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


def proccess_pool_init(locks):
    global mined_per_miner_locks
    mined_per_miner_locks = locks

# TODO modularizar
def get_mined_per_miner_server():
    server_socket = SafeTCPSocket.newServer(BLOCK_APPENDER_PORT)
    process_pool = ProcessPoolExecutor(
        initializer=proccess_pool_init,
        initargs=(mined_per_miner_locks,),
        max_workers=GET_MINED_PER_MINER_PROCESS_AMOUNT
    )
    while True:
        client_socket, _ = server_socket.accept()
        # TODO
        # enqueued = process_pool._work_queue.qsize()
        # if enqueued > MAX_ENQUEUED_READS:
        # respond_service_unavaliable(client_socket)
        # continue
        process_pool.submit(get_mined_per_miner, client_socket)

def get_mined_per_miner(client_socket):
    try:
        miner_id = client_socket.recv_int(MINER_ID_LEN_IN_BYTES)
        if (miner_id == ALL_MINERS):
            to_be_sended = {}
            for miner_id in MINERS_IDS:
                with mined_per_miner_locks[miner_id]:
                    to_be_sended[miner_id] = read_list_from_miner_file(miner_id)
        else:
            with mined_per_miner_locks[miner_id]:
                to_be_sended = read_list_from_miner_file(miner_id)
        to_be_sended_json = json.dumps(
            to_be_sended,
            indent=4,
            sort_keys=False
        )
        respond_ok(client_socket, close_socket=False)
        client_socket.send_string_with_len_prepended(
            to_be_sended_json,
            MINED_PER_MINER_SIZE_LEN_IN_BYTES
        )
        client_socket.close()
    except Exception as e:
        print(e)
