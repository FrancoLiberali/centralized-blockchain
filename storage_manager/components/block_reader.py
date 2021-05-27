from concurrent.futures import ProcessPoolExecutor
import logging

from communications.block_interface import send_hash_and_block_json, recv_hash
from communications.responses import respond_internal_server_error, respond_not_found, respond_ok
from communications.safe_tcp_socket import SafeTCPSocket
from components.common import read_block

logger = logging.getLogger(name="Storage manager - Block reader")

def reply_block(client_socket, client_address):
    try:
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
    except Exception as e:
        logger.critical(
            f"An error ocurred while getting block: {e}")
        respond_internal_server_error(client_socket)


def reader_server(port, process_amount):
    read_process_pool = ProcessPoolExecutor(process_amount)

    server_socket = SafeTCPSocket.newServer(port)
    while True:
        client_socket, client_address = server_socket.accept()
        read_process_pool.submit(reply_block, client_socket, client_address)
