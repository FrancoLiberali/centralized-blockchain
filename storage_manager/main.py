from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock, Thread
from datetime import datetime
import json

import sys
sys.path.append("..")

from common.common import STORAGE_MANAGER_WRITE_PORT, \
    STORAGE_MANAGER_READ_PORT, \
    STORAGE_MANAGER_MINED_PER_MINUTE_PORT, \
    DATE_SIZE_LEN_IN_BYTES, \
    DATE_STRING_FORMAT, \
    HASH_LIST_SIZE_LEN_IN_BYTES
from common.responses import respond_not_found, respond_ok
from common.safe_tcp_socket import SafeTCPSocket
from common.block_interface import send_hash_and_block_json, recv_hash_and_block_json, recv_hash

# TODO DUDA no es la solucion mas eficiente, lectores entre ellos pueden leer a la vez (problema de lector - consumidor)
day_indexs_locks = {}

def write_block(block_hash, block_json):
    # TODO DUDA responder un ok?
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

def writer_server():
    Path("./blockchain_files/minutes_index").mkdir(parents=True, exist_ok=True)

    # TODO DUDA al parar el container quiere excribir el block 0x0.json y vacio, no se porque. Hay que hacer un gracefully quit?
    serversocket = SafeTCPSocket.newServer(STORAGE_MANAGER_WRITE_PORT)
    block_appender_socket = serversocket.accept()
    while True:
        block_hash, block = recv_hash_and_block_json(block_appender_socket)
        write_block(block_hash, block)

def read_block(client_socket):
    block_hash = recv_hash(client_socket)
    try:
        with open(f"./blockchain_files/{hex(block_hash)}.json", "r") as block_file:
            respond_ok(client_socket, close_socket=False)
            send_hash_and_block_json(
                client_socket,
                block_hash,
                block_file.read()
            )
            client_socket.close()
    except FileNotFoundError:
        respond_not_found(client_socket)

# i have choosen to use threads because it is allmost all i/o,
# so paralelism between instructions is not needed,
# and multithreading if ligther than multiprocessing
READ_THREADS_AMOUNT = 64
MINED_PER_MINUTE_THREADS_AMOUNT = 64

def recv_minute(sock):
    date_size = sock.recv_int(DATE_SIZE_LEN_IN_BYTES)
    date_string = sock.recv(date_size).decode('utf-8')
    return datetime.strptime(date_string, DATE_STRING_FORMAT)

def respond_mined_that_minute(sock, hash_list):
    respond_ok(sock, close_socket=False)
    hash_list_json = json.dumps(hash_list, indent=4)
    sock.send_int(
        len(hash_list_json),
        HASH_LIST_SIZE_LEN_IN_BYTES
    )
    sock.send(hash_list_json.encode('utf-8'))

def get_mined_per_minute(client_socket):
    # TODO enviar por mail a los ayudantes por privado: guidosergio12@gmail.com, ezequiel.torresfeyuk@gmail.com, czarniana@gmail.com>,cerana@fi.uba.ar, pablodroca@gmail.com
    minute = recv_minute(client_socket)
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
        except FileNotFoundError:
            respond_not_found(client_socket)

def mined_per_minute_server():
    # TODO pasar a process pool, porque acá si hay procesamiento al levantar json's
    thread_pool = ThreadPoolExecutor(MINED_PER_MINUTE_THREADS_AMOUNT)
    server_socket = SafeTCPSocket.newServer(STORAGE_MANAGER_MINED_PER_MINUTE_PORT)
    while True:
        client_socket = server_socket.accept()
        # TODO DUDA ver si esto tiene un timeout o algo asi que pasa si se llena esa cola
        thread_pool.submit(get_mined_per_minute, (client_socket))

def main():
    writers_t = Thread(target=writer_server)
    writers_t.start()

    mined_per_minute_t = Thread(target=mined_per_minute_server)
    mined_per_minute_t.start()

    read_thread_pool = ThreadPoolExecutor(READ_THREADS_AMOUNT)

    server_socket = SafeTCPSocket.newServer(STORAGE_MANAGER_READ_PORT)
    while True:
        client_socket = server_socket.accept()
        # TODO DUDA ver si esto tiene un timeout o algo asi que pasa si se llena esa cola
        read_thread_pool.submit(read_block, (client_socket))

if __name__ == '__main__':
    main()
