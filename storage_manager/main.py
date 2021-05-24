from concurrent.futures import ThreadPoolExecutor
from logging import Logger
import multiprocessing
from pathlib import Path
from threading import Lock, Thread
from datetime import datetime
import json
import time

import sys
sys.path.append("..")

from common.block_interface import send_hash_and_block_json, recv_hash_and_block_json, recv_hash
from common.common import STORAGE_MANAGER_WRITE_PORT, \
    STORAGE_MANAGER_READ_PORT, \
    STORAGE_MANAGER_MINED_PER_MINUTE_PORT, \
    DATE_SIZE_LEN_IN_BYTES, \
    DATE_STRING_FORMAT, \
    HASH_LIST_SIZE_LEN_IN_BYTES
from common.responses import respond_not_found, respond_ok, respond_service_unavaliable
from common.safe_tcp_socket import SafeTCPSocket
from common.logger import Logger, initialize_log


# i have choosen to use threads because it is allmost all i/o,
# so paralelism between instructions is not needed,
# and multithreading if ligther than multiprocessing
READ_THREADS_AMOUNT = 64
MAX_ENQUEUED_READS = 512
MINED_PER_MINUTE_THREADS_AMOUNT = 64
MAX_ENQUEUED_GET_MINED = 512

# TODO DUDA no es la solucion mas eficiente, lectores entre ellos pueden leer a la vez (problema de lector - consumidor)
day_indexs_locks = {}
logger = Logger("Storage manager") # TODO se podria mejorar para que cada parte diga cual es

def write_block(block_hash, block_json):
    logger.info(f"Received request to write block with hash {hex(block_hash)}")
    # TODO DUDA responder un ok? No es neceserio, pero consultar en foro si quiero  
    with open(f"./blockchain_files/{hex(block_hash)}.json", "x") as block_file:
        block_file.write(block_json)

    block_dict = json.loads(block_json)
    # TODO poner en variable global
    mined_in = datetime.fromtimestamp(block_dict['header']['timestamp'])
    minute = mined_in.replace(second=0, microsecond=0)
    day_string = minute.replace(hour=0, minute=0).strftime('%Y-%m-%d')
    day_index_file_path = f"./blockchain_files/minutes_index/{day_string}.json"

    lock = day_indexs_locks.get(day_string, None)
    if not lock:
        lock = Lock()
        day_indexs_locks[day_string] = lock

    with lock:
        try:
            with open(day_index_file_path, "r") as index_file:
                day_index = json.load(index_file)
        except FileNotFoundError:
            day_index = {}

        minute_key = repr(minute.timestamp())
        mined_that_minute = day_index.get(minute_key, [])
        mined_that_minute.append(hex(block_hash))
        day_index[minute_key] = mined_that_minute

        with open(day_index_file_path, "w") as index_file:
            json.dump(day_index, index_file, sort_keys=True, indent=4)
    logger.info(f"Writed block with hash {hex(block_hash)}")


def writer_server():
    Path("./blockchain_files/minutes_index").mkdir(parents=True, exist_ok=True)

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
    day_index_file_path = f"./blockchain_files/minutes_index/{day_string}.json"

    lock = day_indexs_locks.get(day_string, None)
    if not lock:
        respond_not_found(client_socket)

    with lock:
        try:
            with open(day_index_file_path, "r") as index_file:
                day_index = json.load(index_file)
                mined_that_minute = day_index.get(repr(minute.timestamp()), None)
                if not mined_that_minute:
                    respond_not_found(client_socket)
                else:
                    respond_mined_that_minute(client_socket, mined_that_minute)
                    logger.info(f"Blocks mined in {minute} sended to client {client_address}")
        except FileNotFoundError:
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

def read_block(block_hash):
    try:
        with open(f"./blockchain_files/{block_hash}.json", "r") as block_file:
            return block_file.read()
    except FileNotFoundError as e:
        logger.info(f"Block {block_hash} not found")
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
    except FileNotFoundError:
        logger.info(f"Block {hex(block_hash)} not found")
        respond_not_found(client_socket)

def main():
    initialize_log()
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
