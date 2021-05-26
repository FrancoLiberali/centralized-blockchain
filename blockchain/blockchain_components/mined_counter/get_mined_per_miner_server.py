from concurrent.futures import ProcessPoolExecutor
import json
import logging

from blockchain_components.mined_counter.common import read_list_from_miner_file, \
    mined_per_miner_locks
from common.common import ALL_MINERS, \
    MINED_COUNTER_PORT, \
    MINED_PER_MINER_SIZE_LEN_IN_BYTES, \
    MINERS_IDS, \
    MINER_ID_LEN_IN_BYTES
from common.responses import respond_ok
from common.safe_tcp_socket import SafeTCPSocket

GET_MINED_PER_MINER_PROCESS_AMOUNT = 2  # TODO envvar

logger = logging.getLogger(name="Mined counter - Get mined per miner")


def get_mined_per_miner(client_socket, client_address):
    miner_id = client_socket.recv_int(MINER_ID_LEN_IN_BYTES)
    if (miner_id == ALL_MINERS):
        logger.info(
            f"Received request of blocks mined by all miners from client {client_address}")
        to_be_sended = {}
        for miner_id in MINERS_IDS:
            with mined_per_miner_locks[miner_id]:
                to_be_sended[miner_id] = read_list_from_miner_file(
                    miner_id)
    else:
        logger.info(
            f"Received request of blocks mined by Miner {miner_id} from client {client_address}")
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
    logger.info(f"Replied blocks mined to client {client_address}")

def proccess_pool_init(locks):
    global mined_per_miner_locks
    mined_per_miner_locks = locks

def get_mined_per_miner_server():
    server_socket = SafeTCPSocket.newServer(MINED_COUNTER_PORT)
    process_pool = ProcessPoolExecutor(
        initializer=proccess_pool_init,
        initargs=(mined_per_miner_locks,),
        max_workers=GET_MINED_PER_MINER_PROCESS_AMOUNT
    )
    while True:
        client_socket, client_address = server_socket.accept()
        # TODO
        # enqueued = process_pool._work_queue.qsize()
        # if enqueued > MAX_ENQUEUED_READS:
        # respond_service_unavaliable(client_socket)
        # continue
        process_pool.submit(get_mined_per_miner, client_socket, client_address)
