from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Thread

import sys
sys.path.append("..")

from common.common import STORAGE_MANAGER_WRITE_PORT, STORAGE_MANAGER_READ_PORT
from common.responses import respond_not_found, respond_ok
from common.safe_tcp_socket import SafeTCPSocket
from common.block_interface import send_hash_and_block_json, recv_hash_and_block_json, recv_hash

def write_block(block_hash, block):
    # TODO responder un ok?
    with open(f"./blockchain_files/{hex(block_hash)}.json", "x") as block_file:
        block_file.write(block)

def writer_server():
    Path("./blockchain_files").mkdir(parents=True, exist_ok=True)

    # TODO al parar el container quiere excribir el block 0x0.json y vacio, no se porque
    serversocket = SafeTCPSocket.newServer(STORAGE_MANAGER_WRITE_PORT)
    block_appender_socket = serversocket.accept()
    while True:
        block_hash, block = recv_hash_and_block_json(block_appender_socket)

        print(block_hash)
        print(block)
        # i have choosen to use threads because it is allmost all i/o,
        # so paralelism between instructions is not needed,
        # and multithreading if ligther than multiprocessing
        # TODO thread pool
        writer_t = Thread(target=write_block, args=((block_hash), (block),))
        writer_t.start()

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

READ_THREADS_AMOUNT = 512 # TODO tener en cuenta que el socket tambien es un fd abierto

def main():
    writers_t = Thread(target=writer_server)
    writers_t.start()

    read_thread_pool = ThreadPoolExecutor(READ_THREADS_AMOUNT)

    server_socket = SafeTCPSocket.newServer(STORAGE_MANAGER_READ_PORT)
    while True:
        client_socket = server_socket.accept()
        # TODO ver si esto tiene un timeout o algo asi que pasa si se llena esa cola
        read_thread_pool.submit(read_block, (client_socket))

if __name__ == '__main__':
    main()
