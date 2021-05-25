from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from logging import Logger
from pathlib import Path
from threading import Lock, Thread

from common.block_interface import send_hash_and_block_json, recv_hash_and_block_json, recv_hash
from common.common import STORAGE_MANAGER_WRITE_PORT, \
    STORAGE_MANAGER_READ_PORT, \
    STORAGE_MANAGER_MINED_PER_MINUTE_PORT, \
    DATE_SIZE_LEN_IN_BYTES, \
    DATE_STRING_FORMAT, \
    HASH_LIST_SIZE_LEN_IN_BYTES
from common.logger import Logger, initialize_log
from common.responses import respond_not_found, respond_ok, respond_service_unavaliable
from common.safe_tcp_socket import SafeTCPSocket


# i have choosen to use threads because it is allmost all i/o,
# so paralelism between instructions is not needed,
# and multithreading if ligther than multiprocessing
READ_THREADS_AMOUNT = 64
MAX_ENQUEUED_READS = 512
MINED_PER_MINUTE_THREADS_AMOUNT = 64
MAX_ENQUEUED_GET_MINED = 512

BLOCKCHAIN_FILES_PATH = "/storage_manager/blockchain_files"
MINUTES_INDEX_PATH = f"{BLOCKCHAIN_FILES_PATH}/minutes_index"

# TODO DUDA no es la solucion mas eficiente, lectores entre ellos pueden leer a la vez (problema de lector - consumidor)
minutes_indexs_locks = {}
hash_prefix_locks = {}
logger = Logger("Storage manager") # TODO se podria mejorar para que cada parte diga cual es

def get_blocks_by_prefix_path(prefix):
    return f"{BLOCKCHAIN_FILES_PATH}/{prefix}.json"

def get_minutes_index_path(day):
    return f"{MINUTES_INDEX_PATH}/{day}.json"

def get_block_hash_prefix(block_hash_hex):
    return block_hash_hex[2:7]

def append_to_json(locks_dict, locks_key, file_path, append_function):
    # TODO aca falta un lock? Mas de uno puede estar haciendo esto a la vez?
    lock = locks_dict.get(locks_key, None)
    if not lock:
        lock = Lock()
        locks_dict[locks_key] = lock

    with lock:
        try:
            with open(file_path, "r") as json_file:
                json_dict = json.load(json_file)
        except FileNotFoundError:
            json_dict = {}

        append_function(json_dict)
        with open(file_path, "w") as json_file:
            json.dump(json_dict, json_file, indent=4)


def append_block_to_blocks_by_prefix(block_hash_hex, block_json):
    # function currying in python
    def append_func(blocks_dict):
        blocks_dict[block_hash_hex] = block_json
    return append_func


def append_block_hash_to_minutes_index(minute, block_hash_hex):
    minute_key = repr(minute.timestamp())
    # function currying in python
    def append_func(minutes_index):
        mined_that_minute = minutes_index.get(minute_key, [])
        mined_that_minute.append(block_hash_hex)
        minutes_index[minute_key] = mined_that_minute
    return append_func

def write_block(block_hash, block_json):
    block_hash_hex = hex(block_hash)
    logger.info(f"Received request to write block with hash {block_hash_hex}")

    prefix = get_block_hash_prefix(block_hash_hex)
    blocks_by_prefix_path = get_blocks_by_prefix_path(prefix)
    # TODO DUDA responder un ok? No es neceserio, pero consultar en foro si quiero
    append_to_json(
        hash_prefix_locks,
        prefix,
        blocks_by_prefix_path,
        append_block_to_blocks_by_prefix(
            block_hash_hex, block_json
        )
    )

    block_dict = json.loads(block_json)
    # TODO poner en variable global
    mined_in = datetime.fromtimestamp(block_dict['header']['timestamp'])
    minute = mined_in.replace(second=0, microsecond=0)
    day_string = minute.replace(hour=0, minute=0).strftime('%Y-%m-%d')
    minutes_index_file_path = get_minutes_index_path(day_string)
    append_to_json(
        minutes_indexs_locks,
        day_string,
        minutes_index_file_path,
        append_block_hash_to_minutes_index(
            minute, block_hash_hex
        )
    )
    logger.info(f"Writed block with hash {block_hash_hex} in {prefix}.json")


def writer_server():
    # TODO DUDA al parar el container quiere excribir el block 0x0.json y vacio, no se porque. Hay que hacer un gracefully quit?
    serversocket = SafeTCPSocket.newServer(STORAGE_MANAGER_WRITE_PORT)
    block_appender_socket, _ = serversocket.accept()
    while True:
        block_hash, block = recv_hash_and_block_json(block_appender_socket)
        write_block(block_hash, block)

def recv_minute(sock):
    date_string = sock.recv_string_with_len_prepended(DATE_SIZE_LEN_IN_BYTES)
    return datetime.strptime(date_string, DATE_STRING_FORMAT)

def respond_mined_that_minute(client_socket, hash_list):
    # TODO aca seguro que no imprime las excepciones
    respond_ok(client_socket, close_socket=False)
    client_socket.send_int(len(hash_list),
                           HASH_LIST_SIZE_LEN_IN_BYTES)
    for block_hash in hash_list:
        block_json = read_block(block_hash)
        send_hash_and_block_json(
            client_socket,
            int(block_hash, 16),
            block_json
        )
    client_socket.close()

def get_mined_per_minute(client_socket, client_address):
    minute = recv_minute(client_socket)
    logger.info(f"Received request of blocks mined in {minute} from client {client_address}")
    # TODO codigo repetido con la escritura del indice
    day_string = minute.replace(hour=0, minute=0).strftime('%Y-%m-%d')
    minutes_index_file_path = get_minutes_index_path(day_string)

    try:
        lock = minutes_indexs_locks[day_string]
        minutes_index = read_from_json(lock, minutes_index_file_path)
        mined_that_minute = minutes_index[repr(minute.timestamp())]
        respond_mined_that_minute(client_socket, mined_that_minute)
        logger.info(f"Blocks mined in {minute} sended to client {client_address}")
    except (KeyError, FileNotFoundError) as e:
        logger.info(f"Blocks mined in {minute} not found")
        respond_not_found(client_socket)

def mined_per_minute_server():
    # TODO pasar a process pool, porque acá si hay procesamiento al levantar json's
    thread_pool = ThreadPoolExecutor(MINED_PER_MINUTE_THREADS_AMOUNT)
    server_socket = SafeTCPSocket.newServer(STORAGE_MANAGER_MINED_PER_MINUTE_PORT)
    while True:
        client_socket, client_address = server_socket.accept()
        enqueued = thread_pool._work_queue.qsize()
        if enqueued > MAX_ENQUEUED_GET_MINED:
            respond_service_unavaliable(client_socket)
            continue
        thread_pool.submit(
            get_mined_per_minute,
            client_socket,
            client_address
        )

def read_from_json(lock, json_file_path):
    with lock:
        with open(json_file_path, "r") as json_file:
            return json.load(json_file)

def read_block(block_hash_hex):
    prefix = get_block_hash_prefix(block_hash_hex)
    block_with_prefix_path = get_blocks_by_prefix_path(prefix)

    try:
        lock = hash_prefix_locks[prefix]
        blocks_dict = read_from_json(lock, block_with_prefix_path)
        return blocks_dict[block_hash_hex]
    except (KeyError, FileNotFoundError) as e:
        logger.info(f"Block {block_hash_hex} not found")
        raise e

def reply_block(client_socket, client_address):
    # TODO la carga maxima de esto creo que está buggeada, me saltaba error
    block_hash = recv_hash(client_socket)
    logger.info(f"Received request of block {hex(block_hash)} from client {client_address}")
    try:
        block_json = read_block(hex(block_hash))
        respond_ok(client_socket, close_socket=False)
        send_hash_and_block_json(
            client_socket,
            block_hash,
            block_json
        )
        logger.info(
            f"Block {hex(block_hash)} sended to client {client_address}")
        client_socket.close()
    except (KeyError, FileNotFoundError):
        respond_not_found(client_socket)

def main():
    initialize_log()

    Path(MINUTES_INDEX_PATH).mkdir(parents=True, exist_ok=True)

    writers_t = Thread(target=writer_server)
    writers_t.start()

    mined_per_minute_t = Thread(target=mined_per_minute_server)
    mined_per_minute_t.start()

    read_thread_pool = ThreadPoolExecutor(READ_THREADS_AMOUNT)

    server_socket = SafeTCPSocket.newServer(STORAGE_MANAGER_READ_PORT)
    while True:
        client_socket, client_address = server_socket.accept()
        enqueued = read_thread_pool._work_queue.qsize()
        if enqueued > MAX_ENQUEUED_READS:
            respond_service_unavaliable(client_socket)
            continue
        read_thread_pool.submit(reply_block, client_socket, client_address)

if __name__ == '__main__':
    main()
