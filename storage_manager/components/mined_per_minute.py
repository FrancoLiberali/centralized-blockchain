from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import logging

from common.block_interface import send_hash_and_block_json
from common.constants import DATE_SIZE_LEN_IN_BYTES, \
    DATE_STRING_FORMAT, \
    HASH_LIST_SIZE_LEN_IN_BYTES
from common.responses import respond_not_found, respond_ok, respond_service_unavaliable
from common.safe_tcp_socket import SafeTCPSocket
from components.common import get_day_string, \
    get_minutes_index_path, \
    minutes_indexs_locks_lock, \
    minutes_indexs_locks, \
    read_from_json, \
    read_block

logger = logging.getLogger(name="Storage manager - Mined per minute")

def recv_minute(sock):
    date_string = sock.recv_string_with_len_prepended(DATE_SIZE_LEN_IN_BYTES)
    return datetime.strptime(date_string, DATE_STRING_FORMAT)


def respond_mined_that_minute(client_socket, hash_list):
    # TODO aca seguro que no imprime las excepciones
    respond_ok(client_socket, close_socket=False)
    client_socket.send_int(len(hash_list),
                           HASH_LIST_SIZE_LEN_IN_BYTES)
    for block_hash in hash_list:
        # TODO se puede mejorar, mas de uno podria tener el mismo prefijo
        block_json = read_block(logger, block_hash)
        send_hash_and_block_json(
            client_socket,
            int(block_hash, 16),
            block_json
        )
    client_socket.close()

def get_mined_per_minute(client_socket, client_address):
    minute = recv_minute(client_socket)
    logger.info(
        f"Received request of blocks mined in {minute} from client {client_address}")
    day_string = get_day_string(minute)
    minutes_index_file_path = get_minutes_index_path(day_string)

    try:
        with minutes_indexs_locks_lock:
            lock = minutes_indexs_locks[day_string]
        minutes_index = read_from_json(lock, minutes_index_file_path)
        mined_that_minute = minutes_index[repr(minute.timestamp())]
        respond_mined_that_minute(client_socket, mined_that_minute)
        logger.info(
            f"Blocks mined in {minute} sended to client {client_address}")
    except (KeyError, FileNotFoundError) as e:
        logger.info(f"Blocks mined in {minute} not found")
        respond_not_found(client_socket)


def mined_per_minute_server(port, process_amount):
    process_pool = ProcessPoolExecutor(process_amount)
    server_socket = SafeTCPSocket.newServer(port)
    while True:
        client_socket, client_address = server_socket.accept()
        process_pool.submit(
            get_mined_per_minute,
            client_socket,
            client_address
        )
