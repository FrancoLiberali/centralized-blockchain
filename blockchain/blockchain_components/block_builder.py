import datetime
import threading
import time
from common.common import Block, \
    BLOCK_BUILDER_PORT, \
    CHUNK_SIZE_LEN_IN_BYTES,\
    MAX_ENTRIES_AMOUNT, \
    MAX_ENTRY_SIZE_IN_BYTES
from common.safe_tcp_socket import SafeTCPSocket
from common.responses import respond_bad_request, respond_ok, respond_service_unavaliable
from common.logger import Logger

BLOCK_BUILD_LIMIT_IN_SECONDS = 12

logger = Logger("Block builder")
lock = threading.Lock()
chunks = []
start_time = datetime.datetime.now()

def main(miners_coordinator_queue):
    serversocket = SafeTCPSocket.newServer(BLOCK_BUILDER_PORT)
    lauch_thread_to_verify_elapsed_time(miners_coordinator_queue)

    while True:
        clientsocket, client_adress = serversocket.accept()
        if not miners_coordinator_queue.full():
            chunk_size = clientsocket.recv_int(CHUNK_SIZE_LEN_IN_BYTES)
            if chunk_size > MAX_ENTRY_SIZE_IN_BYTES:
                respond_bad_request(clientsocket) # TODO aclarar

            chunk = clientsocket.recv_string(chunk_size)
            logger.info(f"Received chuck from client {client_adress}: {chunk}")

            with lock:
                chunks.append(chunk)
                if len(chunks) == MAX_ENTRIES_AMOUNT or get_elapsed_time_is_bigger_than_limit():
                    send_chunks_to_be_mined(miners_coordinator_queue)

            respond_ok(clientsocket)
        else:
            respond_service_unavaliable(clientsocket)

def get_elapsed_time_is_bigger_than_limit():
    now = datetime.datetime.now()
    elapsed_time = (now - start_time).total_seconds()
    return elapsed_time >= BLOCK_BUILD_LIMIT_IN_SECONDS

def lauch_thread_to_verify_elapsed_time(miners_coordinator_queue):
    elapsed_time_verifier = threading.Thread(
        target=verify_elapsed_time, args=((miners_coordinator_queue),))
    elapsed_time_verifier.start()

def verify_elapsed_time(miners_coordinator_queue):
    time.sleep(BLOCK_BUILD_LIMIT_IN_SECONDS)
    with lock:
        # not get_elapsed_time_is_bigger_than_limit means that MAX_ENTRIES_AMOUNT has been reached
        # while sleep and this verifier is deprecated
        if get_elapsed_time_is_bigger_than_limit() and len(chunks) > 0:
            logger.info(
                f"Time limit to build block passed, building block"
            )
            send_chunks_to_be_mined(miners_coordinator_queue)

def send_chunks_to_be_mined(miners_coordinator_queue):
    global chunks
    global start_time
    block = Block(chunks)
    logger.info(
        f"Block appended to Miner's coordinator queue: {block}"
    )
    miners_coordinator_queue.put(block)
    chunks = []
    start_time = datetime.datetime.now()
    lauch_thread_to_verify_elapsed_time(miners_coordinator_queue)