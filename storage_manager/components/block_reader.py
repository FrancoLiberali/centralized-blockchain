from concurrent.futures import ThreadPoolExecutor

from common.block_interface import send_hash_and_block_json, recv_hash
from common.common import STORAGE_MANAGER_READ_PORT
from common.logger import Logger
from common.responses import respond_not_found, respond_ok, respond_service_unavaliable
from common.safe_tcp_socket import SafeTCPSocket
from components.common import read_block

# i have choosen to use threads because it is allmost all i/o,
# so paralelism between instructions is not needed,
# and multithreading if ligther than multiprocessing
READ_THREADS_AMOUNT = 64
MAX_ENQUEUED_READS = 512

logger = Logger("Storage manager - Block reader")

def reply_block(client_socket, client_address):
    # TODO la carga maxima de esto creo que está buggeada, me saltaba error
    block_hash = recv_hash(client_socket)
    logger.info(
        f"Received request of block {hex(block_hash)} from client {client_address}")
    try:
        block_json = read_block(logger, hex(block_hash))
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


def reader_server():
    read_thread_pool = ThreadPoolExecutor(READ_THREADS_AMOUNT)

    server_socket = SafeTCPSocket.newServer(STORAGE_MANAGER_READ_PORT)
    while True:
        client_socket, client_address = server_socket.accept()
        enqueued = read_thread_pool._work_queue.qsize()
        if enqueued > MAX_ENQUEUED_READS:
            respond_service_unavaliable(client_socket)
            continue
        read_thread_pool.submit(reply_block, client_socket, client_address)
